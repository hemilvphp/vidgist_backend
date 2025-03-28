from fastapi import Header, HTTPException, Depends,status
from src.users.models import Hashing

def get_current_user(authorization: str=Header(None,alias="Authorization")):
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = authorization.split(" ")[1]  # Extract token
    payload = Hashing.decode_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload["email"]