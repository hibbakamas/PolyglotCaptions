# app/services/translator_azure.py

import logging
import requests
import asyncio
from app.config import settings
from app.services.translator_stub import fake_translate

logger = logging.getLogger("polyglot.services.translator_azure")

def normalize_lang(lang: str) -> str:
    """
    Azure Translator expects short language codes (e.g. 'en', 'es').
    STT might give us 'en-US' or similar. Handle that.
    Returns None for 'auto' to trigger auto-detection.
    """
    if not lang or lang == "auto":
        return None
    if "-" in lang:
        return lang.split("-")[0]
    return lang

def azure_translate(text: str, from_lang: str, to_lang: str) -> str:
    if not text:
        return ""

    # Normalize full codes (en-US → en)
    from_lang = normalize_lang(from_lang)
    to_lang = normalize_lang(to_lang)

    # Use stub if no Azure keys
    if not settings.azure_translator_key or not settings.azure_translator_endpoint:
        return fake_translate(text, from_lang or "auto", to_lang)

    url = settings.azure_translator_endpoint.rstrip("/") + "/translate"
    params = {
        "api-version": "3.0",
        "to": [to_lang],
    }
    
    # Only add 'from' parameter if it's not auto-detection
    if from_lang:
        params["from"] = from_lang
    
    headers = {
        "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
        "Ocp-Apim-Subscription-Region": settings.azure_translator_region,
        "Content-Type": "application/json",
    }

    resp = requests.post(url, params=params, headers=headers, json=[{"text": text}], timeout=10)
    resp.raise_for_status()

    data = resp.json()
    return data[0]["translations"][0]["text"]

async def azure_translate_async(text: str, from_lang: str, to_lang: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: azure_translate(text, from_lang, to_lang)
    )