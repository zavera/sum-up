DELIMITER $$

CREATE PROCEDURE populate_patient_details_report()
BEGIN
DELETE FROM patient_summary;

INSERT INTO patient_summary (
    subject_id, mrn, first_name, last_name, birthdate, gender,
    total_booked_visits, first_visit, last_visit
)
SELECT
    s.id AS subject_id,
    sm.mrn AS mrn,
    s.first_name,
    s.last_name,
    s.birthdate,
    s.gender,
    COUNT(bv.id) AS total_booked_visits,
    MIN(bv.scheduled_start_time) AS first_visit,
    MAX(bv.scheduled_end_time) AS last_visit
FROM
    subject s
        LEFT JOIN
    subject_mrn sm ON s.id = sm.subject
        LEFT JOIN
    booked_visit bv ON sm.id = bv.subject_mrn
GROUP BY
    s.id, sm.mrn, s.first_name, s.last_name, s.birthdate, s.gender;
END$$

DELIMITER ;
