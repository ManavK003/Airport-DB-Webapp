
-- LOAD DATA: real_airports.csv
-- Make sure the CSV file is placed in the /tmp folder or adjust the path accordingly.

COPY airports(airport_id, name, city, country, iata, icao, latitude, longitude)
FROM '/tmp/real_airports.csv'
WITH (FORMAT csv, HEADER true);
