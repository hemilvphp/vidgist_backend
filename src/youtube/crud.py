from sqlalchemy.orm import Session
from src.youtube import models
from src.youtube.models import TranscriptLog
from fastapi import HTTPException,status
from utils.crud.base import CRUDBase
from typing import Dict

class YtCrud(CRUDBase[TranscriptLog,Dict[str,str],Dict[str,str]]):
    
    def get_by_link(url:str, db:"Session"):
        url_log =  db.query(models.TranscriptLog).filter(models.TranscriptLog.url == url).first()
        return url_log
    
    def get_by_id(id:str, db:"Session"):
        url_log =  db.query(models.TranscriptLog).filter(models.TranscriptLog.id == id).first()
        return url_log
    
    def update_log(url:str, id:str, update_log:dict, db:"Session"):
        db.query(models.TranscriptLog).filter(models.TranscriptLog.id == id, models.TranscriptLog.url == url).update(update_log)
        db.commit()

yt_crud = YtCrud(TranscriptLog)
        
        
    
    