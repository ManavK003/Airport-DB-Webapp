-- DML (Insert, Update, Delete)
-- 1) Insert a new airline

INSERT INTO airlines (airline_id, name, country)
VALUES (5000, 'New Skies Air', 'Brazil');

SELECT * FROM airlines
WHERE airline_id = 5000;



-- 2) Update an existing maintenance_cost


UPDATE maintenance_logs
SET cost = cost * 1.10
WHERE date < '2020-01-01';

SELECT maintenance_id, date, cost
FROM maintenance_logs
WHERE date < '2020-01-01';

-- 3) Delete old delays reported by 'Security'

DELETE FROM delays
WHERE reported_by = 'Security';

SELECT * FROM delays
WHERE reported_by = 'Security';


--B) Four+ SELECTs (joins, group‐by, subquery, order‐by)
-- 4) Join landings → airlines, list top 5 busiest airlines by total landings
SELECT a.name, SUM(l.landing_count) AS total_landings
FROM landings l
JOIN airlines a ON l.airline_id = a.airline_id
GROUP BY a.name
ORDER BY total_landings DESC
LIMIT 5;

-- 5) For each aircraft manufacturer, average landed weight
SELECT aircraft_manufacturer, AVG(total_landed_weight) AS avg_weight
FROM landings
GROUP BY aircraft_manufacturer
ORDER BY avg_weight DESC;

-- 6) Find all flights arriving after 10 PM in 2024
SELECT f.flight_id, f.arrival_time, a.name AS airline
FROM flights f
JOIN airlines a ON f.airline_id = a.airline_id
WHERE arrival_time >= '2024-01-01'
  AND EXTRACT(HOUR FROM arrival_time) >= 22
ORDER BY arrival_time;

-- 7) Subquery: landings whose count exceeds the global average
SELECT landing_id, operating_airline, landing_count
FROM landings
WHERE landing_count > (
  SELECT AVG(landing_count) FROM landings
);

-- 8) Count landings per runway surface type
SELECT r.surface_type, COUNT(*) AS uses
FROM landings l
JOIN runways r ON l.runway_id = r.runway_id
GROUP BY r.surface_type
ORDER BY uses DESC;


-- --C) Stored Procedure 
-- -- 9) A simple PL/pgSQL function to insert a new pilot
CREATE OR REPLACE FUNCTION add_pilot(p_id INT, p_name TEXT, p_license TEXT, p_airline INT)
RETURNS VOID AS $$
BEGIN
  INSERT INTO pilots(pilot_id, name, license_id, airline_id)
  VALUES (p_id, p_name, p_license, p_airline);
END;
$$ LANGUAGE plpgsql;

-- -- Usage:
SELECT add_pilot(3001, 'Alex Marathon', 'LIC99999', 1);


SELECT * FROM pilots
WHERE pilot_id = 3001;


-- 10) Delete inserted row:

DELETE FROM airlines
WHERE airline_id = 5000;

SELECT * FROM airlines
WHERE airline_id = 5000;


-- 11) Update a pilot's airline
CREATE OR REPLACE FUNCTION update_pilot_airline(p_id INT, new_airline INT)
RETURNS VOID AS $$
BEGIN
  UPDATE pilots
  SET airline_id = new_airline
  WHERE pilot_id = p_id;
END;
$$ LANGUAGE plpgsql;


SELECT update_pilot_airline(3001, 23);

SELECT pilot_id, name, airline_id
FROM pilots
WHERE pilot_id = 3001;


-- 12) Delete a pilot by pilot_id
CREATE OR REPLACE FUNCTION delete_pilot(p_id INT)
RETURNS VOID AS $$
BEGIN
  DELETE FROM pilots
  WHERE pilot_id = p_id;
END;
$$ LANGUAGE plpgsql;


SELECT delete_pilot(3001);


SELECT *
FROM pilots
WHERE pilot_id = 3001;

