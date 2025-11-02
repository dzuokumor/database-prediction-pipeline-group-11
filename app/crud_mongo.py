"""
Complete CRUD operations for MongoDB collections
Matches Task 1 MongoDB schema structure
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_mongo_db
from app.models_mongo import (
    PatientMongoCreate, PatientMongoUpdate,
    MedicalRecordMongoCreate, MedicalRecordMongoUpdate
)


# ============= HELPER FUNCTIONS =============

def serialize_mongo_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def prepare_patient_document(patient: PatientMongoCreate) -> dict:
    """Prepare patient document for MongoDB insertion"""
    return {
        "patient_id": patient.patient_id,
        "demographics": patient.demographics.model_dump(),
        "lifestyle": patient.lifestyle.model_dump(),
        "created_at": datetime.now().isoformat()
    }


def prepare_medical_record_document(record: MedicalRecordMongoCreate) -> dict:
    """Prepare medical record document for MongoDB insertion"""
    return {
        "patient_id": record.patient_id,
        "measurements": record.measurements.model_dump(),
        "diagnosis": record.diagnosis.model_dump(),
        "recorded_at": datetime.now().isoformat()
    }


# ============= PATIENT CRUD (MongoDB) =============

def create_patient_mongo(patient: PatientMongoCreate) -> dict:
    """
    Create patient in MongoDB patients collection
    
    Args:
        patient: PatientMongoCreate model
    
    Returns:
        Created patient document
    """
    db = get_mongo_db()
    
    # Check if patient already exists
    existing = db.patients.find_one({"patient_id": patient.patient_id})
    if existing:
        raise ValueError(f"Patient with ID {patient.patient_id} already exists in MongoDB")
    
    # Prepare and insert document
    doc = prepare_patient_document(patient)
    result = db.patients.insert_one(doc)
    
    # Fetch and return created document
    created_doc = db.patients.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_doc)


def get_patient_mongo(patient_id: int) -> Optional[dict]:
    """
    Get patient from MongoDB by patient_id
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Patient document or None
    """
    db = get_mongo_db()
    patient = db.patients.find_one({"patient_id": patient_id})
    
    if patient:
        return serialize_mongo_doc(patient)
    return None


def get_patients_mongo(skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Get all patients from MongoDB with pagination
    
    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
    
    Returns:
        List of patient documents
    """
    db = get_mongo_db()
    cursor = db.patients.find().skip(skip).limit(limit).sort("patient_id", 1)
    
    patients = []
    for patient in cursor:
        patients.append(serialize_mongo_doc(patient))
    
    return patients


def get_patients_count_mongo() -> int:
    """Get total count of patients in MongoDB"""
    db = get_mongo_db()
    return db.patients.count_documents({})


def update_patient_mongo(patient_id: int, patient: PatientMongoUpdate) -> Optional[dict]:
    """
    Update patient in MongoDB
    
    Args:
        patient_id: Patient ID
        patient: PatientMongoUpdate model with fields to update
    
    Returns:
        Updated patient document or None
    """
    db = get_mongo_db()
    
    # Build update document
    update_doc = {}
    
    if patient.demographics is not None:
        update_doc["demographics"] = patient.demographics.model_dump()
    
    if patient.lifestyle is not None:
        update_doc["lifestyle"] = patient.lifestyle.model_dump()
    
    if not update_doc:
        return get_patient_mongo(patient_id)
    
    # Update document
    result = db.patients.update_one(
        {"patient_id": patient_id},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        return None
    
    return get_patient_mongo(patient_id)


def delete_patient_mongo(patient_id: int) -> bool:
    """
    Delete patient from MongoDB
    
    Args:
        patient_id: Patient ID
    
    Returns:
        True if deleted, False if not found
    """
    db = get_mongo_db()
    result = db.patients.delete_one({"patient_id": patient_id})
    return result.deleted_count > 0


# ============= MEDICAL RECORD CRUD (MongoDB) =============

def create_medical_record_mongo(record: MedicalRecordMongoCreate) -> dict:
    """
    Create medical record in MongoDB medical_records collection
    
    Args:
        record: MedicalRecordMongoCreate model
    
    Returns:
        Created medical record document
    """
    db = get_mongo_db()
    
    # Check if patient exists
    patient = db.patients.find_one({"patient_id": record.patient_id})
    if not patient:
        raise ValueError(f"Patient with ID {record.patient_id} not found in MongoDB")
    
    # Check if record already exists
    existing = db.medical_records.find_one({"patient_id": record.patient_id})
    if existing:
        raise ValueError(f"Medical record for patient {record.patient_id} already exists")
    
    # Prepare and insert document
    doc = prepare_medical_record_document(record)
    result = db.medical_records.insert_one(doc)
    
    # Fetch and return created document
    created_doc = db.medical_records.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(created_doc)


def get_medical_record_mongo(patient_id: int) -> Optional[dict]:
    """
    Get medical record from MongoDB by patient_id
    
    Args:
        patient_id: Patient ID
    
    Returns:
        Medical record document or None
    """
    db = get_mongo_db()
    record = db.medical_records.find_one({"patient_id": patient_id})
    
    if record:
        return serialize_mongo_doc(record)
    return None


def get_medical_records_mongo(skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Get all medical records from MongoDB with pagination
    
    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
    
    Returns:
        List of medical record documents
    """
    db = get_mongo_db()
    cursor = db.medical_records.find().skip(skip).limit(limit).sort("patient_id", 1)
    
    records = []
    for record in cursor:
        records.append(serialize_mongo_doc(record))
    
    return records


def get_medical_records_count_mongo() -> int:
    """Get total count of medical records in MongoDB"""
    db = get_mongo_db()
    return db.medical_records.count_documents({})


def update_medical_record_mongo(patient_id: int, record: MedicalRecordMongoUpdate) -> Optional[dict]:
    """
    Update medical record in MongoDB
    
    Args:
        patient_id: Patient ID
        record: MedicalRecordMongoUpdate model with fields to update
    
    Returns:
        Updated medical record document or None
    """
    db = get_mongo_db()
    
    # Build update document
    update_doc = {}
    
    if record.measurements is not None:
        update_doc["measurements"] = record.measurements.model_dump()
    
    if record.diagnosis is not None:
        update_doc["diagnosis"] = record.diagnosis.model_dump()
    
    if not update_doc:
        return get_medical_record_mongo(patient_id)
    
    # Update document
    result = db.medical_records.update_one(
        {"patient_id": patient_id},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        return None
    
    return get_medical_record_mongo(patient_id)


def delete_medical_record_mongo(patient_id: int) -> bool:
    """
    Delete medical record from MongoDB
    
    Args:
        patient_id: Patient ID
    
    Returns:
        True if deleted, False if not found
    """
    db = get_mongo_db()
    result = db.medical_records.delete_one({"patient_id": patient_id})
    return result.deleted_count > 0


# ============= SEARCH & FILTER OPERATIONS =============

def search_patients_by_disease_mongo(has_disease: bool, skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Search patients by cardiovascular disease status
    
    Args:
        has_disease: True for patients with disease, False for without
        skip: Number of documents to skip
        limit: Maximum number of documents to return
    
    Returns:
        List of medical record documents matching criteria
    """
    db = get_mongo_db()
    cursor = db.medical_records.find(
        {"diagnosis.cardiovascular_disease": has_disease}
    ).skip(skip).limit(limit)
    
    records = []
    for record in cursor:
        records.append(serialize_mongo_doc(record))
    
    return records


def get_mongo_stats() -> dict:
    """
    Get MongoDB database statistics
    
    Returns:
        Dictionary with collection counts and info
    """
    db = get_mongo_db()
    
    return {
        "database": db.name,
        "collections": {
            "patients": db.patients.count_documents({}),
            "medical_records": db.medical_records.count_documents({})
        },
        "indexes": {
            "patients": list(db.patients.list_indexes()),
            "medical_records": list(db.medical_records.list_indexes())
        }
    }