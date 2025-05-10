--index
SELECT d.dependent_id AS dep_id, d.first_name, d.last_name, d.relationship, d.employee_id, e.first_name AS emp_first, e.last_name AS emp_last
FROM dependents d
JOIN employees e ON d.employee_id = e.employee_id;

--edit
UPDATE dependents
SET first_name=$, last_name=$, relationship=$
WHERE dependent_id=$;

--delete
DELETE FROM dependents WHERE dependent_id=$;
