from fastapi import FastAPI
from routes.mediverifyRoutes import router
from dotenv import load_dotenv
from file_processor import process_file

load_dotenv()

medical = FastAPI()
medical.include_router(router)


        
    