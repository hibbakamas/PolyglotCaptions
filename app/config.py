import os

class Settings:
    APP_ENV = os.getenv("APP_ENV", "local")
    FROM_LANG = os.getenv("FROM_LANG", "en")
    TO_LANG = os.getenv("TO_LANG", "es")

settings = Settings()