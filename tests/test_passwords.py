from app.services.passwords import hash_password, verify_password


def test_hash_password_produces_different_output():
    h1 = hash_password("hello")
    h2 = hash_password("hello")
    assert h1 != h2


def test_verify_password_works():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True
    assert verify_password("wrong", hashed) is False
