import motor.motor_asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URL = os.getenv("MONGO_DB_URL")
print(f"DEBUG MongoDB URL: {MONGO_URL}")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[os.getenv("DB_NAME", "mediverify")]

users_collection = db["users"]
sessions_collection = db["sessions"]