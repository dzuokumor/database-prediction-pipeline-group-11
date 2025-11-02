"""
Main FastAPI application
Cardiovascular Disease Database API
Supports both SQLite (Relational) and MongoDB (NoSQL) databases
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# SQLite routers
from app.routers import patients, medical_measurements, lifestyle_factors, diagnoses

# MongoDB routers
from app.routers import mongo_patients, mongo_medical_records, mongo_stats

from app.models import HealthCheck
from app.database import (
    test_connection, 
    DATABASE_PATH, 
    test_mongo_connection, 
    close_mongo_connection,
    get_db_connection
)

# Create FastAPI app instance
app = FastAPI(
    title="Cardiovascular Disease API",
    description="RESTful API for managing cardiovascular disease patient data with SQLite and MongoDB support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include SQLite routers
app.include_router(patients.router, prefix="/api/v1")
app.include_router(medical_measurements.router, prefix="/api/v1")
app.include_router(lifestyle_factors.router, prefix="/api/v1")
app.include_router(diagnoses.router, prefix="/api/v1")

# Include MongoDB routers
app.include_router(mongo_patients.router, prefix="/api/v1")
app.include_router(mongo_medical_records.router, prefix="/api/v1")
app.include_router(mongo_stats.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint - Welcome message and API information
    """
    return {
        "message": "Welcome to Cardiovascular Disease API",
        "version": "2.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "databases": {
            "sqlite": "SQLite (Relational Database)",
            "mongodb": "MongoDB (NoSQL Database)"
        },
        "endpoints": {
            "sqlite": {
                "patients": "/api/v1/patients",
                "medical_measurements": "/api/v1/medical-measurements",
                "lifestyle_factors": "/api/v1/lifestyle-factors",
                "diagnoses": "/api/v1/diagnoses"
            },
            "mongodb": {
                "patients": "/api/v1/mongo/patients",
                "medical_records": "/api/v1/mongo/medical-records",
                "health": "/api/v1/mongo/health",
                "stats": "/api/v1/mongo/stats"
            }
        },
        "health_check": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
def health_check():
    """
    Health check endpoint - Verify API and databases status
    """
    try:
        # Test SQLite connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            tables_count = len(tables)
        
        # Test MongoDB connection
        mongo_healthy = False
        try:
            mongo_healthy = test_mongo_connection()
        except:
            mongo_healthy = False
        
        return HealthCheck(
            status="healthy" if mongo_healthy else "partial",
            message=f"API is running. SQLite connected. MongoDB: {'connected' if mongo_healthy else 'disconnected'}",
            database=f"SQLite: {DATABASE_PATH}, MongoDB: cardiovascular_db",
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
    
    # Test SQLite connection
    print("\n📊 Testing SQLite Connection...")
    if test_connection():
        print("✓ SQLite database connection successful")
    else:
        print("✗ SQLite database connection failed")
    
    # Test MongoDB connection
    print("\n📊 Testing MongoDB Connection...")
    try:
        if test_mongo_connection():
            print("✓ MongoDB database connection successful")
        else:
            print("⚠ MongoDB database connection failed (will continue with SQLite only)")
    except Exception as e:
        print(f"⚠ MongoDB not available: {e}")
        print("  API will run with SQLite only")
    
    print(f"\n✓ API Documentation: http://localhost:8000/docs")
    print(f"✓ API Health Check: http://localhost:8000/health")
    print(f"✓ SQLite Endpoints: /api/v1/patients, /api/v1/medical-measurements, etc.")
    print(f"✓ MongoDB Endpoints: /api/v1/mongo/patients, /api/v1/mongo/medical-records")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event - Run when API stops
    """
    print("\n" + "="*60)
    print("🛑 Cardiovascular Disease API Shutting Down...")
    print("="*60)
    
    # Close MongoDB connection
    try:
        close_mongo_connection()
    except:
        pass
    
    print("✓ All connections closed")
    print("="*60 + "\n")


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
