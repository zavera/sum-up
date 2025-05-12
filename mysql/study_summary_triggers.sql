DELIMITER $$

CREATE TRIGGER after_study_insert
    AFTER INSERT ON study
    FOR EACH ROW
BEGIN
    CALL populate_study_details_report();
    END$$

    CREATE TRIGGER after_study_update
        AFTER UPDATE ON study
        FOR EACH ROW
    BEGIN
        CALL populate_study_details_report();
        END$$

        CREATE TRIGGER after_study_subject_insert
            AFTER INSERT ON study_subject
            FOR EACH ROW
        BEGIN
            CALL populate_study_details_report();
            END$$

            CREATE TRIGGER after_study_subject_update
                AFTER UPDATE ON study_subject
                FOR EACH ROW
            BEGIN
                CALL populate_study_details_report();
                END$$

                CREATE TRIGGER after_booked_visit_insert
                    AFTER INSERT ON booked_visit
                    FOR EACH ROW
                BEGIN
                    CALL populate_study_details_report();
                    END$$

                    CREATE TRIGGER after_booked_visit_update
                        AFTER UPDATE ON booked_visit
                        FOR EACH ROW
                    BEGIN
                        CALL populate_study_details_report();
                        END$$

                        DELIMITER ;
