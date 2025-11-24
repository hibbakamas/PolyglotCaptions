from fastapi.testclient import TestClient
from unittest.mock import patch
from app.config import settings


def _post_caption(from_lang: str, to_lang: str):
   from app.main import app
   client = TestClient(app)
  
   files = {
       "audio": ("sample.mp3", b"fake-audio-bytes", "audio/mp3")
   }
   data = {
       "from_lang": from_lang,
       "to_lang": to_lang,
   }
   return client.post("/api/caption", files=files, data=data)


@patch("app.routers.caption.azure_transcribe")
@patch("app.routers.caption.fake_translate")
def test_caption_with_mocked_stt(mock_fake_translate, mock_azure_stt):
   """Unit test /caption with mocked Azure STT"""
   mock_azure_stt.return_value = "Hello world"
   mock_fake_translate.return_value = "Fake translation"
  
   original_setting = settings.use_azure_translator
   settings.use_azure_translator = False
  
   try:
       resp = _post_caption("en", "es")
       assert resp.status_code == 200
       data = resp.json()
       assert data["transcript"] == "Hello world"
       assert data["translated_text"] == "Fake translation"
       assert mock_azure_stt.called
   finally:
       settings.use_azure_translator = original_setting


@patch("app.routers.caption.azure_transcribe")
@patch("app.routers.caption.azure_translate")
def test_caption_with_mocked_translation(mock_translate, mock_azure_stt):
   """Unit test /caption with mocked Azure Translator"""
   mock_azure_stt.return_value = "Hello world"
   mock_translate.return_value = "Hola mundo"
  
   original_setting = settings.use_azure_translator
   settings.use_azure_translator = True
  
   try:
       resp = _post_caption("en", "es")
       data = resp.json()
       assert resp.status_code == 200
       assert data["translated_text"] == "Hola mundo"
       assert data["transcript"] == "Hello world"
       mock_translate.assert_called_once_with(
           text="Hello world",
           from_lang="en",
           to_lang="es"
       )
   finally:
       settings.use_azure_translator = original_setting