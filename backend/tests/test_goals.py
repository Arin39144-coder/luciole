"""Tests des objectifs."""


def test_get_goal(client, auth_headers):
    resp = client.get("/api/goals", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["goal"]["daily_limit"] == 120


def test_update_goal(client, auth_headers):
    resp = client.put("/api/goals", headers=auth_headers, json={"daily_limit": 90})
    assert resp.status_code == 200
    assert resp.get_json()["goal"]["daily_limit"] == 90


def test_update_goal_invalid(client, auth_headers):
    resp = client.put("/api/goals", headers=auth_headers, json={"daily_limit": 5})
    assert resp.status_code == 400
