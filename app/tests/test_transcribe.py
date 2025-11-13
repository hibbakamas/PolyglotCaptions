from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_translate_en_es():
   payload = {
       "text": "Hello everyone",
       "from_lang": "en",
       "to_lang": "es",
   }
   response = client.post("/translate", json=payload)
   assert response.status_code == 200
   data = response.json()
   assert "translated_text" in data
   assert data["from_lang"] == "en"
   assert data["to_lang"] == "es"
   assert data["translated_text"] != ""

def test_transcribe_text_echo():
   payload = {
       "text": "This is a test",
   }
   response = client.post("/transcribe", json=payload)
   assert response.status_code == 200
   data = response.json()
   assert data["transcript"] == "This is a test"