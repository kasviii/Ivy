import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MOCK_RESULT = {
    "topic": "test topic",
    "papers": [
        {
            "title": "Test Paper",
            "abstract": "Test abstract",
            "authors": ["Author One"],
            "year": 2024,
            "source": "arxiv"
        }
    ],
    "summaries": ["Test summary"],
    "reflection": "Good coverage",
    "needs_more_papers": False,
    "final_review": "# Literature Review\n\nThis is a test review.",
    "iteration": 0,
    "status": "complete"
}

with patch("src.agent.researcher.run_research", return_value=MOCK_RESULT):
    from src.api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_start_research():
    response = client.post("/research", json={"topic": "machine learning"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["topic"] == "machine learning"
    assert data["status"] == "queued"

def test_get_job():
    res = client.post("/research", json={"topic": "deep learning"})
    job_id = res.json()["job_id"]
    response = client.get(f"/research/{job_id}")
    assert response.status_code == 200
    assert response.json()["job_id"] == job_id

def test_get_job_not_found():
    response = client.get("/research/nonexistent-job-id")
    assert response.status_code == 404

def test_list_jobs():
    response = client.get("/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_status():
    res = client.post("/research", json={"topic": "neural networks"})
    job_id = res.json()["job_id"]
    response = client.get(f"/research/{job_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "progress" in data

def test_empty_topic():
    response = client.post("/research", json={"topic": ""})
    assert response.status_code in [200, 422]