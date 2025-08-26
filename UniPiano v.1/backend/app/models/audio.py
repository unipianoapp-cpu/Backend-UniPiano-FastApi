from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"

class AudioSubmissionBase(BaseModel):
    user_id: str
    exercise_id: str
    file_path: str
    status: SubmissionStatus = SubmissionStatus.PENDING

class AudioSubmissionCreate(AudioSubmissionBase):
    pass

class AudioSubmissionUpdate(BaseModel):
    status: Optional[SubmissionStatus] = None
    feedback: Optional[str] = None
    score: Optional[int] = None

class AudioSubmission(AudioSubmissionBase):
    id: str
    feedback: Optional[str] = None
    score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AudioAnalysisResult(BaseModel):
    tempo: Dict[str, Any] = Field(description="Tempo analysis results")
    pitch_accuracy: Dict[str, Any] = Field(description="Pitch accuracy metrics")
    rhythm_accuracy: Dict[str, Any] = Field(description="Rhythm accuracy metrics")
    overall_score: int = Field(ge=0, le=100, description="Overall performance score")
    feedback: str = Field(description="Textual feedback for the user")
    suggestions: List[str] = Field(description="Improvement suggestions")

class AudioAnalysis(BaseModel):
    submission_id: str
    analysis_result: AudioAnalysisResult
    processed_at: datetime

class AudioUploadResponse(BaseModel):
    success: bool
    submission_id: str
    message: str

class AudioAnalysisResponse(BaseModel):
    success: bool
    analysis: AudioAnalysisResult
    message: str

class AudioFeedbackResponse(BaseModel):
    success: bool
    feedback: Dict[str, Any]
    status: str
