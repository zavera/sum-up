DELIMITER $$

CREATE PROCEDURE populate_resource_level_report()
BEGIN
DELETE FROM resource_summary;

INSERT INTO resource_summary(
    resource_id, resource_name, total_bookings, total_duration_minutes, first_booking, last_booking
)
SELECT
    r.id AS resource_id,
    r.name AS resource_name,
    COUNT(br.id) AS total_bookings,
    SUM(br.duration) AS total_duration_minutes,
    MIN(br.scheduled_start_time) AS first_booking,
    MAX(br.scheduled_end_time) AS last_booking
FROM
    resource r
        LEFT JOIN
    booked_resource br ON r.id = br.resource
GROUP BY
    r.id, r.name;
END$$

DELIMITER ;
