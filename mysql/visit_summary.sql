DELIMITER $$

CREATE PROCEDURE populate_visit_details_report()
BEGIN
DELETE FROM visit_summary;

INSERT INTO visit_summary (
    visit_id, visit_name, study_id, study_name,
    total_bookings, unique_subjects, first_scheduled, last_scheduled
)
SELECT
    vt.id AS visit_id,
    vt.name AS visit_name,
    bv.study AS study_id,
    s.name AS study_name,
    COUNT(bv.id) AS total_bookings,
    COUNT(DISTINCT sm.subject) AS unique_subjects,
    MIN(bv.scheduled_start_time) AS first_scheduled,
    MAX(bv.scheduled_end_time) AS last_scheduled
FROM
    visit_template vt
        LEFT JOIN
    booked_visit bv ON vt.id = bv.visit_template
        LEFT JOIN
    study s ON bv.study = s.id
        LEFT JOIN
    subject_mrn sm ON bv.subject_mrn = sm.id
GROUP BY
    vt.id, vt.name, bv.study, s.name;
END$$

DELIMITER ;
