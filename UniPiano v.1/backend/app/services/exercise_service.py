from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import logging

from app.models.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse, ExerciseWithProgress
from app.core.database import get_db

logger = logging.getLogger(__name__)

class ExerciseService:
    def __init__(self):
        self.db = get_db()
    
    async def get_exercises_by_lesson(
        self, 
        lesson_id: str,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExerciseWithProgress]:
        """Get exercises for a specific lesson with optional user progress"""
        try:
            query = self.db.table("exercises").select("*").eq("lesson_id", lesson_id).eq("is_active", True).order("order_index").range(skip, skip + limit - 1)
            
            response = query.execute()
            exercises = response.data or []
            
            # If user_id provided, get progress for each exercise
            if user_id:
                exercises_with_progress = []
                for exercise in exercises:
                    # Get user progress for this exercise
                    progress_response = self.db.table("progress").select("status, score, attempts, best_score, last_practiced").eq("user_id", user_id).eq("exercise_id", exercise["id"]).execute()
                    
                    progress_data = progress_response.data[0] if progress_response.data else None
                    
                    exercise_with_progress = ExerciseWithProgress(
                        **exercise,
                        progress_status=progress_data["status"] if progress_data else "not_started",
                        user_score=progress_data["score"] if progress_data else None,
                        attempts=progress_data["attempts"] if progress_data else 0,
                        best_score=progress_data["best_score"] if progress_data else None,
                        last_practiced=progress_data["last_practiced"] if progress_data else None
                    )
                    exercises_with_progress.append(exercise_with_progress)
                
                return exercises_with_progress
            else:
                return [ExerciseResponse(**exercise) for exercise in exercises]
            
        except Exception as e:
            logger.error(f"Error fetching exercises for lesson {lesson_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching exercises"
            )
    
    async def get_exercise_by_id(self, exercise_id: str, user_id: Optional[str] = None) -> Optional[ExerciseWithProgress]:
        """Get exercise by ID with optional user progress"""
        try:
            response = self.db.table("exercises").select("*").eq("id", exercise_id).eq("is_active", True).execute()
            
            if not response.data:
                return None
            
            exercise = response.data[0]
            
            # Get user progress if user_id provided
            if user_id:
                progress_response = self.db.table("progress").select("status, score, attempts, best_score, last_practiced").eq("user_id", user_id).eq("exercise_id", exercise_id).execute()
                
                progress_data = progress_response.data[0] if progress_response.data else None
                
                return ExerciseWithProgress(
                    **exercise,
                    progress_status=progress_data["status"] if progress_data else "not_started",
                    user_score=progress_data["score"] if progress_data else None,
                    attempts=progress_data["attempts"] if progress_data else 0,
                    best_score=progress_data["best_score"] if progress_data else None,
                    last_practiced=progress_data["last_practiced"] if progress_data else None
                )
            else:
                return ExerciseResponse(**exercise)
            
        except Exception as e:
            logger.error(f"Error fetching exercise {exercise_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching exercise"
            )
    
    async def get_exercises_by_type(
        self, 
        exercise_type: str,
        user_id: Optional[str] = None,
        difficulty: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExerciseWithProgress]:
        """Get exercises by type with optional filtering"""
        try:
            query = self.db.table("exercises").select("*").eq("type", exercise_type).eq("is_active", True)
            
            if difficulty:
                query = query.eq("difficulty", difficulty)
            
            query = query.order("difficulty", "order_index").range(skip, skip + limit - 1)
            
            response = query.execute()
            exercises = response.data or []
            
            # If user_id provided, get progress for each exercise
            if user_id:
                exercises_with_progress = []
                for exercise in exercises:
                    progress_response = self.db.table("progress").select("status, score, attempts, best_score, last_practiced").eq("user_id", user_id).eq("exercise_id", exercise["id"]).execute()
                    
                    progress_data = progress_response.data[0] if progress_response.data else None
                    
                    exercise_with_progress = ExerciseWithProgress(
                        **exercise,
                        progress_status=progress_data["status"] if progress_data else "not_started",
                        user_score=progress_data["score"] if progress_data else None,
                        attempts=progress_data["attempts"] if progress_data else 0,
                        best_score=progress_data["best_score"] if progress_data else None,
                        last_practiced=progress_data["last_practiced"] if progress_data else None
                    )
                    exercises_with_progress.append(exercise_with_progress)
                
                return exercises_with_progress
            else:
                return [ExerciseResponse(**exercise) for exercise in exercises]
            
        except Exception as e:
            logger.error(f"Error fetching exercises by type {exercise_type}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching exercises"
            )
    
    async def create_exercise(self, exercise_data: ExerciseCreate) -> ExerciseResponse:
        """Create a new exercise (admin only)"""
        try:
            exercise_dict = exercise_data.model_dump()
            response = self.db.table("exercises").insert(exercise_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create exercise"
                )
            
            return ExerciseResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating exercise: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating exercise"
            )
    
    async def update_exercise(self, exercise_id: str, exercise_update: ExerciseUpdate) -> ExerciseResponse:
        """Update an exercise (admin only)"""
        try:
            update_data = exercise_update.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No data to update"
                )
            
            response = self.db.table("exercises").update(update_data).eq("id", exercise_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exercise not found"
                )
            
            return ExerciseResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating exercise {exercise_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating exercise"
            )
    
    async def delete_exercise(self, exercise_id: str) -> bool:
        """Delete an exercise (admin only)"""
        try:
            # Soft delete by setting is_active to False
            response = self.db.table("exercises").update({"is_active": False}).eq("id", exercise_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting exercise {exercise_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting exercise"
            )

# Service instance
exercise_service = ExerciseService()
