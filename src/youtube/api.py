from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from src.youtube.utils.summary_transcript.transcript import transcript_process
from src.youtube.utils.summary_transcript.summary import text_summarization
from src.youtube.utils.thumbnail.thumbnail import extract_video_id
from src.youtube.utils.chatbot.chatbot import chatbot_bot
from src.youtube.schemas import ChatReq
from src.youtube.crud import YtCrud as YC
from utils.db.session import get_db
from uuid import uuid4
from typing import Dict,Union
from src.youtube.crud import yt_crud

yt_router = APIRouter()


def process_transcript(session_id: str, url: str, db:"Session"):
    """Background task for generating transcript, summary, and key points"""
    try:
        transcript = transcript_process.Transcript(link=url)  # Generate transcript
        summary,keypoints = text_summarization.Summary_and_keypoints(large_text=transcript)
        
        update_log = {
            "status": "completed",
            "transcript": transcript,
            "summary": summary,
            "keypoints": keypoints
        }
        
        YC.update_log(url=url,id=session_id,update_log=update_log,db=db)
        
    except Exception as e:
        update_log = {
            "status": f"failed: {str(e)}"
        }
        YC.update_log(url=url, id=session_id, update_log=update_log, db=db)


@yt_router.post("/summary")
def get_summary(link:dict, db:get_db, background_tasks:BackgroundTasks):
    url = link["link"]
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    thumbnail_url = f"https://www.youtube.com/embed/{video_id}"
    
    url_log = YC.get_by_link(url=url,db=db)
    
    if (url_log):
        if (url_log.status=="completed"):
            return { "status": url_log.status, 
                    "transcript": url_log.transcript, 
                    "summary": url_log.summary, 
                    "keypoints": url_log.keypoints,
                    "id":url_log.id,
                    "thumb":thumbnail_url}
            
        else:
            return { "message": "Transcript processing started", 
                    "id": session_id,
                    "thumb": thumbnail_url}
    
    else:
        session_id = str(uuid4())
        
        log = {"url":url,"status":"processing","id":session_id}
        new_log = yt_crud.create(obj_in=log, db=db)
        
        background_tasks.add_task(process_transcript, session_id, url, db)
        
        return { "message": "Transcript processing started", 
                "id": new_log.id, 
                "thumb": thumbnail_url 
                }


@yt_router.get("/status/{session_id}")
def get_transcript_status(session_id: str, db:get_db):
    """Check transcript, summary, and key points processing status"""
    url_log = YC.get_by_id(id=session_id, db=db)
    
    if (not url_log):
        raise HTTPException(status_code=404, detail="Session not found")
    else:   
        return {
        "session_id": url_log.id, 
        "status": url_log.status,
        "transcript": url_log.transcript,
        "summary": url_log.summary,
        "keypoints": url_log.keypoints
    }
    
def get_transcript(session_id: str, db:"Session"):
    """Retrieve transcript, summary, and key points after processing is done"""
    url_log = YC.get_by_id(id=session_id, db=db)
    if (not url_log):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if url_log.status == "processing":
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Transcript is still processing")

    if url_log.status.startswith("failed"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=url_log.status)

    return url_log.transcript

@yt_router.post("/chat/{session_id}")
def chatbot(request: ChatReq, session_id:str, db:get_db):
    chat_transcript = get_transcript(session_id=session_id, db=db)
    try:
        ans = chatbot_bot.chatbot_response(user_input=request.que, transcript=chat_transcript)
        return {"answer": ans}
    except :
        raise HTTPException(status_code=503, detail="The server is currently processing. Please try again later.")



 