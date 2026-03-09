from fastapi import Form, File, UploadFile, HTTPException, Depends
from typing import Optional
import os
from file_processor import process_file
from chatbotCall import chatbotGPT, chatbotClaude

memory = {
    "history": [],
    "analysis": None,
    "mode": "chat"
} 

async def chat(msg: str = Form(default=""),mode: str = Form(),file:Optional[UploadFile]=File(None)):
    memory["mode"] = mode 

    #ANALYSIS MODE
    if mode == "analysis":
        if file:
            contents = await file.read()
            file_data = process_file(contents, file.filename);
            if file_data["type"] == "error":
                return{
                    "reply": f"{file_data['data']}",
                    "mode":mode
                }
        #ANALYSH ME AI -> PERNAS TO FILE_DATA 
        #REPLY



        elif msg:
            if not memory["analysis"]:
                reply = "Ανέβασε πρώτα ένα αρχείο για ανάλυση!"
            else:
                memory["history"].append({"role":"user","content":"message"})
                reply = await chatbotGPT(memory["history"],memory["analysis"]) #PREPEI NA DOUME TA ARGUMENTS POY THA DEXETAI TO LLM
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
