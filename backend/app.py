from fastapi import FastAPI
from backend.routes.mediverifyRoutes import router
from dotenv import load_dotenv

load_dotenv()

# Make sure docs are enabled
medical = FastAPI(
    title="MediVerify API",
    docs_url="/docs",
    redoc_url="/redoc"
)

medical.include_router(router)