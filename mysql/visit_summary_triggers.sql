DELIMITER $$

CREATE TRIGGER after_visit_insert
    AFTER INSERT ON visit
    FOR EACH ROW
BEGIN
    CALL populate_visit_details_report();
    END$$

    CREATE TRIGGER after_visit_update
        AFTER UPDATE ON visit
        FOR EACH ROW
    BEGIN
        CALL populate_visit_details_report();
        END$$

        CREATE TRIGGER after_booked_visit_insert
            AFTER INSERT ON booked_visit
            FOR EACH ROW
        BEGIN
            CALL populate_visit_details_report();
            END$$

            CREATE TRIGGER after_booked_visit_update
                AFTER UPDATE ON booked_visit
                FOR EACH ROW
            BEGIN
                CALL populate_visit_details_report();
                END$$

                DELIMITER ;
