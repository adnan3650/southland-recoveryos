import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Resource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=2)
    name: str
    category: str
    description: str
    geographic_coverage: list[str]
    eligibility: list[str]
    contact: str
    source_url: HttpUrl
    verified_at: str | None
    verification: str
    availability: str
    limitations: str
    needs: list[str]
    program: bool = False


class ResourceService:
    def __init__(self, path: Path):
        self.path = path
        self.resources = self.normalize(json.loads(path.read_text()))

    @staticmethod
    def normalize(rows):
        seen, resources = set(), []
        for raw in rows:
            resource = Resource.model_validate(raw).model_dump(mode="json")
            key = (resource["name"].casefold().strip(), resource["source_url"].rstrip("/"))
            if resource["id"] in {r["id"] for r in resources} or key in seen:
                raise ValueError("Duplicate resource record")
            seen.add(key)
            resources.append(resource)
        return resources

    def search(self, query="", category="", location=""):
        query, location = query.casefold().strip(), location.casefold().strip()

        def matches(r):
            text = json.dumps(r).casefold()
            coverage = {x.casefold() for x in r["geographic_coverage"]}
            local = (
                not location or location in coverage or bool(coverage & {"cook county", "illinois", "united states"})
            )
            return (not query or query in text) and (not category or category == r["category"]) and local

        return [r for r in self.resources if matches(r)]

    def immediate(self, case):
        matches = self.search(location=case["municipality"])
        needs = set(case["immediate_needs"]) | ({"shelter"} if case["displaced"] else set())
        return sorted(matches, key=lambda r: -len(needs.intersection(r["needs"])))
