import pytest
from unittest.mock import patch, MagicMock
from app.services import db


def test_insert_caption_entry_success():
   mock_conn = MagicMock()
   mock_cursor = MagicMock()
   mock_conn.cursor.return_value.__enter__.return_value = mock_cursor


   with patch("app.services.db._get_connection", return_value=mock_conn):
       db.insert_caption_entry(
           from_lang="en",
           to_lang="es",
           transcript="Hello",
           translated_text="Hola",
           processing_ms=123,
           session_id="abc123"
       )


   mock_cursor.execute.assert_called_once()
   mock_conn.commit.assert_called_once()
   mock_conn.close.assert_called_once()


def test_insert_caption_entry_failure_rolls_back():
   mock_conn = MagicMock()
   mock_cursor = MagicMock()
   mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
   mock_cursor.execute.side_effect = Exception("DB insert failed")


   with patch("app.services.db._get_connection", return_value=mock_conn):
       db.insert_caption_entry(
           from_lang="en",
           to_lang="es",
           transcript="Hello",
           translated_text="Hola",
           processing_ms=123,
           session_id="abc123"
       )


   mock_conn.rollback.assert_called_once()
   mock_conn.close.assert_called_once()