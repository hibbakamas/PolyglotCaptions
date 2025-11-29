"""
Azure Translator integration for PolyglotCaptions.
"""

from typing import Any
import logging
import requests
import asyncio

from app.config import settings
from app.services.translator_stub import fake_translate as fallback_translate

logger = logging.getLogger("polyglot.services.translator_azure")


def azure_translate(text: str, from_lang: str, to_lang: str) -> str:
    if not text:
        return ""

    if (
        not settings.azure_translator_key
        or not settings.azure_translator_endpoint
    ):
        logger.warning("Azure Translator missing — using stub.")
        return fallback_translate(text, from_lang, to_lang)

    url = settings.azure_translator_endpoint.rstrip("/") + "/translate"

    params = {
        "api-version": "3.0",
        "from": from_lang or "",
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
        return data[0]["translations"][0]["text"]

    except Exception as exc:
        logger.error("Azure Translator failed — using stub. Error: %s", exc)
        return fallback_translate(text, from_lang, to_lang)


async def azure_translate_async(text: str, from_lang: str, to_lang: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: azure_translate(text, from_lang, to_lang)
    )
