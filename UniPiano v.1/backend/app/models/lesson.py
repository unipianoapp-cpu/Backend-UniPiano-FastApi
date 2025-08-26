from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.user import UserLevel

class LessonLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    level: LessonLevel
    duration: int = Field(..., gt=0)  # in minutes
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    sheet_music_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    order_index: int = Field(default=0, ge=0)
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    level: Optional[LessonLevel] = None
    duration: Optional[int] = Field(None, gt=0)
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    sheet_music_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    is_active: Optional[bool] = None

class LessonResponse(LessonBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LessonWithProgress(LessonResponse):
    progress_status: Optional[str] = "not_started"
    user_score: Optional[int] = None
    last_practiced: Optional[datetime] = None
