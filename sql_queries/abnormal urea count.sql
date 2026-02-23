SELECT COUNT(DISTINCT patient_id) FROM observations o
WHERE code = 'Urea Nitrogen'  AND 
value > 20 or value < 7