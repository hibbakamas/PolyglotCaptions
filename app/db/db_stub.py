"""
Stateful DB Stub used ONLY for CI.
Simulates the Azure SQL DB fully in memory so tests behave consistently.
"""

# In-memory fake DB
_FAKE_CAPTIONS = {}
_FAKE_USERS = {
    "testuser": {
        "username": "testuser",
        "hashed_password": "$2b$12$FakeHashedPasswordForTestsOnly",
    }
}

# Auto-increment counter for captions
_NEXT_ID = 1


# ---------------------------
# USER FUNCTIONS (auth.py)
# ---------------------------
def get_user_by_username(username: str):
    return _FAKE_USERS.get(username)


def create_user(username: str, hashed_password: str):
    _FAKE_USERS[username] = {
        "username": username,
        "hashed_password": hashed_password,
    }
    return True


# ---------------------------
# CAPTION FUNCTIONS
# ---------------------------
def insert_caption_entry(
    transcript,
    translated_text,
    from_lang,
    to_lang,
    processing_ms,
    session_id=None,
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
    }
    return cid


def fetch_captions():
    return list(_FAKE_CAPTIONS.values())


def fetch_recent_captions():
    return fetch_captions()


def delete_caption_entry(caption_id):
    """Return True if deleted, False if not found."""
    return _FAKE_CAPTIONS.pop(caption_id, None) is not None


# ---------------------------
# CONNECTION (never used)
# ---------------------------
def get_connection():
    return None
