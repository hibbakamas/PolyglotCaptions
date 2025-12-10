from io import BytesIO
from unittest.mock import patch


# Use patch so no ffmpeg is called
@patch("app.routers.caption.azure_transcribe", return_value="hello world")
@patch("app.routers.caption.azure_translate_async", return_value="hola mundo")
def test_create_caption(mock_transcribe, mock_translate, client):
    file = ("audio", BytesIO(b"fake audio"), "audio/webm")

    resp = client.post(
        "/api/captions",
        files={"audio": file},
        data={"from_lang": "en", "to_lang": "es"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["transcript"] == "hello world"
    assert data["translated"] == "hola mundo"


@patch("app.routers.caption.azure_transcribe", return_value="hello")
@patch("app.routers.caption.azure_translate_async", return_value="hola")
def test_delete_caption(mock_transcribe, mock_translate, client):
    # create
    file = ("audio", BytesIO(b"fake audio"), "audio/webm")
    resp = client.post(
        "/api/captions",
        files={"audio": file},
        data={"from_lang": "en", "to_lang": "es"},
    )
    cid = resp.json()["id"]

    # delete
    resp = client.delete(f"/api/captions/{cid}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == cid
