from typing import List, Optional
from fastapi import HTTPException, status
import logging

from app.models.user import UserCreate, UserUpdate, UserResponse, UserProgressSummary
from app.core.database import get_db

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = get_db()
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            response = self.db.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                return UserResponse(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching user"
            )
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserResponse:
        """Update user profile"""
        try:
            # Prepare update data
            update_data = user_update.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No data to update"
                )
            
            # Update user
            response = self.db.table("users").update(update_data).eq("id", user_id).execute()
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return UserResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user"
            )
    
    async def get_user_progress_summary(self, user_id: str) -> UserProgressSummary:
        """Get user progress summary"""
        try:
            # Call the database function
            response = self.db.rpc("get_user_progress_summary", {"user_uuid": user_id}).execute()
            if response.data:
                return UserProgressSummary(**response.data[0])
            
            # Return default if no data
            return UserProgressSummary(
                total_lessons=0,
                completed_lessons=0,
                in_progress_lessons=0,
                total_exercises=0,
                completed_exercises=0,
                average_score=0.0,
                total_practice_time=0,
                current_level="beginner"
            )
            
        except Exception as e:
            logger.error(f"Error fetching progress summary for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching progress summary"
            )
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        try:
            # Delete user data (cascading will handle related records)
            response = self.db.table("users").delete().eq("id", user_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting user"
            )

# Service instance
user_service = UserService()
