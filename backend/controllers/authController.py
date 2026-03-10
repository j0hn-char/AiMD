from datetime import datetime, timedelta,timezone
from typing import Optional

from fastapi import HTTPException, Response, Request, status
from sqlmodel import Session, select
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from models.userModel import User
from database import get_session

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY = "your-secret-key-change-in-production"  # move to .env
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
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def set_auth_cookies(response: Response, user_id: int):
    access_token = create_token(
        {"sub": str(user_id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,        # HTTPS only — set False for local dev
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
def register(body: RegisterRequest, response: Response, db: Session):
    # Check if user already exists
    existing = db.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=body.email,
        password=hash_password(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Set cookies + return tokens
    access_token, refresh_token = set_auth_cookies(response, user.id)

    return {
        "message": "Registered successfully",
        "user": {"id": user.id, "email": user.email},
        "access_token": access_token,   # also in cookie
    }


def login(body: LoginRequest, response: Response, db: Session):
    user = db.exec(select(User).where(User.email == body.email)).first() 

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token, refresh_token = set_auth_cookies(response, user.id)

    return {
        "message": "Logged in successfully",
        "user": {"id": user.id, "email": user.email},
        "access_token": access_token,
    }


def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}