from fastapi import Form, File, UploadFile, HTTPException, Depends
from typing import Optional
import os
from file_processor import process_file
from llm.askGPT import callGPT,responseComparison,finalizeResponse

async def chat(msg: str = Form(default=""),mode: str = Form(),file:Optional[UploadFile]=File(None))
