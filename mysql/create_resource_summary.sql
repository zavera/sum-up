CREATE TABLE IF NOT EXISTS resource_summary (
                                                             resource_id INT NOT NULL PRIMARY KEY,
                                                             resource_name VARCHAR(255) NOT NULL,
    total_bookings INT NOT NULL,
    total_duration_minutes INT,
    first_booking DATETIME,
    last_booking DATETIME
    );
