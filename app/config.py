# app/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_speech_key: str = ""
    azure_speech_region: str = "eastus"

    azure_translator_key: str = ""
    azure_translator_endpoint: str = ""
    azure_translator_region: str = "eastus"
    use_azure_translator: bool = False

    log_captions_to_db: bool = False

    sample_transcripts: dict = {
        "en": "stub transcript 1",
        "es": "transcripción breve 1",
        "fr": "transcription courte 1",
        "it": "trascrizione breve 1",
        "de": "kurze Transkription 1",
    }

    class Config:
        env_file = ".env"


settings = Settings()
