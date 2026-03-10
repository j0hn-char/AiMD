from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Response, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

from src.database import db

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")

# ── Config ────────────────────────────────────────────────────────────────────

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)


def create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def set_auth_cookies(response: Response, user_id: str):
    access_token = create_token(
        {"sub": user_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,        # set False for local dev
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

    return access_token, refresh_token


# ── Controllers ───────────────────────────────────────────────────────────────
async def register(body: RegisterRequest, response: Response):
    # Check if user already exists
    existing = await db["users"].find_one({"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user document
    user = {
        "email": body.email,
        "password": hash_password(body.password),
        "created_at": datetime.now(timezone.utc)
    }

    result = await db["users"].insert_one(user)
    user_id = str(result.inserted_id)

    access_token, _ = set_auth_cookies(response, user_id)

    return {
        "message": "Registered successfully",
        "user": {"id": user_id, "email": body.email},
        "access_token": access_token,
    }


async def login(body: LoginRequest, response: Response):
    # Find user by email
    user = await db["users"].find_one({"email": body.email})

    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user_id = str(user["_id"])
    access_token, _ = set_auth_cookies(response, user_id)

    return {
        "message": "Logged in successfully",
        "user": {"id": user_id, "email": user["email"]},
        "access_token": access_token,
    }


async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}