DELIMITER $$

CREATE TRIGGER after_booked_resource_insert
    AFTER INSERT ON booked_resource
    FOR EACH ROW
BEGIN
    CALL populate_resource_level_report();
    END$$

    CREATE TRIGGER after_booked_resource_update
        AFTER UPDATE ON booked_resource
        FOR EACH ROW
    BEGIN
        CALL populate_resource_level_report();
        END$$

        CREATE TRIGGER after_booked_resource_delete
            AFTER DELETE ON booked_resource
            FOR EACH ROW
        BEGIN
            CALL populate_resource_level_report();
            END$$

            -- If you want to also refresh on resource name changes:
            CREATE TRIGGER after_resource_update
                AFTER UPDATE ON resource
                FOR EACH ROW
            BEGIN
                CALL populate_resource_level_report();
                END$$

                DELIMITER ;
