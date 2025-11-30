# app/db/db.py

import os
import pyodbc
from datetime import datetime
from app.config import settings

# ============================================================
#   DETERMINE IF WE ARE RUNNING IN CI (GitHub Actions)
# ============================================================

RUNNING_IN_CI = os.getenv("CI") == "true"

# ============================================================
#   REAL DATABASE CONNECTION  (LOCAL / PRODUCTION)
# ============================================================

def get_connection():
    """
    Uses Azure SQL connection string during real execution.
    In CI, we return None because tests use the stub DB.
    """
    if RUNNING_IN_CI:
        return None  # CI will use the fake DB

    if settings.azure_sql_connection_string:
        return pyodbc.connect(
            settings.azure_sql_connection_string,
            autocommit=True
        )

    raise RuntimeError("No Azure SQL connection string provided")


# ============================================================
#   IN-MEMORY STUB DATABASE FOR CI / TESTING
# ============================================================

_FAKE_CAPTIONS = {}   # caption_id → record dict
_FAKE_USERS = {}      # username → { Username, HashedPassword }
_NEXT_ID = 1


# ------------------ STUB: USERS ------------------

def _fake_get_user_by_username(username):
    return _FAKE_USERS.get(username)

def _fake_create_user(username, hashed_password):
    _FAKE_USERS[username] = {
        "Username": username,
        "HashedPassword": hashed_password
    }


# ------------------ STUB: CAPTIONS ------------------

def _fake_insert_caption_entry(
    transcript,
    translated_text,
    from_lang,
    to_lang,
    processing_ms,
    session_id=None,
    user_id=None,
    created_at=None,
):
    global _NEXT_ID
    cid = _NEXT_ID
    _NEXT_ID += 1

    _FAKE_CAPTIONS[cid] = {
        "Id": cid,
        "Transcript": transcript,
        "TranslatedText": translated_text,
        "FromLang": from_lang,
        "ToLang": to_lang,
        "ProcessingMs": processing_ms,
        "SessionId": session_id,
        "UserId": user_id,
        "CreatedAt": created_at or datetime.utcnow(),
    }
    return cid


def _fake_fetch_captions(user_id=None):
    return list(_FAKE_CAPTIONS.values())


def _fake_delete_caption_entry(caption_id, user_id=None):
    return _FAKE_CAPTIONS.pop(caption_id, None) is not None


def _fake_fetch_recent_captions():
    return list(_FAKE_CAPTIONS.values())


# ============================================================
#             REAL DATABASE USER METHODS
# ============================================================

def _real_get_user_by_username(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Username, HashedPassword FROM Users WHERE Username = ?",
            username
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {"Username": row[0], "HashedPassword": row[1]}


def _real_create_user(username, hashed_password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Users (Username, HashedPassword)
            VALUES (?, ?)
            """,
            username,
            hashed_password
        )


# ============================================================
#             REAL DATABASE CAPTION METHODS
# ============================================================

def _real_insert_caption_entry(
    transcript,
    translated_text,
    from_lang,
    to_lang,
    processing_ms,
    session_id=None,
    user_id=None,
    created_at=None,
):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Captions (Transcript, TranslatedText, FromLang, ToLang,
                ProcessingMs, SessionId, UserId, CreatedAt)
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            transcript,
            translated_text,
            from_lang,
            to_lang,
            processing_ms,
            session_id,
            user_id,
            created_at or datetime.utcnow(),
        )
        row = cursor.fetchone()
        return row[0]


def _real_fetch_captions(user_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Captions WHERE UserId = ? ORDER BY CreatedAt DESC",
            user_id,
        )
        rows = cursor.fetchall()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]


def _real_delete_caption_entry(caption_id, user_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Captions WHERE Id = ? AND UserId = ?",
            caption_id,
            user_id,
        )
        return cursor.rowcount > 0


def _real_fetch_recent_captions():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM Captions
            ORDER BY CreatedAt DESC
            OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY
            """
        )
        rows = cursor.fetchall()
        return [
            dict(zip([col[0] for col in cursor.description], row))
            for row in rows
        ]


# ============================================================
#   EXPORT PUBLIC FUNCTIONS (CI uses stub, local uses real)
# ============================================================

get_user_by_username = (
    _fake_get_user_by_username if RUNNING_IN_CI else _real_get_user_by_username
)
create_user = (
    _fake_create_user if RUNNING_IN_CI else _real_create_user
)

insert_caption_entry = (
    _fake_insert_caption_entry if RUNNING_IN_CI else _real_insert_caption_entry
)
fetch_captions = (
    _fake_fetch_captions if RUNNING_IN_CI else _real_fetch_captions
)
delete_caption_entry = (
    _fake_delete_caption_entry if RUNNING_IN_CI else _real_delete_caption_entry
)
fetch_recent_captions = (
    _fake_fetch_recent_captions if RUNNING_IN_CI else _real_fetch_recent_captions
)
