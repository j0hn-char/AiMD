from fastapi import FastAPI
from fastapi.security import HTTPBearer
from backend.routes.mediverifyRoutes import router
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

medical = FastAPI(
    title="MediVerify API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Αυτό προσθέτει το κουμπί "Authorize" στο Swagger UI
security = HTTPBearer()

medical.include_router(router, prefix="/api")