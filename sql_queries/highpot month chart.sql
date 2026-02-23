SELECT strftime('%d', date(effective_datetime)) as day, COUNT(DISTINCT patient_id) FROM observations o
WHERE code = 'Potassium'  AND 
value > 5 AND date(effective_datetime) BETWEEN '2017-01-01' AND '2017-01-31' GROUP BY day