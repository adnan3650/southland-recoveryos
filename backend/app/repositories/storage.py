"""Ownership is enforced in the repository as well as the service boundary."""

import json
import sqlite3
from pathlib import Path
from typing import Protocol

from fastapi import HTTPException


class CaseRepository(Protocol):
    def list(self, owner: str) -> list[dict]: ...
    def get(self, case_id: str, owner: str) -> dict: ...
    def save(self, case: dict, owner: str) -> None: ...


class BlobStore(Protocol):
    def put(self, key: str, content: bytes, media_type: str) -> None: ...
    def read(self, key: str) -> bytes: ...


class SQLiteRepository:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, owner TEXT NOT NULL, body TEXT NOT NULL)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS cases_owner ON cases(owner)")
        path.chmod(0o600)

    def connect(self):
        return sqlite3.connect(self.path, timeout=20)

    def list(self, owner):
        with self.connect() as db:
            rows = db.execute("SELECT body FROM cases WHERE owner=? ORDER BY rowid DESC", (owner,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def get(self, case_id, owner):
        with self.connect() as db:
            row = db.execute("SELECT body FROM cases WHERE id=? AND owner=?", (case_id, owner)).fetchone()
        if not row:
            raise HTTPException(404, "Case not found")
        return json.loads(row[0])

    def save(self, case, owner):
        body = json.dumps(case)
        if len(body.encode()) > 350000:
            raise HTTPException(413, "Case storage limit reached; start another synthetic case")
        with self.connect() as db:
            existing = db.execute("SELECT owner FROM cases WHERE id=?", (case["id"],)).fetchone()
            if existing and existing[0] != owner:
                raise HTTPException(404, "Case not found")
            db.execute(
                "INSERT INTO cases VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body",
                (case["id"], owner, body),
            )


class LocalBlobStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        root.chmod(0o700)

    def path(self, key):
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise HTTPException(400, "Invalid storage key")
        return path

    def put(self, key, content, media_type):
        path = self.path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.chmod(0o600)

    def read(self, key):
        return self.path(key).read_bytes()


class DynamoRepository:
    """Prepared AWS adapter; integration testing requires approved resources."""

    def __init__(self, table):
        self.table = table

    def list(self, owner):
        from boto3.dynamodb.conditions import Key

        result = self.table.query(KeyConditionExpression=Key("owner").eq(owner))
        rows = result["Items"]
        while "LastEvaluatedKey" in result:
            result = self.table.query(
                KeyConditionExpression=Key("owner").eq(owner), ExclusiveStartKey=result["LastEvaluatedKey"]
            )
            rows.extend(result["Items"])
        return [json.loads(row["body"]) for row in rows]

    def get(self, case_id, owner):
        result = self.table.get_item(Key={"owner": owner, "id": case_id}, ConsistentRead=True)
        if "Item" not in result:
            raise HTTPException(404, "Case not found")
        return json.loads(result["Item"]["body"])

    def save(self, case, owner):
        body = json.dumps(case)
        if len(body.encode()) > 350000:
            raise HTTPException(413, "Case storage limit reached")
        self.table.put_item(Item={"owner": owner, "id": case["id"], "body": body})


class S3BlobStore:
    def __init__(self, client, bucket):
        self.client, self.bucket = client, bucket

    def put(self, key, content, media_type):
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=content, ContentType=media_type, ServerSideEncryption="AES256"
        )

    def read(self, key):
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
