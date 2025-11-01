"""
MongoDB statistics and health check endpoints
"""

from fastapi import APIRouter, HTTPException, status
from app import crud_mongo
from app.database import get_mongo_db, test_mongo_connection

router = APIRouter(
    prefix="/mongo",
    tags=["MongoDB - Statistics"]
)


@router.get("/health")
def mongodb_health_check():
    """
    Check MongoDB connection health
    
    Returns connection status and basic database info
    """
    try:
        if test_mongo_connection():
            db = get_mongo_db()
            collections = db.list_collection_names()
            
            return {
                "status": "healthy",
                "database": db.name,
                "collections": collections,
                "message": "MongoDB connection successful"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MongoDB connection failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"MongoDB health check failed: {str(e)}"
        )


@router.get("/stats")
def get_mongodb_statistics():
    """
    Get MongoDB database statistics
    
    Returns:
    - Collection names
    - Document counts
    - Index information
    """
    try:
        stats = crud_mongo.get_mongo_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get MongoDB stats: {str(e)}"
        )