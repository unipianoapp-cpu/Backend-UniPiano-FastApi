import os
import uuid
import librosa
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import UploadFile
import tempfile
import asyncio

from app.core.database import get_db
from app.core.config import settings

class AudioService:
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        
    async def upload_audio_file(
        self, 
        file: UploadFile, 
        filename: str, 
        user_id: str, 
        exercise_id: str, 
        db
    ) -> Dict[str, Any]:
        """Upload audio file and create submission record"""
        try:
            # Save file temporarily for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Create submission record
            submission_id = str(uuid.uuid4())
            
            # Insert into database
            query = """
                INSERT INTO audio_submissions (id, user_id, exercise_id, file_path, status, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """
            
            result = await db.fetchrow(
                query,
                submission_id,
                user_id,
                exercise_id,
                filename,
                'pending',
                datetime.utcnow()
            )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return {
                "submission_id": submission_id,
                "filename": filename,
                "status": "uploaded"
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload audio: {str(e)}")
    
    async def analyze_audio(self, submission_id: str, db) -> Dict[str, Any]:
        """Analyze audio submission for piano performance"""
        try:
            # Get submission details
            submission = await self.get_submission(submission_id, db)
            if not submission:
                raise Exception("Submission not found")
            
            # For now, return mock analysis - in production, implement actual audio analysis
            analysis_result = {
                "tempo": {
                    "detected": 120,
                    "target": 120,
                    "accuracy": 95
                },
                "pitch_accuracy": {
                    "correct_notes": 85,
                    "total_notes": 100,
                    "accuracy_percentage": 85
                },
                "rhythm_accuracy": {
                    "timing_score": 88,
                    "consistency": 92
                },
                "overall_score": 87,
                "feedback": "Great job! Your timing is excellent. Focus on hitting the correct notes more consistently.",
                "suggestions": [
                    "Practice scales to improve finger positioning",
                    "Use a metronome to maintain steady tempo",
                    "Focus on the middle section where most errors occurred"
                ]
            }
            
            # Update submission with analysis results
            update_query = """
                UPDATE audio_submissions 
                SET status = $1, feedback = $2, score = $3, updated_at = $4
                WHERE id = $5
            """
            
            await db.execute(
                update_query,
                'analyzed',
                str(analysis_result),
                analysis_result['overall_score'],
                datetime.utcnow(),
                submission_id
            )
            
            return analysis_result
            
        except Exception as e:
            # Update submission status to failed
            await db.execute(
                "UPDATE audio_submissions SET status = $1, updated_at = $2 WHERE id = $3",
                'failed',
                datetime.utcnow(),
                submission_id
            )
            raise Exception(f"Failed to analyze audio: {str(e)}")
    
    async def get_submission(self, submission_id: str, db) -> Optional[Dict[str, Any]]:
        """Get audio submission by ID"""
        try:
            query = """
                SELECT * FROM audio_submissions WHERE id = $1
            """
            result = await db.fetchrow(query, submission_id)
            return dict(result) if result else None
            
        except Exception as e:
            raise Exception(f"Failed to get submission: {str(e)}")
    
    async def get_user_submissions(
        self, 
        user_id: str, 
        exercise_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        db = None
    ) -> List[Dict[str, Any]]:
        """Get user's audio submissions"""
        try:
            query = """
                SELECT a.*, e.title as exercise_title, e.type as exercise_type
                FROM audio_submissions a
                LEFT JOIN exercises e ON a.exercise_id = e.id
                WHERE a.user_id = $1
            """
            params = [user_id]
            
            if exercise_id:
                query += " AND a.exercise_id = $2"
                params.append(exercise_id)
                query += " ORDER BY a.created_at DESC LIMIT $3 OFFSET $4"
                params.extend([limit, offset])
            else:
                query += " ORDER BY a.created_at DESC LIMIT $2 OFFSET $3"
                params.extend([limit, offset])
            
            results = await db.fetch(query, *params)
            return [dict(row) for row in results]
            
        except Exception as e:
            raise Exception(f"Failed to get user submissions: {str(e)}")
    
    async def get_detailed_feedback(self, submission_id: str, db) -> Dict[str, Any]:
        """Get detailed feedback for submission"""
        try:
            submission = await self.get_submission(submission_id, db)
            if not submission:
                raise Exception("Submission not found")
            
            if submission['status'] != 'analyzed':
                return {
                    "status": submission['status'],
                    "message": "Analysis not yet complete"
                }
            
            # Parse feedback JSON
            import json
            feedback = json.loads(submission['feedback']) if submission['feedback'] else {}
            
            return {
                "status": "analyzed",
                "score": submission['score'],
                "analysis": feedback,
                "created_at": submission['created_at'],
                "updated_at": submission['updated_at']
            }
            
        except Exception as e:
            raise Exception(f"Failed to get feedback: {str(e)}")
    
    async def delete_submission(self, submission_id: str, db):
        """Delete audio submission and file"""
        try:
            # Get submission to get file path
            submission = await self.get_submission(submission_id, db)
            if not submission:
                raise Exception("Submission not found")
            
            # Delete file from storage
            if submission['file_path']:
                await supabase.storage.from('audio-submissions').remove([submission['file_path']])
            
            # Delete database record
            await db.execute("DELETE FROM audio_submissions WHERE id = $1", submission_id)
            
        except Exception as e:
            raise Exception(f"Failed to delete submission: {str(e)}")

# Export singleton instance
audio_service = AudioService()
