CREATE TABLE appointment_summary (
                                     appointment_id INT PRIMARY KEY,
                                     patient_id INT,
                                     patient_name VARCHAR(255),
                                     patient_mrn VARCHAR(50),
                                     scheduled_start_time DATETIME,
                                     scheduled_end_time DATETIME,
                                     visit_type VARCHAR(255),
                                     visit_template VARCHAR(255),
                                     study_name VARCHAR(255),
                                     appointment_status VARCHAR(255),
                                     appointment_status_reason VARCHAR(255),
                                     comment TEXT
);
