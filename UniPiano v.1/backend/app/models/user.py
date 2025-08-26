from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=3, le=18)
    level: UserLevel = UserLevel.BEGINNER

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=3, le=18)
    level: Optional[UserLevel] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    avatar_url: Optional[str] = None
    total_practice_time: int = 0
    lessons_completed: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProgressSummary(BaseModel):
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    total_exercises: int
    completed_exercises: int
    average_score: float
    total_practice_time: int
    current_level: str
