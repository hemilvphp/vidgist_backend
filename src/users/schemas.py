from pydantic import BaseModel

class LoginRequest(BaseModel):
    email:str
    password:str

class SignupReuest(LoginRequest):
    username : str
    
class User(SignupReuest):
    id : str

class UserShow(BaseModel):
    email:str
    username:str
    
    class Config:
        from_attributes=True
    
class Token(BaseModel):
    user:UserShow
    token:str 