import pytest
import os
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

AUTH_TOKEN = "age-check-api-token-2026"


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Home"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json()["project"] == "Age Check API"


def test_check_age_invalid_threshold():
    response = client.post(
        "/check_age",
        data={"user_id": "test123", "threshold": 25},
        files={"image": ("test.jpg", b"fake_image_data", "image/jpeg")},
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
    )
    assert response.status_code == 400
    assert "Threshold must be 18, 21, or 60" in response.json()["detail"]


def test_check_age_invalid_file_type():
    response = client.post(
        "/check_age",
        data={"user_id": "test123", "threshold": 18},
        files={"image": ("test.pdf", b"fake_pdf_data", "application/pdf")},
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_check_age_missing_auth():
    response = client.post(
        "/check_age",
        data={"user_id": "test123", "threshold": 18},
        files={"image": ("test.jpg", b"fake_image_data", "image/jpeg")}
    )
    assert response.status_code == 401


def test_check_age_valid():
    response = client.post(
        "/check_age",
        data={"user_id": "test123", "threshold": 18},
        files={"image": ("test.jpg", b"fake_image_data", "image/jpeg")},
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
    )
    assert response.status_code == 200
    assert response.json()["module"] == "age_check"
    assert response.json()["decision"] in ["pass", "fail"]
    assert "confidence" in response.json()
    assert "latency_ms" in response.json()


def test_get_logs():
    response = client.get("/logs?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)