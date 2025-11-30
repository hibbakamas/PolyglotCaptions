from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    # --- Azure ---
    azure_speech_key: str = ""
    azure_speech_region: str = "eastus"

    azure_translator_key: str = ""
    azure_translator_endpoint: str = ""
    azure_translator_region: str = "eastus"
    use_azure_translator: bool = False

    # --- Logging / DB ---
    log_captions_to_db: bool = False
    azure_sql_connection_string: str = ""
    db_server: str = ""
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    # --- Sample transcripts ---
    sample_transcripts: dict = {
        "en": "stub transcript 1",
        "es": "transcripción breve 1",
        "fr": "transcription courte 1",
        "it": "trascrizione breve 1",
        "de": "kurze Transkription 1",
    }

    # --- JWT Settings ---
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    # --- Application Insights ---
    app_insights_key: str = "8960853e-c193-4b8b-8290-0996aaf1a53d"  # <--- ADD THIS

    class Config:
        env_file = ".env"

settings = Settings()
