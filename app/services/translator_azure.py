"""
Azure Translator integration for PolyglotCaptions.

Uses the REST API via `requests`. If Azure Translator is misconfigured,
unavailable, or returns an unexpected response, we fall back to the local
stub translator.
"""

from typing import Any
import logging
import requests

from app.config import settings
from app.services.translator_stub import fake_translate as fallback_translate

logger = logging.getLogger("polyglot.services.translator_azure")


def azure_translate(text: str, from_lang: str, to_lang: str) -> str:
    """
    Translate text using Azure Translator.

    - Requires AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_ENDPOINT
    - Accepts arbitrary languages (auto detected by Azure if from_lang incorrect)
    - Falls back to fake/stub translate on ANY failure.
    """

    if not text:
        return ""

    # Validate configuration
    if (
        not settings.azure_translator_key
        or not settings.azure_translator_endpoint
    ):
        logger.warning("Azure Translator is not configured — using stub translator.")
        return fallback_translate(text, from_lang, to_lang)

    # Build full endpoint
    base = settings.azure_translator_endpoint.rstrip("/")
    url = f"{base}/translate"

    params = {
        "api-version": "3.0",
        "from": from_lang or "",     # Azure can auto-detect if empty
        "to": [to_lang],
    }

    headers = {
        "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
        "Ocp-Apim-Subscription-Region": settings.azure_translator_region,
        "Content-Type": "application/json",
    }

    body = [{"text": text}]

    try:
        resp = requests.post(url, params=params, headers=headers, json=body, timeout=10)
        resp.raise_for_status()

        data: list[Any] = resp.json()
        translated = data[0]["translations"][0]["text"]

        return translated

    except Exception as exc:
        logger.error("Azure Translator failed — using stub. Error: %s", exc, exc_info=True)
        return fallback_translate(text, from_lang, to_lang)
