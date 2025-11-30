"""
DB Stub used ONLY for CI.
This version replaces ALL real DB functions so tests run without Azure SQL.
"""

# ---------------------------
# USER FUNCTIONS (auth.py)
# ---------------------------
def get_user_by_username(username: str):
    """Return a fake user record."""
    return {
        "username": username,
        "hashed_password": "$2b$12$FakeHashedPasswordForTestsOnly",
    }

def create_user(username: str, hashed_password: str):
    """Pretend user was created."""
    return True


# ---------------------------
# CAPTION FUNCTIONS
# ---------------------------
def insert_caption_entry(*args, **kwargs):
    return 123

def fetch_captions():
    return [{"Id": 1}]

def delete_caption_entry(caption_id):
    return True

def fetch_recent_captions():
    return [{"Id": 1}]


# ---------------------------
# CONNECTION (never used)
# ---------------------------
def get_connection():
    return None
