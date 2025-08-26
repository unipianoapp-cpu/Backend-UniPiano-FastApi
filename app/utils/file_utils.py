import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
import magic
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def validate_audio_file(file: UploadFile) -> bool:
    """Validate audio file type and size"""
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_AUDIO_EXTENSIONS:
        return False
    
    # Check file size
    if file.size > settings.MAX_FILE_SIZE:
        return False
    
    return True

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    file_extension = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

async def save_uploaded_file(file: UploadFile, subfolder: str = "") -> str:
    """Save uploaded file and return file path"""
    try:
        # Validate file
        if not validate_audio_file(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type or size"
            )
        
        # Create upload directory
        upload_path = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved: {file_path}")
        return file_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file"
        )

def delete_file(file_path: str) -> bool:
    """Delete file from filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False
