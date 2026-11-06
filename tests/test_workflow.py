import io
import time

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pypdf import PdfReader

from backend.app.main import create_app
from backend.app.services.documents import MAX_UPLOAD
from backend.app.services.resources import ResourceService
from backend.app.services.rules import initial_tasks, match_programs, prioritized_plan, readiness


def test_complete_resident_api_journey(client, case, payload, tmp_path):
    cid = case["id"]
    base = "/api/cases/" + cid
    assert client.get("/api/cases").json()[0]["id"] == cid
    assert client.get(base + "/readiness").json()["percent"] == 0
    image = io.BytesIO()
    Image.new("RGB", (60, 40), "green").save(image, format="PNG")
    documents = []
    for name, data, category in [
        ("photo.png", image.getvalue(), "damage"),
        ("policy.txt", b"SYNTHETIC POLICY EXCERPT: Ask insurer about exclusions.", "policy"),
        ("estimate.txt", b"SYNTHETIC estimate: scope requires contractor verification.", "estimate"),
    ]:
        r = client.post(base + "/documents", files={"file": (name, data)}, data={"category": category})
        assert r.status_code == 201, r.text
        documents.append(r.json())
    assert client.get(base + "/documents/" + documents[0]["id"] + "/file").content == image.getvalue()
    assert (
        client.get(base + "/documents/" + documents[1]["id"] + "/file")
        .headers["content-disposition"]
        .startswith("attachment")
    )
    assert (
        client.post(
            base + "/damage",
            json={"item": "Sofa", "area": "Basement", "observation": "Wet upholstery, resident supplied."},
        ).status_code
        == 201
    )
    assert (
        client.put(base + "/insurance", json={"insurer": "Synthetic Insurer", "claim_number": "DEMO-001"}).status_code
        == 200
    )
    assert (
        client.post(
            base + "/contacts",
            json={
                "organization": "Synthetic Insurer",
                "contacted_on": "2026-09-02",
                "notes": "Asked what evidence to preserve.",
            },
        ).status_code
        == 201
    )
    assert client.get(base + "/readiness").json()["percent"] == 100
    programs = client.get(base + "/programs").json()
    assert all(p["final_eligibility"] is False for p in programs)
    assert next(p for p in programs if p["id"] == "fema")["match_status"] == "Current availability unverified"
    assert next(p for p in programs if p["id"] == "south-holland-flood")["match_status"] == "Potentially relevant"
    task = client.post(base + "/tasks", json={"title": "Call caseworker", "due_date": "2026-11-09"}).json()
    assert client.patch(base + "/tasks/" + task["id"], json={"status": "done"}).json()["status"] == "done"
    assert client.get(base + "/plan").json()[-1]["status"] == "done"
    assert client.put(base, json={**payload, "description": "Updated fictional flood description."}).status_code == 200
    start = time.perf_counter()
    packet = client.post(base + "/report")
    elapsed = (time.perf_counter() - start) * 1000
    assert packet.status_code == 200 and packet.content.startswith(b"%PDF-")
    reader = PdfReader(io.BytesIO(packet.content))
    text = "\n".join(p.extract_text() for p in reader.pages)
    for expected in ["Alex Morgan", "Sofa", "SYNTHETIC", "DEMO-001", "Call caseworker", "Reference directory"]:
        assert expected in text
    assert len(reader.pages) >= 2
    print(f"PDF generation {elapsed:.1f} ms, {len(reader.pages)} pages, {len(packet.content)} bytes")
    assert client.get(base).json()["reports"]
    assert any(e["event"] == "report.generated" for e in client.get(base).json()["audit"])


def test_persists_across_app_restart(tmp_path, payload):
    with TestClient(create_app(tmp_path)) as first:
        case = first.post("/api/cases", json=payload).json()
        cookies = dict(first.cookies)
    with TestClient(create_app(tmp_path)) as second:
        second.cookies.update(cookies)
        assert second.get("/api/cases/" + case["id"]).json()["resident_name"] == payload["resident_name"]


@pytest.mark.parametrize(
    "suffix", ["", "/damage", "/readiness", "/programs", "/resources", "/plan", "/documents/missing/file"]
)
def test_ownership_reads(app, client, case, suffix):
    with TestClient(app) as stranger:
        assert stranger.get("/api/cases/" + case["id"] + suffix).status_code == 404
        assert stranger.get("/api/cases").json() == []


@pytest.mark.parametrize(
    "suffix,body",
    [
        ("/tasks", {"title": "Steal case"}),
        ("/assistant", {"question": "Read case", "consent": True}),
        ("/report", {}),
        ("/plan/ai", {"consent": True}),
    ],
)
def test_ownership_writes(app, case, suffix, body):
    with TestClient(app) as stranger:
        assert stranger.post("/api/cases/" + case["id"] + suffix, json=body).status_code == 404


@pytest.mark.parametrize(
    "patch",
    [
        {"zip_code": "bad"},
        {"incident_date": "2099-01-01"},
        {"resident_name": ""},
        {"description": "short"},
        {"extra": "bad"},
        {"disaster_type": "invalid"},
    ],
)
def test_validation(client, payload, patch):
    assert client.post("/api/cases", json={**payload, **patch}).status_code == 422


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"<script>alert(1)</script>",
        b"\x89PNG\r\n\x1a\ninvalid",
        b"%PDF-1.7 invalid",
        b"\x00bad",
        b"x" * (MAX_UPLOAD + 1),
    ],
)
def test_unsafe_upload(client, case, data):
    r = client.post(
        "/api/cases/" + case["id"] + "/documents", files={"file": ("unsafe.png", data)}, data={"category": "damage"}
    )
    assert r.status_code in {413, 415}
    assert client.get("/api/cases/" + case["id"]).json()["documents"] == []


def test_security_boundaries(client, case, payload):
    assert client.post("/api/cases", json=payload, headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 400
    assert "nosniff" == client.get("/api/health").headers["x-content-type-options"]
    assert (
        client.post("/api/cases", json=payload, headers={"Content-Length": str(MAX_UPLOAD + 2000000)}).status_code
        == 413
    )
    assert client.patch("/api/cases/" + case["id"] + "/tasks/missing", json={"status": "done"}).status_code == 404
    assert client.patch("/api/cases/" + case["id"] + "/tasks/safety", json={"status": "approved"}).status_code == 422


def test_filename_and_category(client, case):
    base = "/api/cases/" + case["id"]
    assert (
        client.post(base + "/documents", files={"file": ("a.txt", b"text")}, data={"category": "invalid"}).status_code
        == 422
    )
    r = client.post(
        base + "/documents", files={"file": ("../../evil.txt", b"harmless text")}, data={"category": "other"}
    )
    assert r.status_code == 201 and r.json()["name"] == "evil.txt"
    assert ".." not in r.json()["storage_key"]


def test_resources_and_duplicates(client):
    rows = client.get("/api/resources?q=food&location=South%20Holland").json()
    assert rows and all(r["source_url"].startswith("https://") for r in rows)
    assert all("verified_at" in r and "limitations" in r for r in rows)
    assert client.get("/api/resources?category=not-a-category").json() == []
    with pytest.raises(ValueError):
        ResourceService.normalize([rows[0], rows[0]])


@pytest.mark.parametrize(
    "municipality,tenure,disaster,status",
    [
        ("Harvey", "owner", "flood", "Published requirements appear not to match"),
        ("South Holland", "renter", "flood", "Published requirements appear not to match"),
        ("South Holland", "unknown", "flood", "More information required"),
        ("South Holland", "owner", "fire", "Published requirements appear not to match"),
        ("South Holland", "owner", "flood", "Potentially relevant"),
    ],
)
def test_mitigation_rules(client, case, municipality, tenure, disaster, status):
    from backend.app.main import ROOT

    case.update(municipality=municipality, property_situation=tenure, disaster_type=disaster)
    programs = match_programs(case, ResourceService(ROOT / "data/resources.json").resources)
    assert next(p for p in programs if p["id"] == "south-holland-flood")["match_status"] == status


def test_task_priority_and_readiness(case):
    assert initial_tasks(case)[0]["priority"] == "urgent"
    assert initial_tasks(case)[1]["id"] == "essentials"
    case.update(displaced=False, immediate_needs=[])
    assert "essentials" not in [t["id"] for t in initial_tasks(case)]
    case["documents"] = [{"category": "damage", "media_type": "text/plain"}]
    assert not readiness(case)["checks"][0]["complete"]
    for t in case["tasks"]:
        t["status"] = "done"
    assert readiness(case)["percent"] == 0
    assert prioritized_plan(case, [])[0]["priority"] == "urgent"


def test_insurer_readiness_requires_matching_contact(case):
    case["insurance"] = {"insurer": "Synthetic Insurer"}
    case["contacts"] = [{"organization": "Food pantry"}]
    assert not readiness(case)["checks"][3]["complete"]
    case["contacts"].append({"organization": " synthetic insurer "})
    assert readiness(case)["checks"][3]["complete"]
