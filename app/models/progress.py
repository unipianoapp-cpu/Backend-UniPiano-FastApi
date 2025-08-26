from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"

class ProgressBase(BaseModel):
    lesson_id: str
    exercise_id: Optional[str] = None
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    score: Optional[int] = Field(None, ge=0, le=100)
    time_spent: int = Field(default=0, ge=0)  # in seconds
    notes: Optional[str] = None

class ProgressCreate(ProgressBase):
    pass

class ProgressUpdate(BaseModel):
    status: Optional[ProgressStatus] = None
    score: Optional[int] = Field(None, ge=0, le=100)
    time_spent: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class ProgressResponse(ProgressBase):
    id: str
    user_id: str
    attempts: int = 0
    best_score: Optional[int] = None
    last_practiced: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProgressStats(BaseModel):
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    total_exercises: int
    completed_exercises: int
    average_score: float
    total_practice_time: int
    current_level: str
