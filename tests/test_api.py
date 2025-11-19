# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthcheck():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Triage agent running"}


def test_triage_known_issue():
    payload = {"description": "When I try to checkout on my phone I get a 500 payment error."}
    res = client.post("/triage", json=payload)
    assert res.status_code == 200
    body = res.json()
    # basic shape checks
    assert "summary" in body
    assert "category" in body
    assert "severity" in body
    assert "match_type" in body
    assert "kb_matches" in body
    # for this KB and mock logic we expect either known_issue or new_issue
    assert body["match_type"] in ("known_issue", "new_issue")
    # if known_issue, kb_matches should be non-empty
    if body["match_type"] == "known_issue":
        assert len(body["kb_matches"]) >= 1
        assert isinstance(body["kb_matches"][0]["score"], float)


def test_triage_empty_description():
    payload = {"description": "   "}
    res = client.post("/triage", json=payload)
    assert res.status_code == 400
