def test_manual_translate(client):
    body = {"text": "hello", "from_lang": "en", "to_lang": "es"}
    resp = client.post("/api/manual/translate", json=body)
    assert resp.status_code == 200
    assert "translated_text" in resp.json()


def test_manual_save(client):
    body = {"transcript": "hello", "translated_text": "hola", "from_lang": "en", "to_lang": "es"}
    resp = client.post("/api/manual/save", json=body)
    assert resp.status_code == 200
    assert resp.json()["status"] == "saved"
