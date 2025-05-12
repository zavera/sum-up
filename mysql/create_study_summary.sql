CREATE TABLE IF NOT EXISTS study_summary (
                                                            study_id INT NOT NULL PRIMARY KEY,
                                                            local_id VARCHAR(255),
    irb VARCHAR(255),
    name VARCHAR(255),
    status VARCHAR(64),
    total_subjects INT,
    total_booked_visits INT,
    first_visit DATETIME,
    last_visit DATETIME
    );
