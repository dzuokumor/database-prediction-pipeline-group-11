"""
API Router for logging predictions
"""
from fastapi import APIRouter, HTTPException, status
from app.models import PredictionCreate, PredictionResponse
from app import crud

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
    responses={500: {"description": "Internal server error"}}
)

@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def log_prediction(prediction: PredictionCreate):
    """
    Log a new prediction to the database.
    This endpoint stores the result from the ML model in MongoDB.
    """
    try:
        # The crud function handles all database logic
        new_prediction = crud.create_prediction(prediction)
        return new_prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log prediction: {str(e)}"
        )
