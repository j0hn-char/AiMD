from fastapi import HTTPException, Depends, Request
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"


def verify_jwt(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="No token provided")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = auth_header.split(" ")[1]
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")