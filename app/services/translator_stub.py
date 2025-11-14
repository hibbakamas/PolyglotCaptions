from app.config import settings

def fake_translate(text: str, from_lang: str, to_lang: str) -> str:
    src = (from_lang or "en").lower()
    tgt = (to_lang or "en").lower()

    if src == tgt:
        return text

    return settings.sample_translations.get((src, tgt), f"[{tgt}] {text}")