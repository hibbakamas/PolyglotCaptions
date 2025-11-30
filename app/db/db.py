import logging
from typing import Optional, Dict, List
from datetime import datetime
import pyodbc
from app.config import settings

logger = logging.getLogger("polyglot.db")


def get_connection():
    """
    Return a pyodbc connection using the Azure SQL connection string.
    Raises an error if no connection string is configured.
    """
    if settings.azure_sql_connection_string:
        return pyodbc.connect(
            settings.azure_sql_connection_string,
            autocommit=True
        )
    raise RuntimeError("No Azure SQL connection string provided")


def insert_caption_entry(
    transcript: str,
    translated_text: str,
    from_lang: str,
    to_lang: str,
    processing_ms: int,
    session_id: Optional[str],
    user_id: str,
    created_at: datetime,
) -> int:
    """
    Insert a caption row and return the new ID.
    Matches schema:
        Id, Transcript, TranslatedText, FromLang, ToLang,
        ProcessingMs, SessionId, UserId, CreatedAt
    """
    sql = """
    INSERT INTO dbo.Captions (
        Transcript, TranslatedText, FromLang, ToLang,
        ProcessingMs, SessionId, UserId, CreatedAt
    )
    OUTPUT INSERTED.Id
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            sql,
            transcript,
            translated_text,
            from_lang,
            to_lang,
            processing_ms,
            session_id,
            user_id,
            created_at
        )
        new_row = cur.fetchone()
        return new_row[0]


def fetch_captions(user_id: str) -> List[Dict]:
    """
    Get all captions belonging to a user.
    Ordered newest first.
    """
    sql = """
    SELECT *
    FROM dbo.Captions
    WHERE UserId = ?
    ORDER BY CreatedAt DESC
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, user_id)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_caption_by_id(caption_id: int) -> Optional[Dict]:
    sql = "SELECT * FROM dbo.Captions WHERE Id = ?"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, caption_id)
        row = cur.fetchone()
        if not row:
            return None

        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))


def update_caption_entry(
    caption_id: int,
    transcript: str,
    translated_text: str
) -> Optional[Dict]:
    """
    Update a caption's transcript + translated text.
    """
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


def delete_caption_entry(caption_id: int, user_id: str) -> bool:
    """
    Delete a caption only if it belongs to the authenticated user.
    """
    sql = "DELETE FROM dbo.Captions WHERE Id = ? AND UserId = ?"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, caption_id, user_id)
        return cur.rowcount > 0


def fetch_recent_captions(limit: int = 20) -> List[Dict]:
    """
    Recent captions for the logs dashboard.
    """
    sql = f"""
    SELECT TOP ({limit})
        Id, Transcript, TranslatedText, FromLang, ToLang,
        ProcessingMs, SessionId, CreatedAt, UserId
    FROM dbo.Captions
    ORDER BY CreatedAt DESC
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Return a user dict or None.
    """
    sql = "SELECT * FROM dbo.Users WHERE Username = ?"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, username)
        row = cur.fetchone()

        if not row:
            return None

        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))


def create_user(username: str, hashed_password: str):
    """
    Insert a new user.
    """
    sql = """
    INSERT INTO dbo.Users (Username, HashedPassword)
    VALUES (?, ?)
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, username, hashed_password)
