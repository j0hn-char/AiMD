from fastapi import HTTPException, Form
from src.database import users_collection
from auth import hash_password
import uuid


async def register(
    username: str = Form(...),
    password: str = Form(...)
):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    try:
        existing = await users_collection.find_one({"username": username})
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists")

        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)

        await users_collection.insert_one({
            "user_id": user_id,
            "username": username,
            "password": hashed_pwd
        })

        return {"message": "User registered successfully", "userId": user_id}

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))