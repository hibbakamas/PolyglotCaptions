from datetime import datetime, timedelta

import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
