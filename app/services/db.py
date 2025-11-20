"""
Simple DB layer for logging caption events to Azure SQL Database.
"""

import logging
from datetime import datetime
from typing import Optional

import pyodbc

from config import settings

logger = logging.getLogger(__name__)


def _get_connection() -> pyodbc.Connection:
    """
    Create a new connection to Azure SQL using the connection string
    from environment variable AZURE_SQL_CONNECTION_STRING.
    """
    if not settings.azure_sql_connection_string:
        raise RuntimeError("AZURE_SQL_CONNECTION_STRING not configured")

    conn = pyodbc.connect(settings.azure_sql_connection_string)
    return conn


def insert_caption_entry(
    from_lang: str,
    to_lang: str,
    transcript: str,
    translated_text: str,
    processing_ms: int,
    session_id: Optional[str] = None,
) -> None:
    """
    Insert a caption record into the Captions table.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Table schema:
        # CREATE TABLE Captions (
        #     Id INT IDENTITY(1,1) PRIMARY KEY,
        #     CreatedAt DATETIME2 NOT NULL,
        #     SessionId NVARCHAR(100) NULL,
        #     FromLang NVARCHAR(10) NOT NULL,
        #     ToLang NVARCHAR(10) NOT NULL,
        #     Transcript NVARCHAR(MAX) NOT NULL,
        #     TranslatedText NVARCHAR(MAX) NOT NULL,
        #     ProcessingMs INT NOT NULL
        # );

        now = datetime.utcnow()

        cursor.execute(
            """
            INSERT INTO Captions (CreatedAt, SessionId, FromLang, ToLang, Transcript, TranslatedText, ProcessingMs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            now,
            session_id,
            from_lang,
            to_lang,
            transcript,
            translated_text,
            processing_ms,
        )
        conn.commit()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to insert caption entry into DB: %s", exc, exc_info=True)
    finally:
        try:
            conn.close()  # type: ignore[has-type]
        except Exception:
            pass
