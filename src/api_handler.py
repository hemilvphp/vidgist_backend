from fastapi import APIRouter
from src.users.api import user_router
from src.youtube.api import yt_router

api_router = APIRouter()

api_router.include_router(user_router,include_in_schema=True, tags=["User APIs"])
api_router.include_router(yt_router,include_in_schema=True, tags=["yt APIs"])
