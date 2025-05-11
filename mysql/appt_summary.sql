DELIMITER $$

CREATE PROCEDURE RefreshAppointmentSummary()
BEGIN
    -- Clear the staging table before inserting new data
DELETE FROM appointment_summary;

-- Optionally reset AUTO_INCREMENT (if needed and allowed)
-- ALTER TABLE appointment_summary AUTO_INCREMENT = 1;

-- Insert the latest appointment data
INSERT INTO appointment_summary (
    appointment_id,
    patient_id,
    patient_name,
    patient_mrn,
    scheduled_start_time,
    scheduled_end_time,
    visit_type,
    visit_template,
    study_name,
    appointment_status,
    appointment_status_reason,
    comment
)
SELECT
    bv.id AS appointment_id,
    s.id AS patient_id,
    CONCAT(s.first_name, ' ', s.last_name) AS patient_name,
    sm.mrn AS patient_mrn,
    bv.scheduled_start_time,
    bv.scheduled_end_time,
    vs.name AS visit_type,
    vt.name AS visit_template,
    st.name AS study_name,
    ast.name AS appointment_status,
    asr.name AS appointment_status_reason,
    bv.comment
FROM
    booked_visit bv
        LEFT JOIN subject_mrn sm ON bv.subject_mrn = sm.id
        LEFT JOIN subject s ON sm.subject = s.id
        LEFT JOIN appointment_status ast ON bv.appointment_status = ast.id
        LEFT JOIN appointment_status_reason asr ON bv.appointment_status_reason = asr.id
        LEFT JOIN visit_template vt ON bv.visit_template = vt.id
        LEFT JOIN study st ON bv.study = st.id
        LEFT JOIN visit_type vs ON bv.visit_type = vs.id;
END$$

DELIMITER ;
