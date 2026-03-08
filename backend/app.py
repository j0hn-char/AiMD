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
async def chat(msg: str = Form(default=""),mode: str = Form(),file:Optional[UploadFile]=File(None)):
    memory["mode"] = mode 

    #ANALYSIS MODE
    if mode == "analysis":
        if file:

        elif msg:
            if not memory["analysis"]:
            
            else:
            
        else:
            reply = "Analysis Mode — ανέβασε ένα PDF ή εικόνα!"
    
    else: 
        if not message:

        else:

    
    return {
        "reply": reply,
        "mode":mode,
        "analysis":memory.get("analysis")
    }

        
    