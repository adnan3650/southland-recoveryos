import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .models import CaseInput, ChatInput, Consent, ContactInput, DamageInput, InsuranceInput, TaskInput, TaskPatch
from .repositories.storage import DynamoRepository, LocalBlobStore, S3BlobStore, SQLiteRepository
from .security import owner
from .services.ai import AIAnalysisService
from .services.cases import CaseService, now
from .services.checklist import checklist_docx, checklist_lines
from .services.documents import MAX_UPLOAD, DocumentService
from .services.reports import ReportService
from .services.resources import ResourceService
from .services.rules import match_programs, prioritized_plan, readiness

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def create_app(data_dir=None):
    mode = os.getenv("APP_MODE", "local")
    if mode not in {"local", "aws"}:
        raise RuntimeError("Unsupported APP_MODE")
    if mode == "aws":
        import boto3

        repo = DynamoRepository(boto3.resource("dynamodb").Table(os.environ["CASES_TABLE"]))
        blobs = S3BlobStore(boto3.client("s3"), os.environ["DOCUMENTS_BUCKET"])
    else:
        runtime = Path(data_dir or os.getenv("DATA_DIR", ROOT / "runtime"))
        repo, blobs = SQLiteRepository(runtime / "cases.sqlite3"), LocalBlobStore(runtime / "documents")
    cases = CaseService(repo)
    resources = ResourceService(ROOT / "data/resources.json")
    documents, ai = DocumentService(blobs), AIAnalysisService(blobs)
    locks = {}  # single local worker; production requires optimistic concurrency (documented gap)

    @asynccontextmanager
    async def lifespan(app):
        yield

    app = FastAPI(title="Southland RecoveryOS", version="0.1.0", lifespan=lifespan)
    app.state.ai = ai
    app.state.repo = repo
    if mode == "aws":
        from jwt import PyJWKClient

        app.state.jwks = PyJWKClient(os.environ["COGNITO_ISSUER"] + "/.well-known/jwks.json")
    else:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])

    @app.middleware("http")
    async def boundaries(request: Request, call_next):
        started = time.monotonic()
        if mode == "local" and request.client and request.client.host not in {"127.0.0.1", "::1", "testclient"}:
            return JSONResponse(
                {"error": {"message": "Local synthetic mode accepts loopback clients only"}}, status_code=403
            )
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            allowed = {f"http://{host}:{port}" for host in ["localhost", "127.0.0.1"] for port in [5173, 8000]}
            if mode == "aws":
                allowed = {os.environ["FRONTEND_ORIGIN"]}
            if origin and origin not in allowed:
                return JSONResponse({"error": {"message": "Cross-origin writes are not permitted"}}, status_code=403)
            try:
                if int(request.headers.get("content-length", "0")) > MAX_UPLOAD + 1024 * 1024:
                    return JSONResponse({"error": {"message": "Request too large"}}, status_code=413)
            except ValueError:
                return JSONResponse({"error": {"message": "Invalid content length"}}, status_code=400)
        response = await call_next(request)
        response.headers.update(
            {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Cache-Control": "no-store",
                "Content-Security-Policy": "default-src 'self'; img-src 'self' blob: data:; style-src 'self' 'unsafe-inline'; connect-src 'self' ws://127.0.0.1:5173; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self'",
                "Server-Timing": f"app;dur={(time.monotonic() - started) * 1000:.1f}",
            }
        )
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse({"error": {"message": str(exc.detail)}}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Do not echo input values, file bodies or sensitive information.
        return JSONResponse(
            {
                "error": {
                    "message": "Check the form fields and try again",
                    "fields": [{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()],
                }
            },
            status_code=422,
        )

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        return JSONResponse({"error": {"message": "An unexpected error occurred. Please retry."}}, status_code=500)

    def lock(case_id):
        return locks.setdefault(case_id, asyncio.Lock())

    def get_document(case, document_id):
        document = next((d for d in case["documents"] if d["id"] == document_id), None)
        if not document:
            raise HTTPException(404, "Document not found")
        return document

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "mode": mode,
            "ai_configured": ai.configured,
            "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
            "synthetic_only": mode == "local",
        }

    @app.get("/api/cases")
    def list_cases(user=Depends(owner)):
        return [
            {
                "id": c["id"],
                "resident_name": c["resident_name"],
                "municipality": c["municipality"],
                "disaster_type": c["disaster_type"],
                "incident_date": c["incident_date"],
                "updated_at": c["updated_at"],
            }
            for c in repo.list(user)
        ]

    @app.post("/api/cases", status_code=201)
    def create_case(data: CaseInput, user=Depends(owner)):
        return cases.create(data, user)

    @app.get("/api/cases/{case_id}")
    def get_case(case_id: str, user=Depends(owner)):
        return repo.get(case_id, user)

    @app.put("/api/cases/{case_id}")
    async def update_case(case_id: str, data: CaseInput, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            case.update(data.model_dump(mode="json"))
            if (case["displaced"] or case["immediate_needs"]) and not any(
                t["id"] == "essentials" for t in case["tasks"]
            ):
                from .services.rules import initial_tasks

                case["tasks"].append(next(t for t in initial_tasks(case) if t["id"] == "essentials"))
            return cases.save(case, user, "case.updated")

    @app.post("/api/cases/{case_id}/documents", status_code=201)
    async def upload_document(
        case_id: str, file: UploadFile = File(...), category: str = Form(...), user=Depends(owner)
    ):
        if category not in {"damage", "policy", "estimate", "receipt", "identity", "other"}:
            raise HTTPException(422, "Invalid document category")
        async with lock(case_id):
            case = repo.get(case_id, user)
            content = await file.read(MAX_UPLOAD + 1)
            document = documents.upload(case, content, file.filename or "document", category)
            cases.save(case, user, "document.uploaded")
            return document

    @app.get("/api/cases/{case_id}/documents/{document_id}/file")
    def download_document(case_id: str, document_id: str, user=Depends(owner)):
        document = get_document(repo.get(case_id, user), document_id)
        # Text/PDF download-only. Images can be previewed as validated raster content.
        disposition = "inline" if document["media_type"].startswith("image/") else "attachment"
        return Response(
            blobs.read(document["storage_key"]),
            media_type=document["media_type"],
            headers={"Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(document['name'], safe='')}"},
        )

    @app.post("/api/cases/{case_id}/documents/{document_id}/analyze")
    async def analyze_document(case_id: str, document_id: str, data: Consent, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            document = get_document(case, document_id)
            output, usage = await ai.analyze(case, document)
            document["analysis"] = {
                "result": output,
                "usage": usage,
                "provenance": "Claude interpretation - verify original evidence",
            }
            case["analyses"] = [a for a in case["analyses"] if a["document_id"] != document_id]
            case["analyses"].append({"document_id": document_id, "result": output, "usage": usage})
            case["damage_items"] = [d for d in case["damage_items"] if d.get("document_id") != document_id]
            case["damage_items"].extend(
                [
                    {**item, "id": str(uuid4()), "document_id": document_id, "provenance": "AI interpretation"}
                    for item in output["observations"]
                ]
            )
            cases.save(case, user, "document.analyzed")
            return document["analysis"]

    @app.get("/api/cases/{case_id}/damage")
    def inventory(case_id: str, user=Depends(owner)):
        return repo.get(case_id, user)["damage_items"]

    @app.post("/api/cases/{case_id}/damage", status_code=201)
    async def add_damage(case_id: str, data: DamageInput, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            if len(case["damage_items"]) >= 100:
                raise HTTPException(413, "Inventory limit reached")
            item = {
                **data.model_dump(),
                "id": str(uuid4()),
                "provenance": "Resident observation",
                "evidence_ids": [],
                "uncertainty": "Not independently verified",
            }
            case["damage_items"].append(item)
            cases.save(case, user, "damage.recorded")
            return item

    @app.get("/api/resources")
    def search_resources(q: str = "", category: str = "", location: str = ""):
        if len(q) + len(location) > 300:
            raise HTTPException(422, "Search too long")
        return resources.search(q, category, location)

    @app.get("/api/cases/{case_id}/resources")
    def immediate_resources(case_id: str, user=Depends(owner)):
        return resources.immediate(repo.get(case_id, user))

    @app.get("/api/cases/{case_id}/programs")
    def programs(case_id: str, user=Depends(owner)):
        return match_programs(repo.get(case_id, user), resources.resources)

    @app.get("/api/cases/{case_id}/readiness")
    def get_readiness(case_id: str, user=Depends(owner)):
        return readiness(repo.get(case_id, user))

    @app.get("/api/cases/{case_id}/plan")
    def plan(case_id: str, user=Depends(owner)):
        return prioritized_plan(repo.get(case_id, user), resources.resources)

    @app.post("/api/cases/{case_id}/plan/ai")
    async def ai_plan(case_id: str, data: Consent, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            output, usage = await ai.plan(case, resources.resources)
            case["ai_plan"] = {"result": output, "usage": usage}
            cases.save(case, user, "plan.ai_generated")
            return case["ai_plan"]

    @app.post("/api/cases/{case_id}/tasks", status_code=201)
    async def add_task(case_id: str, data: TaskInput, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            if len(case["tasks"]) >= 60:
                raise HTTPException(413, "Task limit reached")
            task = {
                **data.model_dump(mode="json"),
                "id": str(uuid4()),
                "status": "todo",
                "provenance": "Resident-set task",
                "source_id": None,
            }
            case["tasks"].append(task)
            cases.save(case, user, "task.created")
            return task

    @app.patch("/api/cases/{case_id}/tasks/{task_id}")
    async def update_task(case_id: str, task_id: str, data: TaskPatch, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            task = next((t for t in case["tasks"] if t["id"] == task_id), None)
            if not task:
                raise HTTPException(404, "Task not found")
            task.update(data.model_dump())
            cases.save(case, user, "task.updated")
            return task

    @app.put("/api/cases/{case_id}/insurance")
    async def save_insurance(case_id: str, data: InsuranceInput, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            case["insurance"] = data.model_dump()
            cases.save(case, user, "insurance.updated")
            return case["insurance"]

    @app.post("/api/cases/{case_id}/contacts", status_code=201)
    async def add_contact(case_id: str, data: ContactInput, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            if len(case["contacts"]) >= 50:
                raise HTTPException(413, "Contact limit reached")
            contact = {**data.model_dump(mode="json"), "id": str(uuid4())}
            case["contacts"].append(contact)
            cases.save(case, user, "contact.recorded")
            return contact

    @app.post("/api/cases/{case_id}/assistant")
    async def assistant(case_id: str, data: ChatInput, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            output, usage = await ai.ask(case, resources.resources, data.question)
            conversation = {"id": str(uuid4()), "question": data.question, **output, "usage": usage}
            case["conversations"].append(conversation)
            case["conversations"] = case["conversations"][-30:]
            cases.save(case, user, "assistant.responded")
            return conversation

    @app.get("/api/cases/{case_id}/checklist")
    def export_checklist(case_id: str, format: str = "txt", user=Depends(owner)):
        case = repo.get(case_id, user)
        if format not in {"txt", "docx"}:
            raise HTTPException(422, "Choose txt or docx for your checklist")
        lines = checklist_lines(case, resources.resources)
        content = checklist_docx(lines) if format == "docx" else "\n".join(lines).encode("utf-8")
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if format == "docx" else "text/plain; charset=utf-8"
        return Response(content, media_type=media, headers={
            "Content-Disposition": f'attachment; filename="southland-recovery-checklist.{format}"',
            "Cache-Control": "no-store",
        })

    @app.post("/api/cases/{case_id}/report")
    async def report(case_id: str, user=Depends(owner)):
        async with lock(case_id):
            case = repo.get(case_id, user)
            content = ReportService.generate(case, resources.resources)
            case["reports"].append({"id": str(uuid4()), "created_at": now(), "bytes": len(content)})
            case["reports"] = case["reports"][-20:]
            cases.save(case, user, "report.generated")
            return Response(
                content,
                media_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="southland-recovery-packet.pdf"'},
            )

    frontend = ROOT / "frontend/dist"
    if frontend.exists():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
    return app


app = create_app()
