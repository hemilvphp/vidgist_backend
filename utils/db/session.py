from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import ProgrammingError
from fastapi import Depends
from typing import Annotated
from src.config import Config

engine = create_engine(Config.postgres_path())

SessionLocal = sessionmaker(autoflush=False,autocommit=False, bind=engine)


def _get_db():
    try:
        db = SessionLocal()
        yield db
    
    except ProgrammingError as pro:
        print("##############################################")
        print("EITHER DATABASE NOT FOUND OR NOT TABLES EXIST")
        print("##############################################")
        return pro
    
    finally:
        db.close()
        
get_db = Annotated[Session, Depends(_get_db)]