from dataclasses import dataclass
import os


@dataclass
class Settings:
   # Azure Speech
   azure_speech_key: str | None = os.getenv("AZURE_SPEECH_KEY")
   azure_speech_region: str | None = os.getenv("AZURE_SPEECH_REGION")

   # Azure Translator
   azure_translator_key: str | None = os.getenv("AZURE_TRANSLATOR_KEY")
   azure_translator_region: str | None = os.getenv("AZURE_TRANSLATOR_REGION")
   azure_translator_endpoint: str | None = os.getenv("AZURE_TRANSLATOR_ENDPOINT")

    # Azure SQL Database
   azure_sql_connection_string: str | None = os.getenv("AZURE_SQL_CONNECTION_STRING")  
  
   # Feature flags
   use_azure_translator: bool = os.getenv("USE_AZURE_TRANSLATOR", "false").lower() == "true"
   log_captions_to_db: bool = os.getenv("LOG_CAPTIONS_TO_DB", "false").lower() == "true"


   # Azure Application Insights
   app_insights_instrumentation_key: str | None = os.getenv("APP_INSIGHTS_KEY")
   enable_app_insights: bool = os.getenv("ENABLE_APP_INSIGHTS", "false").lower() == "true"


settings = Settings()