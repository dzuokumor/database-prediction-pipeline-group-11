import sqlite3
from pymongo import MongoClient
from database_setup import calculate_risk_score


def test_sqlite_database(db_path='cardiovascular.db'):
    print("Testing SQLite")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables created: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.execute("SELECT COUNT(*) FROM patients")
    patient_count = cursor.fetchone()[0]
    print(f"\nTotal patients: {patient_count}")

    cursor.execute("SELECT COUNT(*) FROM medical_measurements")
    measurement_count = cursor.fetchone()[0]
    print(f"Total medical measurements: {measurement_count}")

    cursor.execute("SELECT COUNT(*) FROM lifestyle_factors")
    lifestyle_count = cursor.fetchone()[0]
    print(f"Total lifestyle records: {lifestyle_count}")

    cursor.execute("SELECT COUNT(*) FROM diagnoses")
    diagnosis_count = cursor.fetchone()[0]
    print(f"Total diagnoses: {diagnosis_count}")

    cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='trigger'
    """)
    triggers = cursor.fetchall()
    print(f"\nTriggers created: {len(triggers)}")
    for trigger in triggers:
        print(f"  - {trigger[0]}")

    cursor.execute("""
    SELECT p.patient_id, p.age_years, p.gender, p.bmi,
           m.ap_hi, m.ap_lo, d.cardiovascular_disease
    FROM patients p
    JOIN medical_measurements m ON p.patient_id = m.patient_id
    JOIN diagnoses d ON p.patient_id = d.patient_id
    LIMIT 1
    """)
    sample = cursor.fetchone()
    print(f"\n✓ Sample patient record:")
    print(f"  Patient ID: {sample[0]}")
    print(f"  Age: {sample[1]:.1f} years")
    print(f"  Gender: {'Female' if sample[2] == 1 else 'Male'}")
    print(f"  BMI: {sample[3]:.2f}")
    print(f"  Blood Pressure: {sample[4]}/{sample[5]}")
    print(f"  Has CVD: {'Yes' if sample[6] == 1 else 'No'}")

    cursor.execute("SELECT COUNT(*) FROM diagnosis_log")
    log_count = cursor.fetchone()[0]
    print(f"\nDiagnosis log entries (from trigger): {log_count}")

    conn.close()
    print("\nSQLite database test passed!\n")


def test_mongodb_database(mongo_uri='mongodb://localhost:27017/',
                          db_name='cardiovascular_db'):
    print("TESTING MongoDB")

    client = MongoClient(mongo_uri)
    db = client[db_name]

    collections = db.list_collection_names()
    print(f"\nCollections created: {len(collections)}")
    for collection in collections:
        print(f"  - {collection}")

    patient_count = db.patients.count_documents({})
    print(f"\nTotal patients: {patient_count}")

    medical_count = db.medical_records.count_documents({})
    print(f" otal medical records: {medical_count}")

    sample_patient = db.patients.find_one()
    print(f"\nSample patient document:")
    print(f"  Patient ID: {sample_patient['patient_id']}")
    print(f"  Age: {sample_patient['demographics']['age_years']} years")
    print(f"  Gender: {sample_patient['demographics']['gender']}")
    print(f"  BMI: {sample_patient['demographics']['bmi']}")
    print(f"  Smoker: {sample_patient['lifestyle']['smoker']}")
    print(f"  Physically Active: {sample_patient['lifestyle']['physically_active']}")

    sample_medical = db.medical_records.find_one({'patient_id': sample_patient['patient_id']})
    print(f"\nSample medical record:")
    print(
        f"  Blood Pressure: {sample_medical['measurements']['blood_pressure']['systolic']}/{sample_medical['measurements']['blood_pressure']['diastolic']}")
    print(f"  Cholesterol: {sample_medical['measurements']['cholesterol_label']}")
    print(f"  Glucose: {sample_medical['measurements']['glucose_label']}")
    print(f"  Has CVD: {sample_medical['diagnosis']['cardiovascular_disease']}")

    indexes = db.patients.index_information()
    print(f"\nIndexes on patients collection: {len(indexes)}")
    for index_name, index_info in indexes.items():
        print(f"  - {index_name}: {index_info['key']}")

    cvd_positive = db.medical_records.count_documents({'diagnosis.cardiovascular_disease': True})
    cvd_negative = db.medical_records.count_documents({'diagnosis.cardiovascular_disease': False})
    print(f"\nCVD Statistics:")
    print(f"  Positive cases: {cvd_positive} ({cvd_positive / medical_count * 100:.1f}%)")
    print(f"  Negative cases: {cvd_negative} ({cvd_negative / medical_count * 100:.1f}%)")

    client.close()
    print("\n MongoDB database test passed!\n")


def test_stored_procedure():
    print("testing stored procedure (Risk Assessment)")


    test_patient_ids = [0, 100, 500, 1000, 5000]

    for patient_id in test_patient_ids:
        result = calculate_risk_score(patient_id)
        if result:
            print(f"\nPatient {patient_id}:")
            print(f"  Risk Score: {result['risk_score']}")
            print(f"  Risk Level: {result['risk_level']}")
        else:
            print(f"\nPatient {patient_id}: Not found")

    conn = sqlite3.connect('cardiovascular.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM risk_assessments")
    count = cursor.fetchone()[0]
    conn.close()

    print(f"\nTotal risk assessments stored: {count}")
    print("Stored procedure test passed!\n")


def test_trigger():
    print("testing trigger")

    conn = sqlite3.connect('cardiovascular.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM diagnosis_log WHERE action_type = 'INSERT'")
    insert_count = cursor.fetchone()[0]
    print(f"\nINSERT actions logged: {insert_count}")

    cursor.execute("""
    INSERT INTO diagnoses (patient_id, cardiovascular_disease)
    VALUES (99999, 1)
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM diagnosis_log WHERE patient_id = 99999")
    new_log_count = cursor.fetchone()[0]
    print(f"New diagnosis inserted for patient 99999")
    print(f"Trigger automatically created {new_log_count} log entry")

    cursor.execute("DELETE FROM diagnoses WHERE patient_id = 99999")
    conn.commit()

    cursor.execute("""
    SELECT log_id, action_type, cardiovascular_disease, action_timestamp
    FROM diagnosis_log
    ORDER BY log_id DESC
    LIMIT 3
    """)
    recent_logs = cursor.fetchall()
    print(f"\nRecent log entries:")
    for log in recent_logs:
        print(f"  Log ID: {log[0]}, Action: {log[1]}, CVD: {log[2]}, Time: {log[3]}")

    conn.close()
    print("\nTrigger test passed!\n")


def main():
    try:
        test_sqlite_database()
    except Exception as e:
        print(f"\nSQLite test failed: {e}\n")

    try:
        test_mongodb_database()
    except Exception as e:
        print(f"\n mongoDB test failed: {e}\n")


    try:
        test_stored_procedure()
    except Exception as e:
        print(f"\nStored procedure test failed: {e}\n")

    try:
        test_trigger()
    except Exception as e:
        print(f"\nTrigger test failed: {e}\n")

    print("Test complete")


if __name__ == '__main__':
    main()