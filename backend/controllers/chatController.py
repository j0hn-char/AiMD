from fastapi import HTTPException, Request,status
from src.sessionStorage import get_session,update_mode_history,set_analysis_result

from llm.askAI import callGPT,responseComparison,finalizeResponse
from llm.pubMedSearch import get_top_papers

SYSTEM_CHAT = {
    "role": "system",
    "content": (
        "You are a helpful and empathetic medical assistant. "
        "Answer the user's questions clearly and ask clarifying questions when needed."
        "Answer question ONLY regarding medical interest"
    ),
}

SYSTEM_ANALYSIS = {
    "role": "system",
    "content": (
        "You are a highly experienced medical assistant. "
        "Analyze the provided medical information carefully and provide "
        "a clear, professional diagnosis with recommendations."
    ),
}


#NA PAEI STO SESSION STORAGE KAPOIA STIGMH (GIA XARH OMOIOMORFIAS)
async def _get_authorized_session(session_id: str, user: dict) -> dict:
    session = await get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return session

def _build_conversation(history:list[dict],system_msg:dict) -> list[dict]:
    conversation = [system_msg]
    for msg in history: 
        conversation.append({"role":msg["role"],"content":msg["content"]})
    return conversation

async def chat_route(request: Request, user:dict):
    body = await request.json()
    session_id = body.get("session_id")
    user_message= body.get("message","").strip()

    #1
    if not session_id or not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id and message are required"
        )
    
    #2
    session = await _get_authorized_session(session_id,user)

    #3
    user_msg = {"role":"user","content":user_message}
    await update_mode_history(session_id,"chat",user_msg)

    #4
    history = session["conversations"]["chat"]["history"] #AUTH H SYGKEKRIMENH GRAMMH MPAINEI MESA TRIA EPIPEDA STO PYTHON DICTIONARY POY EXOUME KANEI STO BHMA 2 KAI PAIRNEI TO HISTORY APO TO DICTIONARY DHLADH TO ISTORIKO MHNYMATWN 
    conversation = _build_conversation(history,SYSTEM_CHAT)
    conversation.append({"role":"user","content":user_message})
    reply = callGPT(conversation)

    #5 
    assistant_msg = {"role":"assistant","content":reply}
    await update_mode_history(session_id,"chat",assistant_msg)
    return {"reply":reply,"mode":"chat"}


async def analysis_route(request: Request, user:dict):
    body = await request.json()
    session_id = body.get("session_id")
    user_message = body.get("message","").strip()
    filename = body.get("filename", "user_input")
    
    #1
    if not session_id or not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id and message are required"
        )
    #2
    session = await _get_authorized_session

    #3 
    user_msg = {"role":"user","content":user_message}
    await update_mode_history(session_id,"analysis",user_msg)

    #4 
    history = session["conversations"]["chat"]["history"]

    
