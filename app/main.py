"""
Main FastAPI application
Cardiovascular Disease Database API
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

from app.routers import patients, medical_measurements, lifestyle_factors, diagnoses
from app.models import HealthCheck
from app.database import test_connection, DATABASE_PATH

# Create FastAPI app instance
app = FastAPI(
    title="Cardiovascular Disease API",
    description="RESTful API for managing cardiovascular disease patient data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/v1")
app.include_router(medical_measurements.router, prefix="/api/v1")
app.include_router(lifestyle_factors.router, prefix="/api/v1")
app.include_router(diagnoses.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint - Welcome message and API information
    """
    return {
        "message": "Welcome to Cardiovascular Disease API",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "patients": "/api/v1/patients",
            "medical_measurements": "/api/v1/medical-measurements",
            "lifestyle_factors": "/api/v1/lifestyle-factors",
            "diagnoses": "/api/v1/diagnoses"
        },
        "health_check": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
def health_check():
    """
    Health check endpoint - Verify API and database status
    """
    try:
        # Test database connection
        from app.database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            tables_count = len(tables)
        
        return HealthCheck(
            status="healthy",
            message="API is running and database is connected",
            database=DATABASE_PATH,
            tables_count=tables_count
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "database": DATABASE_PATH,
                "tables_count": 0
            }
        )


@app.on_event("startup")
async def startup_event():
    """
    Startup event - Run when API starts
    """
    print("\n" + "="*60)
    print("🚀 Cardiovascular Disease API Starting...")
    print("="*60)
    
    # Test database connection
    if test_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
    
    print(f"✓ API Documentation: http://localhost:8000/docs")
    print(f"✓ API Health Check: http://localhost:8000/health")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event - Run when API stops
    """
    print("\n" + "="*60)
    print("🛑 Cardiovascular Disease API Shutting Down...")
    print("="*60 + "\n")


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )