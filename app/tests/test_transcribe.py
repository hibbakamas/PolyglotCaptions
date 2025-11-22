from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


def _post_caption(from_lang: str, to_lang: str):
    files = {
        "audio": ("chunk.webm", b"fake-audio-bytes", "audio/webm")
    }
    data = {
        "from_lang": from_lang,
        "to_lang": to_lang,
    }
    return client.post("/caption", files=files, data=data)


@patch("app.services.stt_azure.azure_transcribe")
def test_caption_azure_stt(mock_azure_stt):
    mock_azure_stt.return_value = "Hello world"
    resp = _post_caption("en", "es")
    assert resp.status_code == 200
    data = resp.json()
    assert data["transcript"] == "Hello world"
    assert isinstance(data["translated_text"], str)
