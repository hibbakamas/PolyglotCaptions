# app/routers/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import timedelta
import app.services.passwords as pw
from app.db.db import get_user_by_username, create_user
from app.utils.auth import create_access_token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(req: RegisterRequest):
    if get_user_by_username(req.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = pw.hash_password(req.password)
    create_user(req.username, hashed)
    return {"status": "registered"}

@router.post("/login")
def login(req: LoginRequest):
    user = get_user_by_username(req.username)
    if not user or not pw.verify_password(req.password, user["HashedPassword"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": req.username}, expires_delta=timedelta(hours=1))
    return {"access_token": token, "token_type": "bearer"}
