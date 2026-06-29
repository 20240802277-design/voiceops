from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_dashboard():
    """Verify that GET / returns the dashboard HTML successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "VoiceOps Sentinel" in response.text
    assert "Ingest Audio Call" in response.text


def test_get_health():
    """Verify that GET /health returns the correct JSON health check payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "voiceops-sentinel"
    assert "asr_backend" in response.json()


def test_get_audio_endpoint_not_found():
    """Verify that a non-existent job ID returns a 404 error."""
    response = client.get("/calls/non-existent-job-id/audio")
    assert response.status_code == 404
    assert response.json()["detail"] == "Audio file for job 'non-existent-job-id' not found."


def test_get_audio_endpoint_success():
    """Verify that an existing audio file is served correctly by the audio endpoint."""
    from app.main import audio_dir
    job_id = "test-job-1234"
    test_file = audio_dir / f"{job_id}.wav"
    try:
        # Create a dummy WAV file
        test_file.write_bytes(b"mock WAV data content")
        
        response = client.get(f"/calls/{job_id}/audio")
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"mock WAV data content"
    finally:
        if test_file.exists():
            test_file.unlink()

