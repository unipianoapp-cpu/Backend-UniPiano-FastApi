from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, UploadFile
import logging
import os

from app.models.content import ContentCreate, ContentUpdate, ContentResponse
from app.core.database import get_db
from app.utils.file_utils import save_uploaded_file, delete_file
from app.core.config import settings

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        self.db = get_db()
    
    async def upload_content(
        self, 
        file: UploadFile, 
        content_data: ContentCreate,
        subfolder: str = "content"
    ) -> ContentResponse:
        """Upload and create content"""
        try:
            # Save uploaded file
            file_path = await save_uploaded_file(file, subfolder)
            
            # Update content data with file path
            content_dict = content_data.model_dump()
            content_dict["url"] = file_path
            content_dict["file_size"] = file.size
            
            # Insert into database
            response = self.db.table("content").insert(content_dict).execute()
            
            if not response.data:
                # Clean up uploaded file if database insert fails
                delete_file(file_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create content record"
                )
            
            return ContentResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading content: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading content"
            )
    
    async def get_content_by_id(self, content_id: str) -> Optional[ContentResponse]:
        """Get content by ID"""
        try:
            response = self.db.table("content").select("*").eq("id", content_id).eq("is_active", True).execute()
            
            if not response.data:
                return None
            
            return ContentResponse(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error fetching content {content_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching content"
            )
    
    async def get_lesson_content(self, lesson_id: str) -> List[ContentResponse]:
        """Get all content for a lesson"""
        try:
            # This would require a lesson_content junction table
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            logger.error(f"Error fetching lesson content for {lesson_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching lesson content"
            )
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content and associated file"""
        try:
            # Get content to find file path
            content = await self.get_content_by_id(content_id)
            if not content:
                return False
            
            # Soft delete in database
            response = self.db.table("content").update({"is_active": False}).eq("id", content_id).execute()
            
            # Delete physical file
            if content.url and os.path.exists(content.url):
                delete_file(content.url)
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting content"
            )

# Service instance
content_service = ContentService()
