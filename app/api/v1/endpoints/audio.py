from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.audio import AudioSubmission, AudioAnalysis
from app.services.audio_service import AudioService

router = APIRouter()
audio_service = AudioService()

@router.post("/upload", response_model=dict)
async def upload_audio(
    exercise_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload audio file for analysis"""
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if file.filename else 'mp3'
        filename = f"{current_user['id']}/{exercise_id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to storage and save record
        result = await audio_service.upload_audio_file(
            file=file,
            filename=filename,
            user_id=current_user['id'],
            exercise_id=exercise_id,
            db=db
        )
        
        return {
            "success": True,
            "submission_id": result["submission_id"],
            "message": "Audio uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/{submission_id}", response_model=dict)
async def analyze_audio(
    submission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Analyze uploaded audio submission"""
    try:
        # Verify submission belongs to user
        submission = await audio_service.get_submission(submission_id, db)
        if not submission or submission['user_id'] != current_user['id']:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Perform audio analysis
        analysis_result = await audio_service.analyze_audio(submission_id, db)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "message": "Audio analysis completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submissions", response_model=List[dict])
async def get_user_submissions(
    exercise_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's audio submissions"""
    try:
        submissions = await audio_service.get_user_submissions(
            user_id=current_user['id'],
            exercise_id=exercise_id,
            limit=limit,
            offset=offset,
            db=db
        )
        
        return submissions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/{submission_id}", response_model=dict)
async def get_submission_feedback(
    submission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get detailed feedback for audio submission"""
    try:
        # Verify submission belongs to user
        submission = await audio_service.get_submission(submission_id, db)
        if not submission or submission['user_id'] != current_user['id']:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        feedback = await audio_service.get_detailed_feedback(submission_id, db)
        
        return {
            "success": True,
            "feedback": feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/submissions/{submission_id}", response_model=dict)
async def delete_submission(
    submission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete audio submission"""
    try:
        # Verify submission belongs to user
        submission = await audio_service.get_submission(submission_id, db)
        if not submission or submission['user_id'] != current_user['id']:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        await audio_service.delete_submission(submission_id, db)
        
        return {
            "success": True,
            "message": "Submission deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
