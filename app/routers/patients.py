from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models import PatientCreate, PatientUpdate, PatientResponse, MessageResponse
from app import crud

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate):
    try:
        existing = crud.get_patient(patient.patient_id)
        if existing:
            raise HTTPException(status_code=400, detail=f"Patient {patient.patient_id} already exists")
        return crud.create_patient(patient)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: int):
    patient = crud.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/", response_model=List[PatientResponse])
def read_patients(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return crud.get_patients(skip=skip, limit=limit)

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientUpdate):
    existing = crud.get_patient(patient_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.update_patient(patient_id, patient)

@router.delete("/{patient_id}", response_model=MessageResponse)
def delete_patient(patient_id: int):
    deleted = crud.delete_patient(patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return MessageResponse(message="Patient deleted successfully")