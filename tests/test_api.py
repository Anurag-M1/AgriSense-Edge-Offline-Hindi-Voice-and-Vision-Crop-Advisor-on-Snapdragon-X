"""
test_api.py — Integration tests for AgriSense Edge FastAPI HTTP service.

Verifies:
1. GET /api/health returns engine statuses and active backend.
2. POST /api/diagnose handles multimodal (image + text) inputs and streams stages.
3. POST /api/feedback records farmer feedback into SQLite.
4. GET /api/settings returns configuration.
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


class TestAPIEndpoints:
    """Test suite for FastAPI endpoints."""

    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "backend" in data
        assert "engines" in data
        assert "asr" in data["engines"]
        assert "vision" in data["engines"]
        assert "llm" in data["engines"]
        assert "tts" in data["engines"]

    def test_diagnose_with_image_and_text(self, client):
        # Create a test leaf image
        img = Image.new("RGB", (224, 224), color=(50, 140, 50))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            "/api/diagnose",
            files={"image": ("test_leaf.jpg", img_bytes, "image/jpeg")},
            data={"text_input": "टमाटर के पत्तों पर भूरे धब्बे हैं क्या उपाय करें?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "disease_label" in data
        assert "confidence" in data
        assert "advice_text" in data
        assert len(data["advice_text"]) > 0
        assert "stages" in data
        assert len(data["stages"]) > 0
        assert data["total_latency_ms"] >= 0
        assert data["case_id"] is not None

        # Test feedback on this case
        case_id = data["case_id"]
        fb_resp = client.post(
            "/api/feedback",
            json={"case_id": case_id, "helpful": True, "comment": "बहुत बढ़िया सलाह"},
        )
        assert fb_resp.status_code == 200
        assert fb_resp.json()["status"] == "ok"

    def test_diagnose_empty_input_returns_400(self, client):
        response = client.post("/api/diagnose")
        assert response.status_code == 400

    def test_settings_endpoint(self, client):
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "backend" in data
        assert "vision_confidence_threshold" in data
