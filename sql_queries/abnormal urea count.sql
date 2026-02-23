SELECT COUNT(DISTINCT o.patient_id) FROM observations o, patient p
WHERE o.patient_id = p.patient_id AND code = 'Urea Nitrogen'