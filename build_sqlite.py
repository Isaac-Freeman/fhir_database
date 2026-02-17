
import sqlite3
import os
import numpy as np

conn = sqlite3.connect("ehr.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS medication")

cur.execute("DROP TABLE IF EXISTS patient")

cur.execute("DROP TABLE IF EXISTS report")



path = os.path.join(os.getcwd(), 'diagnostic_reports.npy')
reports = np.load(path, allow_pickle = True)

cur.execute("""
CREATE TABLE IF NOT EXISTS report (
    report_id TEXT PRIMARY KEY,
    patient_id TEXT,
    encounter_id TEXT,
    report_code TEXT,
    report_name TEXT,
    lab_name TEXT,
    results TEXT,
    date_issued TEXT
)
""")

rows = [
    (d["report_id"], d["patient_id"], d["encounter_id"], d["report_code"], d["report_name"], d["lab_name"], d["results"], d["date_issued"])
    for d in reports
]

cur.executemany(
    "INSERT INTO report (report_id, patient_id, encounter_id, report_code, report_name, lab_name, results, date_issued) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    rows
)

del reports
del rows

cur.execute("""
CREATE TABLE IF NOT EXISTS medication(
    encounter_id TEXT,
    patient_id TEXT,
    code TEXT,
    description TEXT
)
""")
path = os.path.join(os.getcwd(), 'medications.npy')
meds = np.load(path, allow_pickle = True)


rows = [
    (d["encounter_id"], d["patient_id"], d["code"], d["description"])
    for d in meds
]


cur.executemany(
    "INSERT INTO medication (encounter_id, patient_id, code, description) VALUES (?, ?, ?, ?)",
    rows
)


del meds
del rows

cur.execute("""
CREATE TABLE IF NOT EXISTS patient(
    patient_id TEXT PRIMARY KEY,
    name TEXT,
    birth_date TEXT,
    race TEXT,
    ethnicity TEXT,
    marital_status TEXT,
    address TEXT
)
""")

path = os.path.join(os.getcwd(), 'patients.npy')
patients = np.load(path, allow_pickle = True)


rows = [
    (d["patient_id"], d["name"], d["birth_date"], d["race"].get("coding", {})[0].get("display", {}), d["ethnicity"].get("coding", {})[0].get("display", {}), d["marital_status"], d["address"])
    for d in patients
]


cur.executemany(
    "INSERT INTO patient (patient_id, name, birth_date, race, ethnicity, marital_status, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
    rows
)




conn.commit()
conn.close()
