"""
Simple DB layer for logging and retrieving caption events from Azure SQL Database.
Used in Sprint 3 for the /api/captions/logs endpoint.
"""


import logging
from datetime import datetime
from typing import Optional, List, Dict, Any


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




# ------------------------------------------------------------------
# INSERT CAPTION ENTRY (already existed in your project)
# ------------------------------------------------------------------
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


       now = datetime.utcnow()


       cursor.execute(
           """
           INSERT INTO dbo.Captions
               (CreatedAt, SessionId, FromLang, ToLang, Transcript, TranslatedText, ProcessingMs)
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




# ------------------------------------------------------------------
# FETCH CAPTION ENTRIES (new in Sprint 3)
# ------------------------------------------------------------------
def fetch_recent_captions(limit: int = 20) -> List[Dict[str, Any]]:
   """
   Fetch the N most recent caption events.


   Returns a list of dicts so it is easy to JSON-serialize.
   On error, returns an empty list and logs the failure.
   """
   try:
       conn = _get_connection()
       cursor = conn.cursor()


       cursor.execute(
           """
           SELECT TOP (?)
               Id,
               CreatedAt,
               SessionId,
               FromLang,
               ToLang,
               Transcript,
               TranslatedText,
               ProcessingMs
           FROM dbo.Captions
           ORDER BY CreatedAt DESC;
           """,
           limit,
       )


       rows = cursor.fetchall()
       columns = [col[0] for col in cursor.description]


       results: List[Dict[str, Any]] = []
       for row in rows:
           results.append({col: getattr(row, col) for col in columns})


       return results


   except Exception as exc:  # noqa: BLE001
       logger.error("Failed to fetch recent captions: %s", exc, exc_info=True)
       return []


   finally:
       try:
           conn.close()  # type: ignore[has-type]
       except Exception:
           pass
