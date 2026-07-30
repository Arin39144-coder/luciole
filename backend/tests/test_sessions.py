"""Tests des sessions IA."""


def test_start_session(client, auth_headers):
    resp = client.post("/api/session/start", headers=auth_headers, json={
        "platform_name": "ChatGPT",
        "platform_url": "chatgpt.com",
        "reason": "programmation",
        "needs_ai": "yes",
        "reflections": [
            {"question": "Pourquoi utilisez-vous l'IA ?", "answer": "Programmation"},
            {"question": "Nécessite une IA ?", "answer": "Oui"},
        ],
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "session" in data
    assert data["session"]["reason"] == "programmation"
    assert "score" in data


def test_end_session(client, auth_headers):
    start = client.post("/api/session/start", headers=auth_headers, json={
        "platform_name": "Claude",
        "platform_url": "claude.ai",
        "reason": "recherche",
        "needs_ai": "partially",
    })
    session_id = start.get_json()["session"]["id"]

    resp = client.post("/api/session/end", headers=auth_headers, json={
        "session_id": session_id,
    })
    assert resp.status_code == 200
    assert resp.get_json()["session"]["duration"] is not None


def test_session_history(client, auth_headers):
    client.post("/api/session/start", headers=auth_headers, json={
        "platform_name": "Gemini",
        "platform_url": "gemini.google.com",
        "reason": "etudes",
        "needs_ai": "yes",
    })
    resp = client.get("/api/session/history", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] >= 1


def test_invalid_reason(client, auth_headers):
    resp = client.post("/api/session/start", headers=auth_headers, json={
        "platform_name": "Test",
        "platform_url": "test.com",
        "reason": "invalid_reason",
        "needs_ai": "yes",
    })
    assert resp.status_code == 400
