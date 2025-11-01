"""
CRUD operations for all database tables
"""

from typing import List, Optional, Dict, Any
from app.database import execute_query, execute_insert, execute_update, get_db_connection, dict_from_row
from app.models import (
    PatientCreate, PatientUpdate,
    MedicalMeasurementCreate, MedicalMeasurementUpdate,
    LifestyleFactorsCreate, LifestyleFactorsUpdate,
    DiagnosisCreate, DiagnosisUpdate
)


# ============= PATIENT CRUD =============

def create_patient(patient: PatientCreate) -> Dict[str, Any]:
    """Create a new patient"""
    # Calculate age_years and bmi
    age_years = round(patient.age_days / 365.25, 2)
    bmi = round(patient.weight / ((patient.height / 100) ** 2), 2)
    
    query = """
    INSERT INTO patients (patient_id, age_days, age_years, gender, height, weight, bmi)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (patient.patient_id, patient.age_days, age_years, patient.gender, 
              patient.height, patient.weight, bmi)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient.patient_id,))
        result = cursor.fetchone()
        return dict_from_row(result)


def get_patient(patient_id: int) -> Optional[Dict[str, Any]]:
    """Get a patient by ID"""
    query = "SELECT * FROM patients WHERE patient_id = ?"
    results = execute_query(query, (patient_id,))
    return results[0] if results else None


def get_patients(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all patients with pagination"""
    query = "SELECT * FROM patients ORDER BY patient_id LIMIT ? OFFSET ?"
    return execute_query(query, (limit, skip))


def update_patient(patient_id: int, patient: PatientUpdate) -> Optional[Dict[str, Any]]:
    """Update a patient"""
    update_fields = []
    params = []
    
    if patient.age_days is not None:
        update_fields.append("age_days = ?")
        params.append(patient.age_days)
        update_fields.append("age_years = ?")
        params.append(round(patient.age_days / 365.25, 2))
    
    if patient.gender is not None:
        update_fields.append("gender = ?")
        params.append(patient.gender)
    
    if patient.height is not None:
        update_fields.append("height = ?")
        params.append(patient.height)
    
    if patient.weight is not None:
        update_fields.append("weight = ?")
        params.append(patient.weight)
    
    # Recalculate BMI if height or weight changed
    if patient.height is not None or patient.weight is not None:
        existing = get_patient(patient_id)
        if existing:
            height = patient.height if patient.height is not None else existing['height']
            weight = patient.weight if patient.weight is not None else existing['weight']
            bmi = round(weight / ((height / 100) ** 2), 2)
            update_fields.append("bmi = ?")
            params.append(bmi)
    
    if not update_fields:
        return get_patient(patient_id)
    
    params.append(patient_id)
    query = f"UPDATE patients SET {', '.join(update_fields)} WHERE patient_id = ?"
    execute_update(query, tuple(params))
    return get_patient(patient_id)


def delete_patient(patient_id: int) -> bool:
    """Delete a patient"""
    query = "DELETE FROM patients WHERE patient_id = ?"
    rows_affected = execute_update(query, (patient_id,))
    return rows_affected > 0


# ============= MEDICAL MEASUREMENT CRUD =============

def create_medical_measurement(measurement: MedicalMeasurementCreate) -> Dict[str, Any]:
    """Create a new medical measurement"""
    query = """
    INSERT INTO medical_measurements (patient_id, ap_hi, ap_lo, cholesterol, glucose)
    VALUES (?, ?, ?, ?, ?)
    """
    params = (measurement.patient_id, measurement.ap_hi, measurement.ap_lo,
              measurement.cholesterol, measurement.glucose)
    
    measurement_id = execute_insert(query, params)
    return get_medical_measurement(measurement_id)


def get_medical_measurement(measurement_id: int) -> Optional[Dict[str, Any]]:
    """Get a medical measurement by ID"""
    query = "SELECT * FROM medical_measurements WHERE measurement_id = ?"
    results = execute_query(query, (measurement_id,))
    return results[0] if results else None


def get_medical_measurements(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all medical measurements with pagination"""
    query = "SELECT * FROM medical_measurements ORDER BY measurement_id LIMIT ? OFFSET ?"
    return execute_query(query, (limit, skip))


def get_medical_measurements_by_patient(patient_id: int) -> List[Dict[str, Any]]:
    """Get all medical measurements for a specific patient"""
    query = "SELECT * FROM medical_measurements WHERE patient_id = ? ORDER BY measurement_date DESC"
    return execute_query(query, (patient_id,))


def update_medical_measurement(measurement_id: int, measurement: MedicalMeasurementUpdate) -> Optional[Dict[str, Any]]:
    """Update a medical measurement"""
    update_fields = []
    params = []
    
    if measurement.ap_hi is not None:
        update_fields.append("ap_hi = ?")
        params.append(measurement.ap_hi)
    
    if measurement.ap_lo is not None:
        update_fields.append("ap_lo = ?")
        params.append(measurement.ap_lo)
    
    if measurement.cholesterol is not None:
        update_fields.append("cholesterol = ?")
        params.append(measurement.cholesterol)
    
    if measurement.glucose is not None:
        update_fields.append("glucose = ?")
        params.append(measurement.glucose)
    
    if not update_fields:
        return get_medical_measurement(measurement_id)
    
    params.append(measurement_id)
    query = f"UPDATE medical_measurements SET {', '.join(update_fields)} WHERE measurement_id = ?"
    execute_update(query, tuple(params))
    return get_medical_measurement(measurement_id)


def delete_medical_measurement(measurement_id: int) -> bool:
    """Delete a medical measurement"""
    query = "DELETE FROM medical_measurements WHERE measurement_id = ?"
    rows_affected = execute_update(query, (measurement_id,))
    return rows_affected > 0


# ============= LIFESTYLE FACTORS CRUD =============

def create_lifestyle_factors(lifestyle: LifestyleFactorsCreate) -> Dict[str, Any]:
    """Create new lifestyle factors"""
    query = """
    INSERT INTO lifestyle_factors (patient_id, smoke, alcohol, physical_activity)
    VALUES (?, ?, ?, ?)
    """
    params = (lifestyle.patient_id, lifestyle.smoke, lifestyle.alcohol, lifestyle.physical_activity)
    
    lifestyle_id = execute_insert(query, params)
    return get_lifestyle_factors(lifestyle_id)


def get_lifestyle_factors(lifestyle_id: int) -> Optional[Dict[str, Any]]:
    """Get lifestyle factors by ID"""
    query = "SELECT * FROM lifestyle_factors WHERE lifestyle_id = ?"
    results = execute_query(query, (lifestyle_id,))
    return results[0] if results else None


def get_all_lifestyle_factors(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all lifestyle factors with pagination"""
    query = "SELECT * FROM lifestyle_factors ORDER BY lifestyle_id LIMIT ? OFFSET ?"
    return execute_query(query, (limit, skip))


def get_lifestyle_factors_by_patient(patient_id: int) -> List[Dict[str, Any]]:
    """Get lifestyle factors for a specific patient"""
    query = "SELECT * FROM lifestyle_factors WHERE patient_id = ? ORDER BY recorded_at DESC"
    return execute_query(query, (patient_id,))


def update_lifestyle_factors(lifestyle_id: int, lifestyle: LifestyleFactorsUpdate) -> Optional[Dict[str, Any]]:
    """Update lifestyle factors"""
    update_fields = []
    params = []
    
    if lifestyle.smoke is not None:
        update_fields.append("smoke = ?")
        params.append(lifestyle.smoke)
    
    if lifestyle.alcohol is not None:
        update_fields.append("alcohol = ?")
        params.append(lifestyle.alcohol)
    
    if lifestyle.physical_activity is not None:
        update_fields.append("physical_activity = ?")
        params.append(lifestyle.physical_activity)
    
    if not update_fields:
        return get_lifestyle_factors(lifestyle_id)
    
    params.append(lifestyle_id)
    query = f"UPDATE lifestyle_factors SET {', '.join(update_fields)} WHERE lifestyle_id = ?"
    execute_update(query, tuple(params))
    return get_lifestyle_factors(lifestyle_id)


def delete_lifestyle_factors(lifestyle_id: int) -> bool:
    """Delete lifestyle factors"""
    query = "DELETE FROM lifestyle_factors WHERE lifestyle_id = ?"
    rows_affected = execute_update(query, (lifestyle_id,))
    return rows_affected > 0


# ============= DIAGNOSIS CRUD =============

def create_diagnosis(diagnosis: DiagnosisCreate) -> Dict[str, Any]:
    """Create a new diagnosis (trigger will auto-log)"""
    query = """
    INSERT INTO diagnoses (patient_id, cardiovascular_disease)
    VALUES (?, ?)
    """
    params = (diagnosis.patient_id, diagnosis.cardiovascular_disease)
    
    diagnosis_id = execute_insert(query, params)
    return get_diagnosis(diagnosis_id)


def get_diagnosis(diagnosis_id: int) -> Optional[Dict[str, Any]]:
    """Get a diagnosis by ID"""
    query = "SELECT * FROM diagnoses WHERE diagnosis_id = ?"
    results = execute_query(query, (diagnosis_id,))
    return results[0] if results else None


def get_all_diagnoses(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all diagnoses with pagination"""
    query = "SELECT * FROM diagnoses ORDER BY diagnosis_id LIMIT ? OFFSET ?"
    return execute_query(query, (limit, skip))


def get_diagnoses_by_patient(patient_id: int) -> List[Dict[str, Any]]:
    """Get all diagnoses for a specific patient"""
    query = "SELECT * FROM diagnoses WHERE patient_id = ? ORDER BY diagnosis_date DESC"
    return execute_query(query, (patient_id,))


def update_diagnosis(diagnosis_id: int, diagnosis: DiagnosisUpdate) -> Optional[Dict[str, Any]]:
    """Update a diagnosis (trigger will auto-log the update)"""
    if diagnosis.cardiovascular_disease is None:
        return get_diagnosis(diagnosis_id)
    
    query = "UPDATE diagnoses SET cardiovascular_disease = ? WHERE diagnosis_id = ?"
    execute_update(query, (diagnosis.cardiovascular_disease, diagnosis_id))
    return get_diagnosis(diagnosis_id)


def delete_diagnosis(diagnosis_id: int) -> bool:
    """Delete a diagnosis"""
    query = "DELETE FROM diagnoses WHERE diagnosis_id = ?"
    rows_affected = execute_update(query, (diagnosis_id,))
    return rows_affected > 0