-- Log table for failed-flight inserts
CREATE TABLE failed_tx_logs (
  log_id SERIAL PRIMARY KEY,
  attempted_flight INT,
  log_time       TIMESTAMP DEFAULT NOW(),
  reason         TEXT
);


-- DROP TRIGGER fail_before_insert ON flights;

-- Trigger function: always fails and logs

CREATE OR REPLACE FUNCTION trg_fail_handling()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO failed_tx_logs(attempted_flight, reason)
    VALUES (NEW.flight_id, 'Simulated failure');
  RAISE EXCEPTION 'Simulated insert error for flight %', NEW.flight_id;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- -- Attach BEFORE INSERT trigger on flights

CREATE TRIGGER fail_before_insert
BEFORE INSERT ON flights
FOR EACH ROW
EXECUTE FUNCTION trg_fail_handling();


BEGIN;

INSERT INTO flights (flight_id, aircraft_id, arrival_time, airline_id)
VALUES (999999, 123, '2025-05-01 10:00:00', 1);

COMMIT;

-- ROLLBACK;

SELECT * FROM failed_tx_logs;