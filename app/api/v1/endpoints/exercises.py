from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
import logging

from app.models.exercise import ExerciseResponse, ExerciseCreate, ExerciseUpdate, ExerciseWithProgress
from app.services.exercise_service import exercise_service
from app.core.dependencies import get_current_user, get_admin_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/lesson/{lesson_id}", response_model=List[ExerciseWithProgress])
async def get_exercises_by_lesson(
    lesson_id: str,
    skip: int = Query(0, ge=0, description="Number of exercises to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of exercises to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get exercises for a specific lesson with user progress"""
    try:
        exercises = await exercise_service.get_exercises_by_lesson(
            lesson_id=lesson_id,
            user_id=current_user["id"],
            skip=skip,
            limit=limit
        )
        return exercises
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching exercises for lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching exercises"
        )

@router.get("/type/{exercise_type}", response_model=List[ExerciseWithProgress])
async def get_exercises_by_type(
    exercise_type: str,
    difficulty: Optional[int] = Query(None, ge=1, le=10, description="Filter by difficulty level"),
    skip: int = Query(0, ge=0, description="Number of exercises to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of exercises to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get exercises by type with optional difficulty filtering"""
    try:
        exercises = await exercise_service.get_exercises_by_type(
            exercise_type=exercise_type,
            user_id=current_user["id"],
            difficulty=difficulty,
            skip=skip,
            limit=limit
        )
        return exercises
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching exercises by type {exercise_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching exercises"
        )

@router.get("/{exercise_id}", response_model=ExerciseWithProgress)
async def get_exercise(
    exercise_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get exercise by ID with user progress"""
    try:
        exercise = await exercise_service.get_exercise_by_id(exercise_id, current_user["id"])
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        return exercise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching exercise"
        )

@router.post("/", response_model=ExerciseResponse)
async def create_exercise(
    exercise_data: ExerciseCreate,
    admin_user: dict = Depends(get_admin_user)
):
    """Create a new exercise (admin only)"""
    try:
        exercise = await exercise_service.create_exercise(exercise_data)
        return exercise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating exercise: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating exercise"
        )

@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: str,
    exercise_update: ExerciseUpdate,
    admin_user: dict = Depends(get_admin_user)
):
    """Update an exercise (admin only)"""
    try:
        exercise = await exercise_service.update_exercise(exercise_id, exercise_update)
        return exercise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating exercise"
        )

@router.delete("/{exercise_id}", response_model=dict)
async def delete_exercise(
    exercise_id: str,
    admin_user: dict = Depends(get_admin_user)
):
    """Delete an exercise (admin only)"""
    try:
        success = await exercise_service.delete_exercise(exercise_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        return {"message": "Exercise deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exercise {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting exercise"
        )
