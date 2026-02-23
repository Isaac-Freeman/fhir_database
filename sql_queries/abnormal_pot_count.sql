SELECT COUNT(DISTINCT o.patient_id) FROM observations o
WHERE code = 'Potassium'  AND 
value > 5