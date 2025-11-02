"""
Pydantic models for request/response validation
Based on cardiovascular disease database schema
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import IntEnum
from datetime import datetime # <-- ADDED THIS IMPORT


# ============= ENUMS =============

class Gender(IntEnum):
    """Gender codes: 1=Female, 2=Male"""
    FEMALE = 1
    MALE = 2


class CholesterolLevel(IntEnum):
    """Cholesterol levels: 1=Normal, 2=Above Normal, 3=Well Above Normal"""
    NORMAL = 1
    ABOVE_NORMAL = 2
    WELL_ABOVE_NORMAL = 3


class GlucoseLevel(IntEnum):
    """Glucose levels: 1=Normal, 2=Above Normal, 3=Well Above Normal"""
    NORMAL = 1
    ABOVE_NORMAL = 2
    WELL_ABOVE_NORMAL = 3


class BinaryChoice(IntEnum):
    """Binary yes/no choices: 0=No, 1=Yes"""
    NO = 0
    YES = 1


# ============= PATIENT MODELS =============

class PatientBase(BaseModel):
    """Base model for Patient"""
    age_days: int = Field(..., gt=0, description="Age in days")
    gender: int = Field(..., ge=1, le=2, description="1=Female, 2=Male")
    height: int = Field(..., gt=0, le=250, description="Height in cm")
    weight: float = Field(..., gt=0, le=300, description="Weight in kg")


class PatientCreate(PatientBase):
    """Model for creating a new patient"""
    patient_id: int = Field(..., description="Unique patient ID")


class PatientUpdate(BaseModel):
    """Model for updating patient (all fields optional)"""
    age_days: Optional[int] = Field(None, gt=0)
    gender: Optional[int] = Field(None, ge=1, le=2)
    height: Optional[int] = Field(None, gt=0, le=250)
    weight: Optional[float] = Field(None, gt=0, le=300)


class PatientResponse(BaseModel):
    """Model for patient response"""
    patient_id: int
    age_days: int
    age_years: Optional[float] = None
    gender: int
    height: int
    weight: float
    bmi: Optional[float] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= MEDICAL MEASUREMENT MODELS =============

class MedicalMeasurementBase(BaseModel):
    """Base model for Medical Measurements"""
    patient_id: int = Field(..., gt=0)
    ap_hi: int = Field(..., ge=70, le=250, description="Systolic blood pressure")
    ap_lo: int = Field(..., ge=40, le=150, description="Diastolic blood pressure")
    cholesterol: int = Field(..., ge=1, le=3, description="Cholesterol level (1-3)")
    glucose: int = Field(..., ge=1, le=3, description="Glucose level (1-3)")
    
    @validator('ap_lo')
    def validate_blood_pressure(cls, v, values):
        """Ensure diastolic BP is less than systolic BP"""
        if 'ap_hi' in values and v >= values['ap_hi']:
            raise ValueError('Diastolic BP (ap_lo) must be less than Systolic BP (ap_hi)')
        return v


class MedicalMeasurementCreate(MedicalMeasurementBase):
    """Model for creating medical measurement"""
    pass


class MedicalMeasurementUpdate(BaseModel):
    """Model for updating medical measurement"""
    ap_hi: Optional[int] = Field(None, ge=70, le=250)
    ap_lo: Optional[int] = Field(None, ge=40, le=150)
    cholesterol: Optional[int] = Field(None, ge=1, le=3)
    glucose: Optional[int] = Field(None, ge=1, le=3)


class MedicalMeasurementResponse(BaseModel):
    """Model for medical measurement response"""
    measurement_id: int
    patient_id: int
    ap_hi: int
    ap_lo: int
    cholesterol: int
    glucose: int
    measurement_date: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= LIFESTYLE FACTORS MODELS =============

class LifestyleFactorsBase(BaseModel):
    """Base model for Lifestyle Factors"""
    patient_id: int = Field(..., gt=0)
    smoke: int = Field(..., ge=0, le=1, description="Smoking status (0=No, 1=Yes)")
    alcohol: int = Field(..., ge=0, le=1, description="Alcohol consumption (0=No, 1=Yes)")
    physical_activity: int = Field(..., ge=0, le=1, description="Physical activity (0=No, 1=Yes)")


class LifestyleFactorsCreate(LifestyleFactorsBase):
    """Model for creating lifestyle factors"""
    pass


class LifestyleFactorsUpdate(BaseModel):
    """Model for updating lifestyle factors"""
    smoke: Optional[int] = Field(None, ge=0, le=1)
    alcohol: Optional[int] = Field(None, ge=0, le=1)
    physical_activity: Optional[int] = Field(None, ge=0, le=1)


class LifestyleFactorsResponse(BaseModel):
    """Model for lifestyle factors response"""
    lifestyle_id: int
    patient_id: int
    smoke: int
    alcohol: int
    physical_activity: int
    recorded_at: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= DIAGNOSIS MODELS =============

class DiagnosisBase(BaseModel):
    """Base model for Diagnosis"""
    patient_id: int = Field(..., gt=0)
    cardiovascular_disease: int = Field(..., ge=0, le=1, description="Disease presence (0=No, 1=Yes)")


class DiagnosisCreate(DiagnosisBase):
    """Model for creating diagnosis"""
    pass


class DiagnosisUpdate(BaseModel):
    """Model for updating diagnosis"""
    cardiovascular_disease: Optional[int] = Field(None, ge=0, le=1)


class DiagnosisResponse(BaseModel):
    """Model for diagnosis response"""
    diagnosis_id: int
    patient_id: int
    cardiovascular_disease: int
    diagnosis_date: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= UTILITY MODELS =============

class HealthCheck(BaseModel):
    """API health check response"""
    status: str
    message: str
    database: str
    tables_count: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


# ============= PREDICTION MODELS =============

class PredictionBase(BaseModel):
    """Base model for a prediction log"""
    patient_id: int
    prediction_score: float = Field(..., ge=0, le=1, description="Model's raw probability score")
    predicted_class: int = Field(..., ge=0, le=1, description="Final predicted class (0=No, 1=Yes)")

class PredictionCreate(PredictionBase):
    """Model for creating a new prediction log"""
    pass

class PredictionResponse(PredictionBase):
    """Model for a prediction log response"""
    # Use Field with alias to handle MongoDB's '_id'
    id: str = Field(..., alias="_id", description="Unique prediction ID from MongoDB")
    created_at: datetime = Field(..., description="Timestamp of when the prediction was logged")
    
    class Config:
        from_attributes = True
        populate_by_name = True # Important for aliasing _id
        json_encoders = {
            # This ensures datetime is sent as a clean ISO string
            datetime: lambda dt: dt.isoformat() 
        }
