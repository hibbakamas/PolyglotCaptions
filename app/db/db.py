import logging
import os
from typing import Optional, List, Dict
from datetime import datetime
import pyodbc
from app.config import settings

logger = logging.getLogger("polyglot.db")

# --- Database connection ---
def get_connection():
    """Connect to the Azure SQL database."""
    if settings.azure_sql_connection_string:
        # Use full connection string if provided
        return pyodbc.connect(settings.azure_sql_connection_string, autocommit=True)
    else:
        # Fallback to individual settings
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings.db_server};"
            f"DATABASE={settings.db_name};"
            f"UID={settings.db_user};"
            f"PWD={settings.db_password}"
        )
        return pyodbc.connect(conn_str, autocommit=True)


# --- LOG-ONLY INSERT (old behavior) ---
def log_caption_entry(transcript: str, translation: str, from_lang: str, to_lang: str) -> bool:
    """
    Inserts a caption log into Azure SQL if enabled. Returns True on success, False on failure.
    """
    if not settings.log_captions_to_db:
        logger.debug("DB logging disabled. Skipping insert.")
        return False

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO Captions (Transcript, TranslatedText, FromLang, ToLang)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (transcript, translation, from_lang, to_lang))
            conn.commit()
            logger.info("DB log insert ok.")
            return True
    except Exception as e:
        logger.error(f"Failed to log caption: {e}")
        return False


# --- CREATE ---
def insert_caption_entry(
    transcript: str,
    translated_text: str,
    from_lang: str,
    to_lang: str,
    processing_ms: int,
    session_id: Optional[str] = None,
    created_at: Optional[datetime] = None
) -> int:
    """Insert a full caption entry and return its ID."""
    if created_at is None:
        created_at = datetime.utcnow()

    sql = """
    INSERT INTO dbo.Captions (Transcript, TranslatedText, FromLang, ToLang, ProcessingMs, SessionId, CreatedAt)
    OUTPUT INSERTED.Id
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, transcript, translated_text, from_lang, to_lang, processing_ms, session_id, created_at)
        inserted_id = cursor.fetchone()[0]
        return inserted_id


# --- READ ---
def fetch_captions(session_id: Optional[str] = None) -> List[Dict]:
    try:
        sql = "SELECT * FROM dbo.Captions"
        params: tuple = ()
        if session_id:
            sql += " WHERE SessionId = ?"
            params = (session_id,)
        sql += " ORDER BY CreatedAt DESC"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Failed to fetch captions: {e}")
        raise



def fetch_caption_by_id(caption_id: int) -> Optional[Dict]:
    """Fetch a single caption by ID."""
    sql = "SELECT * FROM dbo.Captions WHERE Id = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, caption_id)
        row = cursor.fetchone()
        if not row:
            return None
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))


# --- UPDATE ---
def update_caption_entry(
    caption_id: int,
    transcript: Optional[str] = None,
    translated_text: Optional[str] = None
) -> Optional[Dict]:
    """Update transcript and/or translated_text for a caption."""
    fields: List[str] = []
    params: List = []
    if transcript is not None:
        fields.append("Transcript = ?")
        params.append(transcript)
    if translated_text is not None:
        fields.append("TranslatedText = ?")
        params.append(translated_text)

    if not fields:
        return fetch_caption_by_id(caption_id)

    params.append(caption_id)
    sql = f"UPDATE dbo.Captions SET {', '.join(fields)} WHERE Id = ?"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if cursor.rowcount == 0:
            return None
        return fetch_caption_by_id(caption_id)


# --- DELETE ---
def delete_caption_entry(caption_id: int) -> bool:
    """Delete a caption by ID."""
    sql = "DELETE FROM dbo.Captions WHERE Id = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, caption_id)
        return cursor.rowcount > 0
