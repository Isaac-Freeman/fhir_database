import pandas
import numpy as np
import kagglehub
from kagglehub import KaggleDatasetAdapter
import json
import os
FHIR_DIR = os.path.join(os.getcwd(), "data")
lab_tests_of_interest = [
    "Red Blood Cell Count", "White Blood Cell Count", "Hemoglobin", "Hematocrit", "Platelet Count",
    "Mean Corpuscular Volume", "Mean Corpuscular Hemoglobin", "Mean Corpuscular Hemoglobin Concentration",
    "Glucose", "Sodium", "Potassium", "Calcium", "Chloride", "Carbon Dioxide", "Blood Urea Nitrogen", "Creatinine",
    "Alanine Aminotransferase", "Aspartate Aminotransferase", "Alkaline Phosphatase", "Bilirubin",
    "Cholesterol", "HDL", "LDL", "Triglycerides",
    "Vitamin D", "Iron", "C-Reactive Protein", "Erythrocyte Sedimentation Rate", "Thyroid Stimulating Hormone"
]
normalized_targets = set(test.lower() for test in lab_tests_of_interest)
patients, encounters, conditions, medications, observations, diagnostic_reports = [], [], [], [], [], []
def extract_extension_value(resource, url_match):
    for ext in resource.get("extension", []):
        if ext.get("url") == url_match:
            val_key = next((k for k in ext.keys() if k.startswith("value")), None)
            return ext[val_key] if val_key else None
    return None

def extract_patient_name(resource):
    names = resource.get("name", [])
    if names:
        name = names[0]
        given = " ".join(name.get("given", []))
        family = name.get("family", "")
        return f"{given} {family}"
    return None
pat_list = np.load("patients_samp.npy", allow_pickle=True)

id_list = []
for i in range(len(pat_list)):
    id_list.append(pat_list[i].get("patient_id"))

for root, _, files in os.walk(FHIR_DIR):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data.get("resourceType") == "Bundle":
                        for entry in data.get("entry", []):
                            resource = entry.get("resource", {})
                            r_type = resource.get("resourceType")

                            if r_type == "Patient":
                                patient_id = resource.get("id")
                                if True:
                                    patients.append({
                                        "patient_id": patient_id,
                                        "name": extract_patient_name(resource),
                                        "birth_date": resource.get("birthDate"),
                                        "gender": resource.get("gender"),
                                        "race": extract_extension_value(resource, "http://hl7.org/fhir/StructureDefinition/us-core-race"),
                                        "ethnicity": extract_extension_value(resource, "http://hl7.org/fhir/StructureDefinition/us-core-ethnicity"),
                                        "marital_status": resource.get("maritalStatus", {}).get("coding", [{}])[0].get("code"),
                                        "address": resource.get("address", [{}])[0].get("city", None)
                                    })

                            elif r_type == "Condition":
                                coding = resource.get("code", {}).get("coding", [{}])[0]
                                patient_ref = resource.get("subject", {}).get("reference", "")
                                encounter_ref = resource.get("context", {}).get("reference", "")
                                #if patient_ref.split("/")[-1][9:] in id_list:
                                if True:
                                    conditions.append({
                                        "condition_id": resource.get("id"),
                                        "patient_id": patient_ref.split("/")[-1] if patient_ref else None,
                                        "encounter_id": encounter_ref.split("/")[-1] if encounter_ref else None,
                                        "code": coding.get("code"),
                                        "description": coding.get("display")
                                    })

                            elif r_type == "MedicationRequest":
                                med_code = resource.get("medicationCodeableConcept", {}).get("coding", [{}])[0]
                                patient_ref = resource.get("patient", {}).get("reference", "")
                                #if patient_ref.split("/")[-1][9:] in id_list:
                                if True:
                                    medications.append({
                                        "encounter_id": resource.get("context", {}).get("reference", ""),
                                        "patient_id": patient_ref.split("/")[-1] if patient_ref else None,
                                        "code": med_code.get("code"),
                                        "description": med_code.get("display"),
                                    })

                            elif r_type == "Observation":
                                patient_ref = resource.get("subject", {}).get("reference", "")
                                encounter_ref = resource.get("encounter", {}).get("reference", "")
                                #if patient_ref.split("/")[-1][9:] in id_list:
                                if True:
                                    observations.append({
                                        "obs_id": resource.get("id"),
                                        "patient_id": patient_ref.split("/")[-1] if patient_ref else None,
                                        "encounter_id": encounter_ref.split("/")[-1] if encounter_ref else None,
                                        "code": resource.get("code", {}).get("coding", [{}])[0].get("display"),
                                        "value": resource.get("valueQuantity", {}).get("value"),
                                        "unit": resource.get("valueQuantity", {}).get("unit"),
                                        "interpretation": resource.get("interpretation", [{}])[0].get("text")
                                            if isinstance(resource.get("interpretation", [{}]), list) else None,
                                        "effective_datetime": resource.get("effectiveDateTime")
                                    })

                            elif r_type == "DiagnosticReport":
                                patient_ref = resource.get("subject", {}).get("reference", "")
                                encounter_ref = resource.get("encounter", {}).get("reference", "")
                                report_code = resource.get("code", {}).get("coding", [{}])[0]
                                results_list = resource.get("result", [])
                                result_names = ", ".join(res.get("display", "") for res in results_list if "display" in res)
                                #if patient_ref.split("/")[-1][9:] in id_list:
                                if True:
                                    diagnostic_reports.append({
                                        "report_id": resource.get("id"),
                                        "patient_id": patient_ref.split("/")[-1] if patient_ref else None,
                                        "encounter_id": encounter_ref.split("/")[-1] if encounter_ref else None,
                                        "report_code": report_code.get("code"),
                                        "report_name": report_code.get("display"),
                                        "lab_name": resource.get("performer", [{}])[0].get("display"),
                                        "results": result_names,
                                        "date_issued": resource.get("issued")
                                    })

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
tables = {
    'patients': patients,
    'conditions': conditions,
    'medications': medications,
    'observations': observations,
    'diagnostic_reports': diagnostic_reports
}
for name, arr in tables.items():
    np.save(f"{name}.npy", arr, allow_pickle=True)
