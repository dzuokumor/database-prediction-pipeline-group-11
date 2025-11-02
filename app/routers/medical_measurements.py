from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models import MedicalMeasurementCreate, MedicalMeasurementUpdate, MedicalMeasurementResponse, MessageResponse
from app import crud

router = APIRouter(
    prefix="/medical-measurements",
    tags=["Medical Measurements"]
)

@router.post("/", response_model=MedicalMeasurementResponse, status_code=status.HTTP_201_CREATED)
def create_medical_measurement(measurement: MedicalMeasurementCreate):
    try:
        patient = crud.get_patient(measurement.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return crud.create_medical_measurement(measurement)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{measurement_id}", response_model=MedicalMeasurementResponse)
def read_medical_measurement(measurement_id: int):
    measurement = crud.get_medical_measurement(measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement

@router.get("/", response_model=List[MedicalMeasurementResponse])
def read_medical_measurements(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return crud.get_medical_measurements(skip=skip, limit=limit)

@router.get("/patient/{patient_id}", response_model=List[MedicalMeasurementResponse])
def read_patient_measurements(patient_id: int):
    patient = crud.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.get_medical_measurements_by_patient(patient_id)

@router.put("/{measurement_id}", response_model=MedicalMeasurementResponse)
def update_medical_measurement(measurement_id: int, measurement: MedicalMeasurementUpdate):
    existing = crud.get_medical_measurement(measurement_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return crud.update_medical_measurement(measurement_id, measurement)

@router.delete("/{measurement_id}", response_model=MessageResponse)
def delete_medical_measurement(measurement_id: int):
    deleted = crud.delete_medical_measurement(measurement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return MessageResponse(message="Measurement deleted successfully")