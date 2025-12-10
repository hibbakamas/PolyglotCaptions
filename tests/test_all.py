from datetime import timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.passwords import hash_password, verify_password
from app.services.stt_stub import fake_transcribe
from app.services.translator_azure import azure_translate
from app.services.translator_stub import fake_translate
from app.utils.auth import create_access_token, get_current_user_from_token

client = TestClient(app)

# ------------------------------------------------------------
# PASSWORD TESTS
# ------------------------------------------------------------


def test_password_hash_differs():
    h1 = hash_password("hello")
    h2 = hash_password("hello")
    assert h1 != h2


def test_password_verify_true():
    h = hash_password("test123")
    assert verify_password("test123", h)


def test_password_verify_false():
    h = hash_password("test123")
    assert not verify_password("wrongpass", h)


# ------------------------------------------------------------
# JWT TESTS
# ------------------------------------------------------------


def test_jwt_roundtrip():
    tok = create_access_token({"sub": "vega"}, timedelta(hours=1))
    user = get_current_user_from_token(tok)
    assert user == "vega"


def test_jwt_invalid():
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        get_current_user_from_token("bad.token.here")


# ------------------------------------------------------------
# STT + TRANSLATOR STUB TESTS
# ------------------------------------------------------------


def test_stt_stub_en():
    assert fake_transcribe(b"123", "en") == "stub transcript 1"


def test_stt_stub_es():
    assert fake_transcribe(b"xxx", "es") == "transcripción breve 1"


def test_fake_translate():
    assert fake_translate("hello", "en", "es") == "[es] hello"


# ------------------------------------------------------------
# TRANSLATOR AZURE FALLBACK
# ------------------------------------------------------------


@patch("app.services.translator_azure.settings")
def test_azure_fallback(mock_settings):
    mock_settings.azure_translator_key = ""
    out = azure_translate("hi", "en", "es")
    assert out == "[es] hi"


# ------------------------------------------------------------
# AUTH ROUTER TESTS
# ------------------------------------------------------------


@patch("app.routers.auth.get_user_by_username", return_value=None)
@patch("app.routers.auth.create_user", return_value=True)
@patch("app.routers.auth.pw.hash_password", return_value="hash")
def test_register(mock1, mock2, mock3):
    r = client.post("/api/auth/register", json={"username": "x", "password": "y"})
    assert r.status_code == 200


@patch(
    "app.routers.auth.get_user_by_username",
    return_value={"Username": "x", "HashedPassword": "hash"},
)
@patch("app.routers.auth.pw.verify_password", return_value=True)
def test_login_success(mock1, mock2):
    r = client.post("/api/auth/login", json={"username": "x", "password": "y"})
    assert r.status_code == 200


def test_login_failure():
    r = client.post("/api/auth/login", json={"username": "xx", "password": "bad"})
    assert r.status_code in (400, 401)


# ------------------------------------------------------------
# LOGS ROUTER TEST
# ------------------------------------------------------------


@patch("app.routers.logs.fetch_recent_captions", return_value=[{"Id": 1}])
def test_logs(mocked):
    r = client.get("/api/logs/recent")
    assert r.status_code == 200
    assert r.json() == [{"Id": 1}]


# ------------------------------------------------------------
# CAPTION ROUTER TESTS
# ------------------------------------------------------------


def test_caption_missing_audio():
    r = client.post("/api/captions", data={"from_lang": "en", "to_lang": "es"})
    assert r.status_code == 422


@patch("app.routers.caption.insert_caption_entry", return_value=123)
@patch("app.routers.caption.azure_translate_async", return_value="HOLA")
@patch("app.routers.caption.azure_transcribe", return_value="HELLO")
@patch("app.routers.caption.get_current_user", return_value="user1")
def test_caption_create(mock_user, mock_stt, mock_trans, mock_insert):
    fake_audio = ("file", b"bytes", "audio/webm")
    r = client.post(
        "/api/captions",
        files={"audio": fake_audio},
        data={"from_lang": "en", "to_lang": "es"},
    )
    assert r.status_code == 200
    assert r.json()["id"] == 123


@patch("app.routers.caption.fetch_captions", return_value=[{"Id": 1}])
@patch("app.routers.caption.get_current_user", return_value="user1")
def test_caption_get(mock_user, mock_db):
    r = client.get("/api/captions")
    assert r.status_code == 200
    assert r.json() == [{"Id": 1}]


@patch("app.routers.caption.delete_caption_entry", return_value=True)
@patch("app.routers.caption.get_current_user", return_value="user1")
def test_caption_delete(mock_user, mock_db):
    r = client.delete("/api/captions/1")
    assert r.status_code == 200


# ------------------------------------------------------------
# MANUAL ROUTER TESTS
# ------------------------------------------------------------


@patch("app.routers.manual.azure_translate_async", return_value="hola")
@patch("app.routers.manual.get_current_user", return_value="user1")
def test_manual_translate(mock_user, mock_trans):
    r = client.post(
        "/api/manual/translate", json={"text": "hello", "from_lang": "en", "to_lang": "es"}
    )
    assert r.status_code == 200
    assert r.json()["translated_text"] == "hola"


@patch("app.routers.manual.insert_caption_entry", return_value=55)
@patch("app.routers.manual.get_current_user", return_value="user1")
def test_manual_save(mock_user, mock_db):
    payload = {"transcript": "hello", "translated_text": "hola", "from_lang": "en", "to_lang": "es"}
    r = client.post("/api/manual/save", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "saved"


@patch("app.routers.manual.azure_translate_async", return_value="")
@patch("app.routers.manual.get_current_user", return_value="user1")
def test_manual_translate_empty(mock_user, mock_trans):
    r = client.post("/api/manual/translate", json={"text": "", "from_lang": "en", "to_lang": "es"})
    assert r.status_code == 200


# ------------------------------------------------------------
# HEALTH TESTS
# ------------------------------------------------------------


def test_health_basic():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("app.routers.health.requests.get", side_effect=Exception("fail"))
def test_health_ready(mocked):
    r = client.get("/api/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is False
