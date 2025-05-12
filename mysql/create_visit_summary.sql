CREATE TABLE IF NOT EXISTS visit_summary (
                                                            visit_id INT NOT NULL PRIMARY KEY,
                                                            visit_name VARCHAR(255),
    study_id INT,
    study_name VARCHAR(255),
    total_bookings INT,
    unique_subjects INT,
    first_scheduled DATETIME,
    last_scheduled DATETIME
    );
