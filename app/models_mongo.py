"""
Pydantic models for MongoDB operations
Based on Task 1 MongoDB schema
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


# ============= MONGODB PATIENT MODELS =============

class PatientDemographics(BaseModel):
    """Demographics nested document"""
    age_days: int
    age_years: float
    gender: str = Field(..., pattern="^(male|female)$")
    height_cm: int
    weight_kg: float
    bmi: float


class PatientLifestyle(BaseModel):
    """Lifestyle nested document"""
    smoker: bool
    alcohol_consumption: bool
    physically_active: bool


class PatientMongoCreate(BaseModel):
    """Model for creating patient in MongoDB"""
    patient_id: int
    demographics: PatientDemographics
    lifestyle: PatientLifestyle
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 999999,
                "demographics": {
                    "age_days": 18000,
                    "age_years": 49.32,
                    "gender": "male",
                    "height_cm": 175,
                    "weight_kg": 80.0,
                    "bmi": 26.12
                },
                "lifestyle": {
                    "smoker": False,
                    "alcohol_consumption": False,
                    "physically_active": True
                }
            }
        }


class PatientMongoUpdate(BaseModel):
    """Model for updating patient in MongoDB"""
    demographics: Optional[PatientDemographics] = None
    lifestyle: Optional[PatientLifestyle] = None


class PatientMongoResponse(BaseModel):
    """Model for patient response from MongoDB"""
    id: str = Field(..., alias="_id")
    patient_id: int
    demographics: PatientDemographics
    lifestyle: PatientLifestyle
    created_at: Optional[str] = None
    
    class Config:
        populate_by_name = True


# ============= MONGODB MEDICAL RECORD MODELS =============

class BloodPressure(BaseModel):
    """Blood pressure nested document"""
    systolic: int = Field(..., ge=70, le=250)
    diastolic: int = Field(..., ge=40, le=150)
    
    @validator('diastolic')
    def validate_bp(cls, v, values):
        if 'systolic' in values and v >= values['systolic']:
            raise ValueError('Diastolic must be less than systolic')
        return v


class Measurements(BaseModel):
    """Measurements nested document"""
    blood_pressure: BloodPressure
    cholesterol_level: int = Field(..., ge=1, le=3)
    cholesterol_label: str
    glucose_level: int = Field(..., ge=1, le=3)
    glucose_label: str


class Diagnosis(BaseModel):
    """Diagnosis nested document"""
    cardiovascular_disease: bool
    diagnosis_date: Optional[str] = None


class MedicalRecordMongoCreate(BaseModel):
    """Model for creating medical record in MongoDB"""
    patient_id: int
    measurements: Measurements
    diagnosis: Diagnosis
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 999999,
                "measurements": {
                    "blood_pressure": {
                        "systolic": 120,
                        "diastolic": 80
                    },
                    "cholesterol_level": 1,
                    "cholesterol_label": "normal",
                    "glucose_level": 1,
                    "glucose_label": "normal"
                },
                "diagnosis": {
                    "cardiovascular_disease": False,
                    "diagnosis_date": "2024-01-15"
                }
            }
        }


class MedicalRecordMongoUpdate(BaseModel):
    """Model for updating medical record in MongoDB"""
    measurements: Optional[Measurements] = None
    diagnosis: Optional[Diagnosis] = None


class MedicalRecordMongoResponse(BaseModel):
    """Model for medical record response from MongoDB"""
    id: str = Field(..., alias="_id")
    patient_id: int
    measurements: Measurements
    diagnosis: Diagnosis
    recorded_at: Optional[str] = None
    
    class Config:
        populate_by_name = True


# ============= UTILITY MODELS =============

class MongoHealthCheck(BaseModel):
    """MongoDB health check response"""
    status: str
    database: str
    collections: list
    total_documents: dict