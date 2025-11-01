"""
MongoDB CRUD endpoints for patients collection
Provides complete CRUD operations on MongoDB patients
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models_mongo import PatientMongoCreate, PatientMongoUpdate, PatientMongoResponse
from app.models import MessageResponse
from app import crud_mongo

router = APIRouter(
    prefix="/mongo/patients",
    tags=["MongoDB - Patients"],
    responses={404: {"description": "Patient not found in MongoDB"}}
)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_patient_in_mongodb(patient: PatientMongoCreate):
    """
    Create a new patient in MongoDB
    
    - **patient_id**: Unique patient identifier
    - **demographics**: Nested document with age, gender, height, weight, BMI
    - **lifestyle**: Nested document with smoker, alcohol, physical activity status
    """
    try:
        result = crud_mongo.create_patient_mongo(patient)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{patient_id}", response_model=dict)
def read_patient_from_mongodb(patient_id: int):
    """
    Get a patient from MongoDB by patient_id
    
    - **patient_id**: The ID of the patient to retrieve
    """
    patient = crud_mongo.get_patient_mongo(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found in MongoDB"
        )
    return patient


@router.get("/", response_model=List[dict])
def read_patients_from_mongodb(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of documents to return")
):
    """
    Get all patients from MongoDB with pagination
    
    - **skip**: Number of documents to skip (for pagination)
    - **limit**: Maximum number of documents to return (max 1000)
    """
    patients = crud_mongo.get_patients_mongo(skip=skip, limit=limit)
    return patients


@router.put("/{patient_id}", response_model=dict)
def update_patient_in_mongodb(patient_id: int, patient: PatientMongoUpdate):
    """
    Update a patient in MongoDB
    
    - **patient_id**: The ID of the patient to update
    - All fields in request body are optional
    - Only provided fields will be updated
    """
    try:
        updated_patient = crud_mongo.update_patient_mongo(patient_id, patient)
        if not updated_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found in MongoDB"
            )
        return updated_patient
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{patient_id}", response_model=dict)
def delete_patient_from_mongodb(patient_id: int):
    """
    Delete a patient from MongoDB
    
    - **patient_id**: The ID of the patient to delete
    """
    deleted = crud_mongo.delete_patient_mongo(patient_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found in MongoDB"
        )
    
    return {
        "message": "Patient deleted from MongoDB successfully",
        "patient_id": patient_id
    }


@router.get("/count/total", response_model=dict)
def get_total_patients_count_mongodb():
    """Get total count of patients in MongoDB"""
    count = crud_mongo.get_patients_count_mongo()
    return {"total_patients": count, "database": "MongoDB"}