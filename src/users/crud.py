from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from src.users import models
from src.users.models import Hashing, User
from src.users.schemas import SignupReuest,User
import uuid
from utils.crud.base import CRUDBase


class UserCrud():
    
    def get_by_email(email:str, db:"Session") -> User:
        return db.query(models.User).filter(models.User.email==email).first()
    
    def create_user(user_req:SignupReuest, db:"Session") -> User:
        hash_pass = Hashing.get_password_hash(password=user_req.password)
        user_req.password = hash_pass
        
        new_user = models.User(id=str(uuid.uuid4()),**user_req.model_dump())
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Username, password and email can't be empty")
        
        