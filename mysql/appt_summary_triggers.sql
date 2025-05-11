DELIMITER $$

CREATE TRIGGER tr_after_insert_booked_visit
    AFTER INSERT ON booked_visit
    FOR EACH ROW
BEGIN
    CALL RefreshAppointmentSummary();
    END$$

    CREATE TRIGGER tr_after_update_booked_visit
        AFTER UPDATE ON booked_visit
        FOR EACH ROW
    BEGIN
        CALL RefreshAppointmentSummary();
        END$$

        CREATE TRIGGER tr_after_delete_booked_visit
            AFTER DELETE ON booked_visit
            FOR EACH ROW
        BEGIN
            CALL RefreshAppointmentSummary();
            END$$

            DELIMITER ;
