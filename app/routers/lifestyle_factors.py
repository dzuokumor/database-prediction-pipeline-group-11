from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models import LifestyleFactorsCreate, LifestyleFactorsUpdate, LifestyleFactorsResponse, MessageResponse
from app import crud

router = APIRouter(
    prefix="/lifestyle-factors",
    tags=["Lifestyle Factors"]
)

@router.post("/", response_model=LifestyleFactorsResponse, status_code=status.HTTP_201_CREATED)
def create_lifestyle_factors(lifestyle: LifestyleFactorsCreate):
    try:
        patient = crud.get_patient(lifestyle.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return crud.create_lifestyle_factors(lifestyle)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lifestyle_id}", response_model=LifestyleFactorsResponse)
def read_lifestyle_factors(lifestyle_id: int):
    lifestyle = crud.get_lifestyle_factors(lifestyle_id)
    if not lifestyle:
        raise HTTPException(status_code=404, detail="Lifestyle factors not found")
    return lifestyle

@router.get("/", response_model=List[LifestyleFactorsResponse])
def read_all_lifestyle_factors(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return crud.get_all_lifestyle_factors(skip=skip, limit=limit)

@router.get("/patient/{patient_id}", response_model=List[LifestyleFactorsResponse])
def read_patient_lifestyle(patient_id: int):
    patient = crud.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_lifestyle_factors_by_patient(patient_id)

@router.put("/{lifestyle_id}", response_model=LifestyleFactorsResponse)
def update_lifestyle_factors(lifestyle_id: int, lifestyle: LifestyleFactorsUpdate):
    existing = crud.get_lifestyle_factors(lifestyle_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Lifestyle factors not found")
    return crud.update_lifestyle_factors(lifestyle_id, lifestyle)

@router.delete("/{lifestyle_id}", response_model=MessageResponse)
def delete_lifestyle_factors(lifestyle_id: int):
    deleted = crud.delete_lifestyle_factors(lifestyle_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lifestyle factors not found")
    return MessageResponse(message="Lifestyle factors deleted successfully")