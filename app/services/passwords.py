import bcrypt


def hash_password(raw: str) -> str:
    raw_bytes = raw.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    raw_bytes = raw.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(raw_bytes, hashed_bytes)
