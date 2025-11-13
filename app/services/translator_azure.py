from .translator_stub import fake_translate as _fallback_fake_translate
from app.config import settings




def azure_translate(text: str, from_lang: str, to_lang: str) -> str:
   """
   Placeholder implementation.


   Later:
   - Use Azure Translator Text API
   - Read subscription key & region from settings
   """
   # For Sprint 1 we just call the stub so nothing breaks.
   return _fallback_fake_translate(text, from_lang, to_lang)