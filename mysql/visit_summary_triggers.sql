DELIMITER $$

CREATE TRIGGER after_visit_template_insert
    AFTER INSERT ON visit_template
    FOR EACH ROW
BEGIN
    CALL populate_visit_details_report();
    END$$

    CREATE TRIGGER after_visit_template_update
        AFTER UPDATE ON visit_template
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
