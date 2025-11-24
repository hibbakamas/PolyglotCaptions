import logging
from datetime import datetime
from typing import Optional

import pyodbc

from app.config import settings


logger = logging.getLogger(__name__)


def _get_connection() -> pyodbc.Connection:
   if not settings.azure_sql_connection_string:
       raise RuntimeError("AZURE_SQL_CONNECTION_STRING not configured")
   return pyodbc.connect(settings.azure_sql_connection_string, autocommit=False)


def insert_caption_entry(
   from_lang: str,
   to_lang: str,
   transcript: str,
   translated_text: str,
   processing_ms: int,
   session_id: Optional[str] = None,
) -> None:
 
   conn = None
   try:
       conn = _get_connection()
       with conn.cursor() as cursor:
           now = datetime.utcnow()
           cursor.execute(
               now,
               session_id,
               from_lang,
               to_lang,
               transcript,
               translated_text,
               processing_ms,
           )
       conn.commit()
   except Exception as exc:
       logger.error("Failed to insert caption entry into DB: %s", exc, exc_info=True)
       if conn:
           try:
               conn.rollback()
           except Exception as rb_exc:
               logger.error("Rollback failed: %s", rb_exc, exc_info=True)
   finally:
       if conn:
           try:
               conn.close()
           except Exception as close_exc:
               logger.warning("Failed to close DB connection: %s", close_exc, exc_info=True)