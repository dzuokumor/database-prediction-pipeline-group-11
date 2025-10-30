from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models import DiagnosisCreate, DiagnosisUpdate, DiagnosisResponse, MessageResponse
from app import crud

router = APIRouter(
    prefix="/diagnoses",
    tags=["Diagnoses"]
)

@router.post("/", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
def create_diagnosis(diagnosis: DiagnosisCreate):
    try:
        patient = crud.get_patient(diagnosis.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return crud.create_diagnosis(diagnosis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
def read_diagnosis(diagnosis_id: int):
    diagnosis = crud.get_diagnosis(diagnosis_id)
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return diagnosis

@router.get("/", response_model=List[DiagnosisResponse])
def read_all_diagnoses(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return crud.get_all_diagnoses(skip=skip, limit=limit)

@router.get("/patient/{patient_id}", response_model=List[DiagnosisResponse])
def read_patient_diagnoses(patient_id: int):
    patient = crud.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_diagnoses_by_patient(patient_id)

@router.put("/{diagnosis_id}", response_model=DiagnosisResponse)
def update_diagnosis(diagnosis_id: int, diagnosis: DiagnosisUpdate):
    existing = crud.get_diagnosis(diagnosis_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return crud.update_diagnosis(diagnosis_id, diagnosis)

@router.delete("/{diagnosis_id}", response_model=MessageResponse)
def delete_diagnosis(diagnosis_id: int):
    deleted = crud.delete_diagnosis(diagnosis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return MessageResponse(message="Diagnosis deleted successfully")