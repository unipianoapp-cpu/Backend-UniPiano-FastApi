from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
import logging

from app.models.lesson import LessonResponse, LessonCreate, LessonUpdate, LessonWithProgress
from app.services.lesson_service import lesson_service
from app.core.dependencies import get_current_user, get_admin_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[LessonWithProgress])
async def get_lessons(
    level: Optional[str] = Query(None, description="Filter by level (beginner, intermediate, advanced)"),
    skip: int = Query(0, ge=0, description="Number of lessons to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of lessons to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get lessons with user progress"""
    try:
        lessons = await lesson_service.get_lessons(
            level=level,
            user_id=current_user["id"],
            skip=skip,
            limit=limit
        )
        return lessons
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lessons: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching lessons"
        )

@router.get("/recommended", response_model=List[LessonWithProgress])
async def get_recommended_lessons(current_user: dict = Depends(get_current_user)):
    """Get recommended lessons for current user"""
    try:
        lessons = await lesson_service.get_recommended_lessons(current_user["id"])
        return lessons
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommended lessons: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching recommended lessons"
        )

@router.get("/{lesson_id}", response_model=LessonWithProgress)
async def get_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get lesson by ID with user progress"""
    try:
        lesson = await lesson_service.get_lesson_by_id(lesson_id, current_user["id"])
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return lesson
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching lesson"
        )

@router.post("/", response_model=LessonResponse)
async def create_lesson(
    lesson_data: LessonCreate,
    admin_user: dict = Depends(get_admin_user)
):
    """Create a new lesson (admin only)"""
    try:
        lesson = await lesson_service.create_lesson(lesson_data)
        return lesson
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lesson: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating lesson"
        )

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    admin_user: dict = Depends(get_admin_user)
):
    """Update a lesson (admin only)"""
    try:
        lesson = await lesson_service.update_lesson(lesson_id, lesson_update)
        return lesson
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating lesson"
        )

@router.delete("/{lesson_id}", response_model=dict)
async def delete_lesson(
    lesson_id: str,
    admin_user: dict = Depends(get_admin_user)
):
    """Delete a lesson (admin only)"""
    try:
        success = await lesson_service.delete_lesson(lesson_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return {"message": "Lesson deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting lesson"
        )
