from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import logging

from app.models.lesson import LessonCreate, LessonUpdate, LessonResponse, LessonWithProgress
from app.core.database import get_db

logger = logging.getLogger(__name__)

class LessonService:
    def __init__(self):
        self.db = get_db()
    
    async def get_lessons(
        self, 
        level: Optional[str] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LessonWithProgress]:
        """Get lessons with optional filtering and user progress"""
        try:
            # Build query
            query = self.db.table("lessons").select("*")
            
            if level:
                query = query.eq("level", level)
            
            query = query.eq("is_active", True).order("order_index").range(skip, skip + limit - 1)
            
            response = query.execute()
            lessons = response.data or []
            
            # If user_id provided, get progress for each lesson
            if user_id:
                lessons_with_progress = []
                for lesson in lessons:
                    # Get user progress for this lesson
                    progress_response = self.db.table("progress").select("status, score, last_practiced").eq("user_id", user_id).eq("lesson_id", lesson["id"]).execute()
                    
                    progress_data = progress_response.data[0] if progress_response.data else None
                    
                    lesson_with_progress = LessonWithProgress(
                        **lesson,
                        progress_status=progress_data["status"] if progress_data else "not_started",
                        user_score=progress_data["score"] if progress_data else None,
                        last_practiced=progress_data["last_practiced"] if progress_data else None
                    )
                    lessons_with_progress.append(lesson_with_progress)
                
                return lessons_with_progress
            else:
                return [LessonResponse(**lesson) for lesson in lessons]
            
        except Exception as e:
            logger.error(f"Error fetching lessons: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching lessons"
            )
    
    async def get_lesson_by_id(self, lesson_id: str, user_id: Optional[str] = None) -> Optional[LessonWithProgress]:
        """Get lesson by ID with optional user progress"""
        try:
            response = self.db.table("lessons").select("*").eq("id", lesson_id).eq("is_active", True).execute()
            
            if not response.data:
                return None
            
            lesson = response.data[0]
            
            # Get user progress if user_id provided
            if user_id:
                progress_response = self.db.table("progress").select("status, score, last_practiced").eq("user_id", user_id).eq("lesson_id", lesson_id).execute()
                
                progress_data = progress_response.data[0] if progress_response.data else None
                
                return LessonWithProgress(
                    **lesson,
                    progress_status=progress_data["status"] if progress_data else "not_started",
                    user_score=progress_data["score"] if progress_data else None,
                    last_practiced=progress_data["last_practiced"] if progress_data else None
                )
            else:
                return LessonResponse(**lesson)
            
        except Exception as e:
            logger.error(f"Error fetching lesson {lesson_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching lesson"
            )
    
    async def get_recommended_lessons(self, user_id: str) -> List[LessonWithProgress]:
        """Get recommended lessons for a user"""
        try:
            # Use the database function
            response = self.db.rpc("get_recommended_lessons", {"user_uuid": user_id}).execute()
            
            if not response.data:
                return []
            
            recommended_lessons = []
            for lesson_data in response.data:
                lesson_with_progress = LessonWithProgress(
                    id=lesson_data["lesson_id"],
                    title=lesson_data["title"],
                    description=lesson_data["description"],
                    level=lesson_data["level"],
                    duration=lesson_data["duration"],
                    progress_status=lesson_data["progress_status"],
                    # Add other fields as needed
                    video_url=None,
                    audio_url=None,
                    sheet_music_url=None,
                    thumbnail_url=None,
                    order_index=0,
                    prerequisites=[],
                    learning_objectives=[],
                    is_active=True,
                    created_at=None,
                    updated_at=None
                )
                recommended_lessons.append(lesson_with_progress)
            
            return recommended_lessons
            
        except Exception as e:
            logger.error(f"Error fetching recommended lessons for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching recommended lessons"
            )
    
    async def create_lesson(self, lesson_data: LessonCreate) -> LessonResponse:
        """Create a new lesson (admin only)"""
        try:
            lesson_dict = lesson_data.model_dump()
            response = self.db.table("lessons").insert(lesson_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create lesson"
                )
            
            return LessonResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating lesson: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating lesson"
            )
    
    async def update_lesson(self, lesson_id: str, lesson_update: LessonUpdate) -> LessonResponse:
        """Update a lesson (admin only)"""
        try:
            update_data = lesson_update.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No data to update"
                )
            
            response = self.db.table("lessons").update(update_data).eq("id", lesson_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson not found"
                )
            
            return LessonResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating lesson {lesson_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating lesson"
            )
    
    async def delete_lesson(self, lesson_id: str) -> bool:
        """Delete a lesson (admin only)"""
        try:
            # Soft delete by setting is_active to False
            response = self.db.table("lessons").update({"is_active": False}).eq("id", lesson_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting lesson {lesson_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting lesson"
            )

# Service instance
lesson_service = LessonService()
