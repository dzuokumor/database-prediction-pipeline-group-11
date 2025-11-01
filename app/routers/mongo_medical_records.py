"""
MongoDB CRUD endpoints for medical_records collection
Provides complete CRUD operations on MongoDB medical records
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from app.models_mongo import MedicalRecordMongoCreate, MedicalRecordMongoUpdate, MedicalRecordMongoResponse
from app.models import MessageResponse
from app import crud_mongo

router = APIRouter(
    prefix="/mongo/medical-records",
    tags=["MongoDB - Medical Records"],
    responses={404: {"description": "Medical record not found in MongoDB"}}
)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_medical_record_in_mongodb(record: MedicalRecordMongoCreate):
    """
    Create a new medical record in MongoDB
    
    - **patient_id**: ID of the patient (must exist in patients collection)
    - **measurements**: Blood pressure, cholesterol, glucose levels
    - **diagnosis**: Cardiovascular disease status and date
    """
    try:
        result = crud_mongo.create_medical_record_mongo(record)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{patient_id}", response_model=dict)
def read_medical_record_from_mongodb(patient_id: int):
    """
    Get a medical record from MongoDB by patient_id
    
    - **patient_id**: The patient ID to retrieve medical record for
    """
    record = crud_mongo.get_medical_record_mongo(patient_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical record for patient {patient_id} not found in MongoDB"
        )
    return record


@router.get("/", response_model=List[dict])
def read_medical_records_from_mongodb(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all medical records from MongoDB with pagination
    
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    """
    records = crud_mongo.get_medical_records_mongo(skip=skip, limit=limit)
    return records


@router.put("/{patient_id}", response_model=dict)
def update_medical_record_in_mongodb(patient_id: int, record: MedicalRecordMongoUpdate):
    """
    Update a medical record in MongoDB
    
    - **patient_id**: The patient ID whose medical record to update
    - All fields in request body are optional
    """
    try:
        updated_record = crud_mongo.update_medical_record_mongo(patient_id, record)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical record for patient {patient_id} not found in MongoDB"
            )
        return updated_record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{patient_id}", response_model=dict)
def delete_medical_record_from_mongodb(patient_id: int):
    """
    Delete a medical record from MongoDB
    
    - **patient_id**: The patient ID whose medical record to delete
    """
    deleted = crud_mongo.delete_medical_record_mongo(patient_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical record for patient {patient_id} not found in MongoDB"
        )
    
    return {
        "message": "Medical record deleted from MongoDB successfully",
        "patient_id": patient_id
    }


@router.get("/search/by-disease", response_model=List[dict])
def search_by_disease_status(
    has_disease: bool = Query(..., description="True for patients with disease, False for without"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Search medical records by cardiovascular disease status
    
    - **has_disease**: Filter by disease presence (true/false)
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    """
    records = crud_mongo.search_patients_by_disease_mongo(has_disease, skip, limit)
    return records


@router.get("/count/total", response_model=dict)
def get_total_records_count_mongodb():
    """Get total count of medical records in MongoDB"""
    count = crud_mongo.get_medical_records_count_mongo()
    return {"total_records": count, "database": "MongoDB"}