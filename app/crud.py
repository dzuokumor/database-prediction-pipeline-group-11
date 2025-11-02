"""
CRUD operations for all database tables
Synchronizes writes to both SQLite and MongoDB
"""

from typing import List, Optional, Dict, Any
from app.database import (
    execute_query, execute_insert, execute_update, 
    get_db_connection, dict_from_row,
    get_mongo_db  # <-- IMPORT THE MONGO DB CONNECTION
)
from app.models import (
    PatientCreate, PatientUpdate,
    MedicalMeasurementCreate, MedicalMeasurementUpdate,
    LifestyleFactorsCreate, LifestyleFactorsUpdate,
    DiagnosisCreate, DiagnosisUpdate
)


# ============= PATIENT CRUD =============

def create_patient(patient: PatientCreate) -> Dict[str, Any]:
    """Create a new patient in SQL and Mongo"""
    # Calculate age_years and bmi
    age_years = round(patient.age_days / 365.25, 2)
    bmi = round(patient.weight / ((patient.height / 100) ** 2), 2)
    
    query = """
    INSERT INTO patients (patient_id, age_days, age_years, gender, height, weight, bmi)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (patient.patient_id, patient.age_days, age_years, patient.gender, 
              patient.height, patient.weight, bmi)
    
    # --- SQL LOGIC ---
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient.patient_id,))
        result = cursor.fetchone()
        sql_result_dict = dict_from_row(result)

    # --- MONGO LOGIC ---
    try:
        db = get_mongo_db()
        # Use a "patients" collection
        db.patients.insert_one(sql_result_dict)
    except Exception as e:
        print(f"Error: Failed to create patient {patient.patient_id} in MongoDB.")
        print(f"Details: {e}")
        # Note: In a real app, you might "rollback" the SQL insert.
        # For this project, logging the error is fine.

    return sql_result_dict


def get_patient(patient_id: int) -> Optional[Dict[str, Any]]:
    """Get a patient by ID (from SQL)"""
    # Reads come from SQL as the "source of truth"
    query = "SELECT * FROM patients WHERE patient_id = ?"
    results = execute_query(query, (patient_id,))
    return results[0] if results else None


def get_patients(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all patients with pagination (from SQL)"""
    query = "SELECT * FROM patients ORDER BY patient_id LIMIT ? OFFSET ?"
    return execute_query(query, (limit, skip))


def update_patient(patient_id: int, patient: PatientUpdate) -> Optional[Dict[str, Any]]:
    """Update a patient in SQL and Mongo"""
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
    
    # --- SQL LOGIC ---
    params.append(patient_id)
    query = f"UPDATE patients SET {', '.join(update_fields)} WHERE patient_id = ?"
    execute_update(query, tuple(params))
    
    # Get the fully updated patient record from SQL
    updated_patient_dict = get_patient(patient_id)

    # --- MONGO LOGIC ---
    if updated_patient_dict:
        try:
            db = get_mongo_db()
            db.patients.update_one(
                {"patient_id": patient_id},
                {"$set": updated_patient_dict}
            )
        except Exception as e:
            print(f"Error: Failed to update patient {patient_id} in MongoDB.")
            print(f"Details: {e}")

    return updated_patient_dict


def delete_patient(patient_id: int) -> bool:
    """Delete a patient from SQL and Mongo"""
    # --- SQL LOGIC ---
    query = "DELETE FROM patients WHERE patient_id = ?"
    rows_affected = execute_update(query, (patient_id,))
    
    # --- MONGO LOGIC ---
    if rows_affected > 0:
        try:
            db = get_mongo_db()
            db.patients.delete_one({"patient_id": patient_id})
        except Exception as e:
            print(f"Error: Failed to delete patient {patient_id} from MongoDB.")
            print(f"Details: {e}")
            
    return rows_affected > 0


# ============= MEDICAL MEASUREMENT CRUD =============

def create_medical_measurement(measurement: MedicalMeasurementCreate) -> Dict[str, Any]:
    """Create a new medical measurement in SQL and Mongo"""
    query = """
    INSERT INTO medical_measurements (patient_id, ap_hi, ap_lo, cholesterol, glucose)
    VALUES (?, ?, ?, ?, ?)
    """
    params = (measurement.patient_id, measurement.ap_hi, measurement.ap_lo,
              measurement.cholesterol, measurement.glucose)
    
    # --- SQL LOGIC ---
    measurement_id = execute_insert(query, params)
    sql_result_dict = get_medical_measurement(measurement_id)

    # --- MONGO LOGIC ---
    if sql_result_dict:
        try:
            db = get_mongo_db()
            db.medical_measurements.insert_one(sql_result_dict)
        except Exception as e:
            print(f"Error: Failed to create measurement {measurement_id} in MongoDB.")
            print(f"Details: {e}")
            
    return sql_result_dict


def get_medical_measurement(measurement_id: int) -> Optional[Dict[str, Any]]:
    """Get a medical measurement by ID (from SQL)"""
    query = "SELECT * FROM medical_measurements WHERE measurement_id = ?"
    results = execute_query(query, (measurement_id,))
    return results[0] if results else None


def get_medical_measurements(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all medical measurements with pagination (from SQL)"""
    query = "SELECT * FROM medical_measurements ORDER BY measurement_id LIMIT ? OFFSET ?"
    return execute_query(query, (limit, skip))


def get_medical_measurements_by_patient(patient_id: int) -> List[Dict[str, Any]]:
    """Get all medical measurements for a specific patient (from SQL)"""
    query = "SELECT * FROM medical_measurements WHERE patient_id = ? ORDER BY measurement_date DESC"
    return execute_query(query, (patient_id,))


def update_medical_measurement(measurement_id: int, measurement: MedicalMeasurementUpdate) -> Optional[Dict[str, Any]]:
    """Update a medical measurement in SQL and Mongo"""
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
    
    # --- SQL LOGIC ---
    params.append(measurement_id)
    query = f"UPDATE medical_measurements SET {', '.join(update_fields)} WHERE measurement_id = ?"
    execute_update(query, tuple(params))
    
    updated_measurement_dict = get_medical_measurement(measurement_id)

    # --- MONGO LOGIC ---
    if updated_measurement_dict:
        try:
            db = get_mongo_db()
            db.medical_measurements.update_one(
                {"measurement_id": measurement_id},
                {"$set": updated_measurement_dict}
            )
        except Exception as e:
            print(f"Error: Failed to update measurement {measurement_id} in MongoDB.")
            print(f"Details: {e}")

    return updated_measurement_dict


def delete_medical_measurement(measurement_id: int) -> bool:
    """Delete a medical measurement from SQL and Mongo"""
    # --- SQL LOGIC ---
    query = "DELETE FROM medical_measurements WHERE measurement_id = ?"
    rows_affected = execute_update(query, (measurement_id,))
    
    # --- MONGO LOGIC ---
    if rows_affected > 0:
        try:
            db = get_mongo_db()
            db.medical_measurements.delete_one({"measurement_id": measurement_id})
        except Exception as e:
            print(f"Error: Failed to delete measurement {measurement_id} from MongoDB.")
            print(f"Details: {e}")
            
    return rows_affected > 0


# ============= LIFESTYLE FACTORS CRUD =============

def create_lifestyle_factors(lifestyle: LifestyleFactorsCreate) -> Dict[str, Any]:
    """Create new lifestyle factors in SQL and Mongo"""
    query = """
    INSERT INTO lifestyle_factors (patient_id, smoke, alcohol, physical_activity)
    VALUES (?, ?, ?, ?)
    """
    params = (lifestyle.patient_id, lifestyle.smoke, lifestyle.alcohol, lifestyle.physical_activity)
    
    # --- SQL LOGIC ---
    lifestyle_id = execute_insert(query, params)
    sql_result_dict = get_lifestyle_factors(lifestyle_id)

    # --- MONGO LOGIC ---
    if sql_result_dict:
        try:
            db = get_mongo_db()
            db.lifestyle_factors.insert_one(sql_result_dict)
        except Exception as e:
            print(f"Error: Failed to create lifestyle factors {lifestyle_id} in MongoDB.")
            print(f"Details: {e}")

    return sql_result_dict


def get_lifestyle_factors(lifestyle_id: int) -> Optional[Dict[str, Any]]:
    """Get lifestyle factors by ID (from SQL)"""
    query = "SELECT * FROM lifestyle_factors WHERE lifestyle_id = ?"
    results = execute_query(query, (lifestyle_id,))
    return results[0] if results else None


def get_all_lifestyle_factors(skip: int = 0, limit: int = 100) -> List[Dict
