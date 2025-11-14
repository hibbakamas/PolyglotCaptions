from dataclasses import dataclass
import os
from typing import Dict, Tuple


#preparaing Azure tools for later sprints
@dataclass
class Settings:
    # Azure Speech 
    azure_speech_key: str | None = os.getenv("AZURE_SPEECH_KEY")
    azure_speech_region: str | None = os.getenv("AZURE_SPEECH_REGION")

    # Azure Translator 
    azure_translator_key: str | None = os.getenv("AZURE_TRANSLATOR_KEY")
    azure_translator_region: str | None = os.getenv("AZURE_TRANSLATOR_REGION")


    # this is just for demo / testing purposes
    sample_transcripts: Dict[str, str] = None
    sample_translations: Dict[Tuple[str, str], str] = None


    supported_languages: list[str] = None


    def __post_init__(self):
        self.sample_transcripts = {
            "en": "Hello everyone, welcome to our demo.",
            "es": "Hola a todos, bienvenidos a nuestra demo.",
            "fr": "Bonjour à tous, bienvenue à notre démonstration.",
            "de": "Hallo zusammen, willkommen zu unserer Demo.",
            "it": "Ciao a tutti, benvenuti alla nostra demo.",
        }


        self.sample_translations = {
            ("en", "es"): "Hola a todos, bienvenidos a nuestra demo.",
            ("en", "fr"): "Bonjour à tous, bienvenue à notre démonstration.",
            ("en", "de"): "Hallo zusammen, willkommen zu unserer Demo.",
            ("en", "it"): "Ciao a tutti, benvenuti alla nostra demo.",


            ("es", "en"): "Hello everyone, welcome to our demo.",
            ("fr", "en"): "Hello everyone, welcome to our demo.",
            ("de", "en"): "Hello everyone, welcome to our demo.",
            ("it", "en"): "Hello everyone, welcome to our demo.",
        }


        self.supported_languages = list(self.sample_transcripts.keys())


settings = Settings()