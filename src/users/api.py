from fastapi import Depends, HTTPException, status, APIRouter
from src.users.schemas import SignupReuest, LoginRequest, Token, UserShow
from utils.db.session import get_db
from src.users.crud import UserCrud as UC
from src.users.models import Hashing
from src.users.utils.deps import get_current_user
from datetime import datetime, timezone, timedelta

user_router = APIRouter()

@user_router.post("/signup", response_model=Token)
def signup(user_req: SignupReuest, db: get_db):
    if UC.get_by_email(email=user_req.email, db=db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User with this email already exists")
    
    user = UC.create_user(user_req=user_req, db=db)
    
    return Token(user=UserShow.model_validate(user),token=Hashing.create_token(user=user))

@user_router.post("/login", response_model=Token)
def login(user_req:LoginRequest, db:get_db):
    user = UC.get_by_email(email=user_req.email, db=db)
    
    if not user or (
        not Hashing.verify_password(plain_password=user_req.password, hashed_password=user.password)
        ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    
    return Token(user=UserShow.model_validate(user),token=Hashing.create_token(user=user))
    

@user_router.post("/validate-token")
def validate_token(user:dict, token_email:str=Depends(get_current_user)):
    print(datetime.now(timezone.utc))
    if(user["email"]==token_email):
        return {"message":True}
    else:
        return {"message":False}
    