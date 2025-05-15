
-- CREATE TABLE: airports
DROP TABLE IF EXISTS airports CASCADE;

CREATE TABLE airports (
    airport_id   INTEGER PRIMARY KEY,
    name         VARCHAR(100),
    city         VARCHAR(100),
    country      VARCHAR(100),
    iata         VARCHAR(10),
    icao         VARCHAR(10),
    latitude     FLOAT,
    longitude    FLOAT
);
