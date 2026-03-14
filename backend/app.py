from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from routes.mediverifyRoutes import router
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

medical = FastAPI(
    title="MediVerify API",
    docs_url="/docs",
    redoc_url="/redoc"
)

security = HTTPBearer()

medical.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

medical.include_router(router, prefix="/api")