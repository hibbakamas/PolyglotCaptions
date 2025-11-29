from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta
import app.services.passwords as pw
import app.services.jwt_tokens as jwt
from app.db.db import get_user_by_username, create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(req: RegisterRequest):
    existing = get_user_by_username(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = pw.hash_password(req.password)
    create_user(req.username, hashed)
    return {"status": "registered"}


@router.post("/login")
def login(req: LoginRequest):
    user = get_user_by_username(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pw.verify_password(req.password, user["HashedPassword"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.create_access_token({"sub": req.username}, expires=timedelta(hours=1))

    print("Username:", req.username)
    print("User row:", user)


    return {"access_token": token, "token_type": "bearer"}
