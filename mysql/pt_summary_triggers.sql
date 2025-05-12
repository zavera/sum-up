DELIMITER $$

CREATE TRIGGER after_subject_insert
    AFTER INSERT ON subject
    FOR EACH ROW
BEGIN
    CALL populate_patient_details_report();
    END$$

    CREATE TRIGGER after_subject_update
        AFTER UPDATE ON subject
        FOR EACH ROW
    BEGIN
        CALL populate_patient_details_report();
        END$$

        CREATE TRIGGER after_subject_mrn_insert
            AFTER INSERT ON subject_mrn
            FOR EACH ROW
        BEGIN
            CALL populate_patient_details_report();
            END$$

            CREATE TRIGGER after_subject_mrn_update
                AFTER UPDATE ON subject_mrn
                FOR EACH ROW
            BEGIN
                CALL populate_patient_details_report();
                END$$

                CREATE TRIGGER after_booked_visit_insert
                    AFTER INSERT ON booked_visit
                    FOR EACH ROW
                BEGIN
                    CALL populate_patient_details_report();
                    END$$

                    CREATE TRIGGER after_booked_visit_update
                        AFTER UPDATE ON booked_visit
                        FOR EACH ROW
                    BEGIN
                        CALL populate_patient_details_report();
                        END$$

                        DELIMITER ;
