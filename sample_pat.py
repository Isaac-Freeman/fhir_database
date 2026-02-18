import pandas
import numpy as np
import kagglehub
from kagglehub import KaggleDatasetAdapter
import json
import os
FHIR_DIR = os.path.join(os.getcwd(), "data")

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
def sample_pat_pop(count):
    patients = []

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

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    small = np.random.choice(patients, size=count, replace=False)
    return small
patients = sample_pat_pop(2000)
np.save("patients_samp.npy", patients, allow_pickle=True)

