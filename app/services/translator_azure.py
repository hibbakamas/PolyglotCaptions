"""
Azure Translator integration for PolyglotCaptions.

Uses the REST API via `requests`. If anything goes wrong (missing config,
HTTP error, bad response), we fall back to the local stub translator.
"""
from typing import Any
import logging

import requests

from config import settings
from services.translator_stub import fake_translate as _fallback_fake_translate

logger = logging.getLogger(__name__)


def azure_translate(text: str, from_lang: str, to_lang: str) -> str:
    """
    Translate `text` from `from_lang` to `to_lang` using Azure Translator.

    - Reads key, region and endpoint from settings.
    - Returns the translated text on success.
    - Falls back to `fake_translate` if config is missing or an error occurs.
    """
    if not settings.azure_translator_key or not settings.azure_translator_endpoint:
        logger.warning("Azure Translator not configured; using stub translator.")
        return _fallback_fake_translate(text, from_lang, to_lang)

    base_url = settings.azure_translator_endpoint.rstrip("/")
    url = f"{base_url}/translate"  

    params = {
        "api-version": "3.0",
        "from": (from_lang or "en"),
        "to": [to_lang or "en"],
    }

    headers = {
        "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
        "Ocp-Apim-Subscription-Region": settings.azure_translator_region or "westeurope",
        "Content-Type": "application/json",
    }

    body = [{"text": text}]

    try:
        resp = requests.post(url, params=params, headers=headers, json=body, timeout=10)
        resp.raise_for_status()
        data: list[Any] = resp.json()
        translation = data[0]["translations"][0]["text"]
        return translation
    except Exception as exc: 
        logger.error("Azure Translator error, falling back to stub: %s", exc, exc_info=True)
        return _fallback_fake_translate(text, from_lang, to_lang)
