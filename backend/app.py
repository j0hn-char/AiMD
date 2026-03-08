from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import os
from file_processor import process_file

load_dotenv()

medical = FastAPI()

memory = {
    "history": [],
    "analysis": None,
    "mode": "chat"
} 

@medical.post("/chat")
def chat(msg: str = Form(default=""),mode: str = Form()):
    memory["mode"] = mode 
    if mode == "analysis":
        