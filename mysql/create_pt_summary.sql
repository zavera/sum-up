CREATE TABLE IF NOT EXISTS patient_summary (
                                                              subject_id INT NOT NULL PRIMARY KEY,
                                                              mrn VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    birthdate DATE,
    gender VARCHAR(32),
    total_booked_visits INT,
    first_visit DATETIME,
    last_visit DATETIME
    );
