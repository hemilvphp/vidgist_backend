from sqlalchemy import Column, String, CheckConstraint
from utils.db.base import Base
from passlib.context import CryptContext
from src.config import Config
from fastapi import HTTPException,status
import jwt
from datetime import datetime, timezone, timedelta

class User(Base):
    email = Column(String, unique=True, index=True,nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, index=True,nullable=False)
    refresh_token = Column(String, nullable=True)
    
    __table_args__ = (
        CheckConstraint("length(email) > 0", name="email_not_empty"),  # Prevent empty strings
        CheckConstraint("length(password) > 0", name="password_not_empty"),
        CheckConstraint("length(password) > 0", name="username_not_empty")
    )
    
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

class Hashing:
    def get_password_hash(password):
        return pwd_context.hash(password)
    
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    
    def create_token(user:User):
        data={"id":user.id,
              "email":user.email,
              "username":user.username}
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(Config.JWT_EXPIRATION_TIME))
        print(datetime.now(timezone.utc))
        print(expire)
        
        data.update({"exp":expire})
        
        return jwt.encode(data,key=Config.JWT_SECRET_KEY,algorithm=Config.JWT_ALGORITHM)
    
    def decode_jwt_token(token: str):
        try:
            payload = jwt.decode(token, key=Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Token expired")  # Token expired
        except jwt.InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")  # Invalid token
    