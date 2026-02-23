SELECT COUNT(DISTINCT o.patient_id) FROM observations o
WHERE code = 'Hemoglobin A1c/Hemoglobin.total in Blood'  AND 
value < 8