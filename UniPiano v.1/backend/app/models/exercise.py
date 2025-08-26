from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ExerciseType(str, Enum):
    RHYTHM = "rhythm"
    MELODY = "melody"
    CHORD = "chord"
    SCALE = "scale"
    TECHNIQUE = "technique"
    THEORY = "theory"

class ExerciseBase(BaseModel):
    lesson_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    type: ExerciseType
    difficulty: int = Field(..., ge=1, le=10)
    audio_url: Optional[str] = None
    sheet_music_url: Optional[str] = None
    expected_notes: Optional[List[str]] = Field(default_factory=list)
    tempo: Optional[int] = Field(None, gt=0)  # BPM
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    instructions: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    order_index: int = Field(default=0, ge=0)

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    type: Optional[ExerciseType] = None
    difficulty: Optional[int] = Field(None, ge=1, le=10)
    audio_url: Optional[str] = None
    sheet_music_url: Optional[str] = None
    expected_notes: Optional[List[str]] = None
    tempo: Optional[int] = Field(None, gt=0)
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    instructions: Optional[str] = None
    hints: Optional[List[str]] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class ExerciseResponse(ExerciseBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExerciseWithProgress(ExerciseResponse):
    progress_status: Optional[str] = "not_started"
    user_score: Optional[int] = None
    attempts: int = 0
    best_score: Optional[int] = None
    last_practiced: Optional[datetime] = None
