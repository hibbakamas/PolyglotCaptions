import os
import pytest
from datetime import datetime
from app.services import db
from app.config import settings


@pytest.mark.skipif(
   "pyodbc" not in globals(),
   reason="pyodbc not available locally"
)


def test_insert_caption_entry_integration():
   """
   Integration test for inserting a caption record into Azure SQL DB.
   WARNING: This will insert a real record. Clean up after if necessary.
   """
   from_lang = "en"
   to_lang = "es"
   transcript = "Hello world"
   translated_text = "Hola mundo"
   processing_ms = 456
   session_id = "test-session"


   before = datetime.utcnow()


   # Execute insert
   db.insert_caption_entry(
       from_lang=from_lang,
       to_lang=to_lang,
       transcript=transcript,
       translated_text=translated_text,
       processing_ms=processing_ms,
       session_id=session_id
   )


   conn = db._get_connection()
   cursor = conn.cursor()
   cursor.execute(
       "SELECT TOP 1 FromLang, ToLang, Transcript, TranslatedText, ProcessingMs, SessionId "
       "FROM Captions ORDER BY Id DESC"
   )
   row = cursor.fetchone()
   conn.close()


   assert row is not None
   assert row.FromLang == from_lang
   assert row.ToLang == to_lang
   assert row.Transcript == transcript
   assert row.TranslatedText == translated_text
   assert row.ProcessingMs == processing_ms
   assert row.SessionId == session_id