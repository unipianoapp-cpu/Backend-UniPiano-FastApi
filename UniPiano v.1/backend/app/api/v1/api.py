from fastapi import APIRouter
from .endpoints import auth, users, lessons, exercises, progress, audio

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
