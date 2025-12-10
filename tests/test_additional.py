import asyncio
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.routers import caption as caption_router
from app.routers import manual as manual_router
from app.services import jwt_tokens, stt_azure, translator_azure
from app.utils.auth import create_access_token

# ---------------------------------------------------------------------------
# JWT token helpers
# ---------------------------------------------------------------------------


def test_jwt_tokens_roundtrip():
    token = jwt_tokens.create_access_token({"sub": "user1"}, expires=timedelta(minutes=5))
    payload = jwt_tokens.verify_access_token(token)
    assert payload["sub"] == "user1"


def test_jwt_tokens_invalid():
    assert jwt_tokens.verify_access_token("not-a-real-token") is None


# ---------------------------------------------------------------------------
# STT Azure helpers
# ---------------------------------------------------------------------------


def test_convert_webm_to_wav_uses_ffmpeg(monkeypatch):
    created = {}

    def fake_run(cmd, capture_output, check):
        # mimic ffmpeg creating the wav file
        src = Path(cmd[3])
        dst = Path(cmd[4])
        created["src"] = src
        created["dst"] = dst
        dst.write_bytes(b"RIFF")
        src.unlink(missing_ok=True)

    monkeypatch.setattr(stt_azure.subprocess, "run", fake_run)

    wav_path = Path(stt_azure.convert_webm_to_wav(b"abc"))
    assert wav_path.exists()
    assert created["dst"] == wav_path
    wav_path.unlink(missing_ok=True)


def test_azure_transcribe_falls_back_to_stub(monkeypatch):
    monkeypatch.setattr(stt_azure.settings, "azure_speech_key", "")
    monkeypatch.setattr(stt_azure.settings, "azure_speech_region", "")

    calls = {}

    def fake_transcribe(audio_bytes, from_lang):
        calls["args"] = (audio_bytes, from_lang)
        return "stub transcript"

    monkeypatch.setattr(stt_azure, "fake_transcribe", fake_transcribe)

    out = stt_azure.azure_transcribe(b"123", "en")
    assert out == "stub transcript"
    assert calls["args"] == (b"123", "en")


def test_azure_transcribe_empty_audio_returns_empty(monkeypatch):
    monkeypatch.setattr(stt_azure.settings, "azure_speech_key", "")
    result = stt_azure.azure_transcribe(b"", "en")
    assert result == ""


# ---------------------------------------------------------------------------
# Translator Azure
# ---------------------------------------------------------------------------


def test_azure_translate_with_keys_calls_api(monkeypatch):
    monkeypatch.setattr(translator_azure.settings, "azure_translator_key", "key")
    monkeypatch.setattr(
        translator_azure.settings, "azure_translator_endpoint", "https://example.com"
    )
    monkeypatch.setattr(translator_azure.settings, "azure_translator_region", "westus")

    captured = {}

    def fake_post(url, params, headers, json, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return [{"translations": [{"text": "bonjour"}]}]

        return Resp()

    monkeypatch.setattr(translator_azure.requests, "post", fake_post)

    out = translator_azure.azure_translate("hello", "en-US", "fr")
    assert out == "bonjour"
    assert captured["params"]["from"] == "en"
    assert captured["params"]["to"] == ["fr"]
    assert captured["headers"]["Ocp-Apim-Subscription-Key"] == "key"
    assert captured["url"].endswith("/translate")


# ---------------------------------------------------------------------------
# Caption router auth helper
# ---------------------------------------------------------------------------


def test_caption_get_current_user_requires_header():
    request = Request(
        {"type": "http", "headers": [], "method": "GET", "path": "/", "scheme": "http"}
    )
    with pytest.raises(HTTPException):
        asyncio.run(caption_router.get_current_user(request))


def test_caption_get_current_user_valid_token():
    token = create_access_token({"sub": "alice"}, timedelta(minutes=5))
    headers = [(b"authorization", f"Bearer {token}".encode())]
    request = Request(
        {"type": "http", "headers": headers, "method": "GET", "path": "/", "scheme": "http"}
    )
    user = asyncio.run(caption_router.get_current_user(request))
    assert user == "alice"


# ---------------------------------------------------------------------------
# Caption router error branches
# ---------------------------------------------------------------------------


def test_update_caption_missing_field(client):
    resp = client.put("/api/captions/1", json={})
    assert resp.status_code == 400


@patch("app.routers.caption.update_caption_entry", return_value=False)
def test_update_caption_not_found(mock_update, client):
    resp = client.put("/api/captions/99", json={"translated_text": "hola"})
    assert resp.status_code == 404


@patch("app.routers.caption.delete_caption_entry", return_value=False)
def test_delete_caption_not_found(mock_delete, client):
    resp = client.delete("/api/captions/123")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Logs router
# ---------------------------------------------------------------------------


@patch("app.routers.logs.fetch_recent_captions", return_value=None)
def test_logs_returns_empty_when_no_records(mock_fetch, client):
    resp = client.get("/api/logs/recent")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Manual router auth helper
# ---------------------------------------------------------------------------


def test_manual_get_current_user_requires_header():
    request = Request(
        {"type": "http", "headers": [], "method": "GET", "path": "/", "scheme": "http"}
    )
    with pytest.raises(HTTPException):
        asyncio.run(manual_router.get_current_user(request))


# ---------------------------------------------------------------------------
# Auth router duplicate registration
# ---------------------------------------------------------------------------


@patch("app.routers.auth.get_user_by_username", return_value={"Username": "bob"})
def test_register_rejects_duplicate(mock_get, client):
    resp = client.post("/api/auth/register", json={"username": "bob", "password": "pw"})
    assert resp.status_code == 400
