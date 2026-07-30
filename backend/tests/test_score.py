"""Tests du score de réflexion."""
from app.services.reflection_score_service import ReflectionScoreService


def test_score_levels():
    assert ReflectionScoreService.get_level(10) == "Utilisation automatique"
    assert ReflectionScoreService.get_level(30) == "Utilisation réactive"
    assert ReflectionScoreService.get_level(50) == "Utilisation consciente"
    assert ReflectionScoreService.get_level(70) == "Utilisation réfléchie"
    assert ReflectionScoreService.get_level(90) == "Utilisation maîtrisée"


def test_calculate_score_new_user(client, auth_headers):
    resp = client.get("/api/stats/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "score" in data
    assert 0 <= data["score"]["value"] <= 100


def test_today_stats(client, auth_headers):
    client.post("/api/session/start", headers=auth_headers, json={
        "platform_name": "ChatGPT",
        "platform_url": "chatgpt.com",
        "reason": "travail",
        "needs_ai": "yes",
    })
    resp = client.get("/api/stats/today", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["stats"]["sessions_today"] >= 1
