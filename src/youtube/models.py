from sqlalchemy import Column, String, Boolean, Text
from utils.db.base import Base

class TranscriptLog(Base):
    url = Column(String, unique=True,nullable=True, index=True)
    transcript=Column(Text,nullable=True)
    summary = Column(Text,nullable=True)
    keypoints = Column(Text, nullable=True)
    status = Column(String,nullable=True)
    