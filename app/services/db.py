# app/services/db.py

from app.config import settings
import logging

logger = logging.getLogger("polyglot.db")


def insert_caption_entry(transcript: str, translation: str, from_lang: str, to_lang: str) -> bool:
    """
    Inserts a caption log into Azure SQL if enabled. Returns True on success, False on failure.
    """

    # If DB logging disabled → return gracefully
    if not settings.log_captions_to_db:
        logger.debug("DB logging disabled (LOG_CAPTIONS_TO_DB=false). Skipping insert.")
        return False

    # If no connection string, bail quietly
    if not settings.azure_sql_connection_string:
        logger.warning("Azure SQL connection string missing. Cannot insert caption.")
        return False

    try:
        import pyodbc  # 👈 moved local to avoid import errors on macOS

        conn = pyodbc.connect(settings.azure_sql_connection_string, timeout=5)
        cursor = conn.cursor()

        query = """
            INSERT INTO Captions (transcript, translation, from_lang, to_lang)
            VALUES (?, ?, ?, ?)
        """

        cursor.execute(query, (transcript, translation, from_lang, to_lang))
        conn.commit()
        cursor.close()
        conn.close()

        logger.info("DB insert ok.")
        return True

    except Exception as e:
        logger.error(f"Failed to insert caption into DB: {e}")
        return False
