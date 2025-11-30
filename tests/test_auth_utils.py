from app.utils.auth import create_access_token, get_current_user_from_token
from datetime import timedelta

def test_token_roundtrip():
    token = create_access_token({"sub": "testuser"}, timedelta(hours=1))
    user = get_current_user_from_token(token)
    assert user == "testuser"
