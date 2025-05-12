DELIMITER $$

CREATE PROCEDURE populate_study_details_report()
BEGIN
DELETE FROM study_summary;

INSERT INTO study_summary (
    study_id, local_id, irb, name, status,
    total_subjects, total_booked_visits, first_visit, last_visit
)
SELECT
    s.id AS study_id,
    s.local_id,
    s.irb,
    s.name,
    s.status,
    COUNT(DISTINCT subj.id) AS total_subjects,
    COUNT(bv.id) AS total_booked_visits,
    MIN(bv.scheduled_start_time) AS first_visit,
    MAX(bv.scheduled_end_time) AS last_visit
FROM
    study s
        LEFT JOIN
    study_subject ss ON s.id = ss.study
        LEFT JOIN
    subject subj ON ss.subject = subj.id
        LEFT JOIN
    booked_visit bv ON s.id = bv.study
GROUP BY
    s.id, s.local_id, s.irb, s.name, s.status;
END$$

DELIMITER ;
