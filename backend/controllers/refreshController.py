from fastapi import HTTPException, Request, Response
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from backend.src.database import users_collection
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def refresh(request: Request, response: Response):
    try:
        # Πάρε το refresh token από τα cookies
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token provided")

        # Decode το refresh token
        try:
            decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid or expired refresh token")

        # Βρες τον user στη MongoDB
        user = await users_collection.find_one({"_id": decoded.get("sub")})
        if not user:
            raise HTTPException(status_code=403, detail="User not found")

        # Φτιάξε νέο access token
        access_token = jwt.encode(
            {
                "sub": str(user["_id"]),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        # Βάλε το νέο access token στο cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        return {"access_token": access_token}

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))