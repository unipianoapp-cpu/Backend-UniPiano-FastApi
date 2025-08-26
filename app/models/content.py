from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    SHEET_MUSIC = "sheet_music"
    IMAGE = "image"
    TEXT = "text"

class ContentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content_type: ContentType
    url: str
    file_size: Optional[int] = Field(None, gt=0)
    duration: Optional[int] = Field(None, gt=0)  # in seconds for audio/video
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    url: Optional[str] = None
    file_size: Optional[int] = Field(None, gt=0)
    duration: Optional[int] = Field(None, gt=0)
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ContentResponse(ContentBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LessonContent(BaseModel):
    lesson_id: str
    content_id: str
    order_index: int = Field(default=0, ge=0)
    is_required: bool = True

class ExerciseContent(BaseModel):
    exercise_id: str
    content_id: str
    content_role: str  # "instruction", "example", "reference", etc.
    order_index: int = Field(default=0, ge=0)
