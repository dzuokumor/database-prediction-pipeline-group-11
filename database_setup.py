import sqlite3
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os


def create_sqlite_database(db_path='cardiovascular.db', csv_path='cardio_train.csv'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS diagnosis_log')
    cursor.execute('DROP TABLE IF EXISTS diagnoses')
    cursor.execute('DROP TABLE IF EXISTS lifestyle_factors')
    cursor.execute('DROP TABLE IF EXISTS medical_measurements')
    cursor.execute('DROP TABLE IF EXISTS patients')

    cursor.execute('''
    CREATE TABLE patients (
        patient_id INTEGER PRIMARY KEY,
        age_days INTEGER NOT NULL CHECK(age_days > 0),
        age_years REAL,
        gender INTEGER NOT NULL CHECK(gender IN (1, 2)),
        height INTEGER NOT NULL CHECK(height > 0),
        weight REAL NOT NULL CHECK(weight > 0),
        bmi REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE medical_measurements (
        measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        ap_hi INTEGER NOT NULL,
        ap_lo INTEGER NOT NULL,
        cholesterol INTEGER NOT NULL CHECK(cholesterol IN (1, 2, 3)),
        glucose INTEGER NOT NULL CHECK(glucose IN (1, 2, 3)),
        measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE lifestyle_factors (
        lifestyle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        smoke INTEGER NOT NULL CHECK(smoke IN (0, 1)),
        alcohol INTEGER NOT NULL CHECK(alcohol IN (0, 1)),
        physical_activity INTEGER NOT NULL CHECK(physical_activity IN (0, 1)),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE diagnoses (
        diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        cardiovascular_disease INTEGER NOT NULL CHECK(cardiovascular_disease IN (0, 1)),
        diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE diagnosis_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        diagnosis_id INTEGER,
        patient_id INTEGER,
        action_type TEXT NOT NULL,
        cardiovascular_disease INTEGER,
        action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER log_diagnosis_insert
    AFTER INSERT ON diagnoses
    FOR EACH ROW
    BEGIN
        INSERT INTO diagnosis_log (diagnosis_id, patient_id, action_type, cardiovascular_disease)
        VALUES (NEW.diagnosis_id, NEW.patient_id, 'INSERT', NEW.cardiovascular_disease);
    END;
    ''')

    cursor.execute('''
    CREATE TRIGGER log_diagnosis_update
    AFTER UPDATE ON diagnoses
    FOR EACH ROW
    BEGIN
        INSERT INTO diagnosis_log (diagnosis_id, patient_id, action_type, cardiovascular_disease)
        VALUES (NEW.diagnosis_id, NEW.patient_id, 'UPDATE', NEW.cardiovascular_disease);
    END;
    ''')

    conn.commit()

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, delimiter=';')

        for _, row in df.iterrows():
            age_years = row['age'] / 365.25
            bmi = row['weight'] / ((row['height'] / 100) ** 2)

            cursor.execute('''
            INSERT INTO patients (patient_id, age_days, age_years, gender, height, weight, bmi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['id'], row['age'], age_years, row['gender'],
                  row['height'], row['weight'], bmi))

            cursor.execute('''
            INSERT INTO medical_measurements (patient_id, ap_hi, ap_lo, cholesterol, glucose)
            VALUES (?, ?, ?, ?, ?)
            ''', (row['id'], row['ap_hi'], row['ap_lo'],
                  row['cholesterol'], row['gluc']))

            cursor.execute('''
            INSERT INTO lifestyle_factors (patient_id, smoke, alcohol, physical_activity)
            VALUES (?, ?, ?, ?)
            ''', (row['id'], row['smoke'], row['alco'], row['active']))

            cursor.execute('''
            INSERT INTO diagnoses (patient_id, cardiovascular_disease)
            VALUES (?, ?)
            ''', (row['id'], row['cardio']))

        conn.commit()
        print(f"Inserted {len(df)} records into SQLite database")

    conn.close()
    print("SQLite database created successfully!")


def create_stored_procedures(db_path='cardiovascular.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS risk_assessments (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()
    print("Stored procedure table created!")


def calculate_risk_score(patient_id, db_path='cardiovascular.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT p.age_years, p.bmi, p.gender,
           m.ap_hi, m.ap_lo, m.cholesterol, m.glucose,
           l.smoke, l.alcohol, l.physical_activity
    FROM patients p
    JOIN medical_measurements m ON p.patient_id = m.patient_id
    JOIN lifestyle_factors l ON p.patient_id = l.patient_id
    WHERE p.patient_id = ?
    ''', (patient_id,))

    result = cursor.fetchone()

    if not result:
        conn.close()
        return None

    age_years, bmi, gender, ap_hi, ap_lo, cholesterol, glucose, smoke, alcohol, physical_activity = result

    risk_score = 0

    if age_years > 55:
        risk_score += 30
    elif age_years > 45:
        risk_score += 20
    elif age_years > 35:
        risk_score += 10

    if bmi > 30:
        risk_score += 25
    elif bmi > 25:
        risk_score += 15

    if ap_hi > 140 or ap_lo > 90:
        risk_score += 20
    elif ap_hi > 130 or ap_lo > 80:
        risk_score += 10

    if cholesterol == 3:
        risk_score += 15
    elif cholesterol == 2:
        risk_score += 10

    if glucose == 3:
        risk_score += 15
    elif glucose == 2:
        risk_score += 10

    if smoke == 1:
        risk_score += 15

    if alcohol == 1:
        risk_score += 5

    if physical_activity == 0:
        risk_score += 10

    if risk_score >= 70:
        risk_level = 'CRITICAL'
    elif risk_score >= 50:
        risk_level = 'HIGH'
    elif risk_score >= 30:
        risk_level = 'MODERATE'
    else:
        risk_level = 'LOW'

    cursor.execute('''
    INSERT INTO risk_assessments (patient_id, risk_score, risk_level)
    VALUES (?, ?, ?)
    ''', (patient_id, risk_score, risk_level))

    conn.commit()
    conn.close()

    return {'risk_score': risk_score, 'risk_level': risk_level}


def create_mongodb_database(csv_path='cardio_train.csv',
                            mongo_uri='mongodb://localhost:27017/',
                            db_name='cardiovascular_db'):
    client = MongoClient(mongo_uri)
    db = client[db_name]

    db.patients.drop()
    db.medical_records.drop()

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, delimiter=';')

        patients_docs = []
        medical_records_docs = []

        for _, row in df.iterrows():
            age_years = row['age'] / 365.25
            bmi = row['weight'] / ((row['height'] / 100) ** 2)

            patient_doc = {
                'patient_id': int(row['id']),
                'demographics': {
                    'age_days': int(row['age']),
                    'age_years': round(age_years, 2),
                    'gender': 'female' if row['gender'] == 1 else 'male',
                    'height_cm': int(row['height']),
                    'weight_kg': float(row['weight']),
                    'bmi': round(bmi, 2)
                },
                'lifestyle': {
                    'smoker': bool(row['smoke']),
                    'alcohol_consumption': bool(row['alco']),
                    'physically_active': bool(row['active'])
                },
                'created_at': datetime.now()
            }
            patients_docs.append(patient_doc)

            medical_record_doc = {
                'patient_id': int(row['id']),
                'measurements': {
                    'blood_pressure': {
                        'systolic': int(row['ap_hi']),
                        'diastolic': int(row['ap_lo'])
                    },
                    'cholesterol_level': int(row['cholesterol']),
                    'cholesterol_label': 'normal' if row['cholesterol'] == 1 else
                    'above_normal' if row['cholesterol'] == 2 else 'high',
                    'glucose_level': int(row['gluc']),
                    'glucose_label': 'normal' if row['gluc'] == 1 else
                    'above_normal' if row['gluc'] == 2 else 'high'
                },
                'diagnosis': {
                    'cardiovascular_disease': bool(row['cardio']),
                    'diagnosis_date': datetime.now()
                },
                'recorded_at': datetime.now()
            }
            medical_records_docs.append(medical_record_doc)

        db.patients.insert_many(patients_docs)
        db.medical_records.insert_many(medical_records_docs)

        db.patients.create_index('patient_id', unique=True)
        db.medical_records.create_index('patient_id')
        db.medical_records.create_index('diagnosis.cardiovascular_disease')

        print(f"Inserted {len(patients_docs)} patient documents into MongoDB")
        print(f"Inserted {len(medical_records_docs)} medical record documents into MongoDB")

    client.close()
    print("MongoDB database created successfully!")


if __name__ == '__main__':
    print("Creating SQLite database...")
    create_sqlite_database()

    print("\nCreating stored procedure table...")
    create_stored_procedures()

    print("\nTesting stored procedure with patient_id=1...")
    result = calculate_risk_score(1)
    print(f"Risk assessment result: {result}")

    print("\nCreating MongoDB database...")
    create_mongodb_database()

    print("\nDatabase setup complete!")