"""
API Router for Patient endpoints
Handles all CRUD operations for patients
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models import PatientCreate, PatientUpdate, PatientResponse, MessageResponse
from app import crud

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    responses={404: {"description": "Patient not found"}}
)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate):
    """
    Create a new patient
    
    - **patient_id**: Unique patient identifier
    - **age_days**: Age in days (will auto-calculate age_years)
    - **gender**: 1=Female, 2=Male
    - **height**: Height in cm
    - **weight**: Weight in kg (will auto-calculate BMI)
    """
    try:
        # Check if patient already exists
        existing = crud.get_patient(patient.patient_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient with ID {patient.patient_id} already exists"
            )
        
        result = crud.create_patient(patient)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: int):
    """
    Get a patient by ID
    
    - **patient_id**: The ID of the patient to retrieve
    """
    patient = crud.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return patient


@router.get("/", response_model=List[PatientResponse])
def read_patients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """
    Get all patients with pagination
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 1000)
    """
    patients = crud.get_patients(skip=skip, limit=limit)
    return patients


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient: PatientUpdate):
    """
    Update a patient
    
    - **patient_id**: The ID of the patient to update
    - All fields in request body are optional
    - Will auto-recalculate age_years and BMI if relevant fields are updated
    """
    # Check if patient exists
    existing = crud.get_patient(patient_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    try:
        updated_patient = crud.update_patient(patient_id, patient)
        return updated_patient
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update patient: {str(e)}"
        )


@router.delete("/{patient_id}", response_model=MessageResponse)
def delete_patient(patient_id: int):
    """
    Delete a patient
    
    - **patient_id**: The ID of the patient to delete
    - Warning: This will CASCADE delete all related records (measurements, lifestyle, diagnoses)
    """
    deleted = crud.delete_patient(patient_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    return MessageResponse(
        message="Patient deleted successfully",
        detail=f"Patient {patient_id} and all related records have been deleted"
    )