import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["APP_MODE"] = "local"
from backend.app.main import create_app


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    return create_app(tmp_path)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def payload():
    return dict(
        resident_name="Alex Morgan",
        municipality="South Holland",
        zip_code="60473",
        disaster_type="flood",
        incident_date="2026-09-01",
        description="Fictional basement flood damaged sofa and storage boxes.",
        property_situation="owner",
        displaced=True,
        immediate_needs=["food"],
    )


@pytest.fixture
def case(client, payload):
    response = client.post("/api/cases", json=payload)
    assert response.status_code == 201
    return response.json()
