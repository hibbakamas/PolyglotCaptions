import logging
from typing import Optional, List, Dict
from datetime import datetime
import pyodbc
from app.config import settings

logger = logging.getLogger("polyglot.db")

def get_connection():
    if settings.azure_sql_connection_string:
        return pyodbc.connect(settings.azure_sql_connection_string, autocommit=True)

    raise RuntimeError("No Azure SQL connection string provided")


def insert_caption_entry(
    transcript: str,
    translated_text: str,
    from_lang: str,
    to_lang: str,
    processing_ms: int,
    session_id: Optional[str],
    created_at: datetime,
) -> int:
    sql = """
    INSERT INTO dbo.Captions (Transcript, TranslatedText, FromLang, ToLang,
                              ProcessingMs, SessionId, CreatedAt)
    OUTPUT INSERTED.Id
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, transcript, translated_text, from_lang, to_lang,
                       processing_ms, session_id, created_at)
        row = cursor.fetchone()
        return row[0]


def fetch_captions() -> List[Dict]:
    sql = "SELECT * FROM dbo.Captions ORDER BY CreatedAt DESC"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def fetch_caption_by_id(caption_id: int) -> Optional[Dict]:
    sql = "SELECT * FROM dbo.Captions WHERE Id = ?"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, caption_id)
        row = cur.fetchone()
        if not row: return None
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))


def update_caption_entry(caption_id: int, transcript: str, translated_text: str):
    sql = """
    UPDATE dbo.Captions
    SET Transcript = ?, TranslatedText = ?
    WHERE Id = ?
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, transcript, translated_text, caption_id)
        if cur.rowcount == 0:
            return None
        return fetch_caption_by_id(caption_id)


def delete_caption_entry(caption_id: int) -> bool:
    sql = "DELETE FROM dbo.Captions WHERE Id = ?"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, caption_id)
        return cur.rowcount > 0

def fetch_recent_captions(limit: int = 20):
    sql = f"""
        SELECT TOP ({limit})
            Id, Transcript, TranslatedText, FromLang, ToLang, ProcessingMs, SessionId, CreatedAt
        FROM dbo.Captions
        ORDER BY CreatedAt DESC
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
