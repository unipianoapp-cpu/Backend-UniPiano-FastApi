from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Supabase client instance
supabase: Client = None

async def init_db():
    """Initialize database connection"""
    global supabase
    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def get_db() -> Client:
    """Get database client"""
    if supabase is None:
        raise Exception("Database not initialized")
    return supabase

async def close_db():
    """Close database connection"""
    global supabase
    if supabase:
        # Supabase client doesn't need explicit closing
        supabase = None
        logger.info("Database connection closed")
