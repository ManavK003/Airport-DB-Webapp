-- 1. Airlines
CREATE TABLE airlines (
  airline_id        INTEGER      PRIMARY KEY,
  name              VARCHAR(100) NOT NULL,
  country           VARCHAR( 50 )
);

-- 2. Aircraft
CREATE TABLE aircraft (
  aircraft_id       INTEGER      PRIMARY KEY,
  manufacturer      VARCHAR(50)  NOT NULL,
  model             VARCHAR(50)  NOT NULL,
  aircraft_type     VARCHAR(50),
  capacity          INTEGER
);

-- 3. Airports
CREATE TABLE airports (
  airport_id        INTEGER      PRIMARY KEY,
  location          VARCHAR(100) NOT NULL,
  country           VARCHAR( 50 ) NOT NULL
);

-- 4. Runways
CREATE TABLE runways (
  runway_id         INTEGER      PRIMARY KEY,
  airport_id        INTEGER      NOT NULL
    REFERENCES airports(airport_id) ON DELETE CASCADE,
  length            INTEGER      NOT NULL,
  surface_type      VARCHAR(50)  NOT NULL
);

-- 5. Weather Conditions
CREATE TABLE weather_conditions (
  weather_id        INTEGER      PRIMARY KEY,
  temperature       DECIMAL(5,2) NOT NULL,
  wind_speed        DECIMAL(5,2) NOT NULL,
  visibility        VARCHAR(50)  NOT NULL
);

-- 6. Pilots
CREATE TABLE pilots (
  pilot_id          INTEGER      PRIMARY KEY,
  name              VARCHAR(100) NOT NULL,
  license_id        VARCHAR(20)  UNIQUE NOT NULL,
  airline_id        INTEGER      NOT NULL
    REFERENCES airlines(airline_id) ON DELETE SET NULL
);

-- 7. Flights
CREATE TABLE flights (
  flight_id         INTEGER      PRIMARY KEY,
  aircraft_id       INTEGER      NOT NULL
    REFERENCES aircraft(aircraft_id) ON DELETE RESTRICT,
  arrival_time      TIMESTAMP    NOT NULL,
  airline_id        INTEGER      NOT NULL
    REFERENCES airlines(airline_id) ON DELETE CASCADE
);

-- 8. Delays
CREATE TABLE delays (
  delay_id          INTEGER      PRIMARY KEY,
  flight_id         INTEGER      NOT NULL
    REFERENCES flights(flight_id) ON DELETE CASCADE,
  reason            VARCHAR(255) NOT NULL,
  delay_duration    INTEGER      NOT NULL,
  reported_by       VARCHAR(100) NOT NULL
);

-- 9. Maintenance Logs
CREATE TABLE maintenance_logs (
  maintenance_id    INTEGER      PRIMARY KEY,
  aircraft_id       INTEGER      NOT NULL
    REFERENCES aircraft(aircraft_id) ON DELETE CASCADE,
  date              DATE         NOT NULL,
  technician        VARCHAR(100) NOT NULL,
  description       VARCHAR(100) NOT NULL,
  cost              DECIMAL(10,2)NOT NULL
);

-- 10. Landings (fact table)
CREATE TABLE landings (
  landing_id            INTEGER      PRIMARY KEY,
  activity_period       VARCHAR(6)   NOT NULL,
  operating_airline     VARCHAR(100) NOT NULL,
  operating_iata        VARCHAR(3),
  published_airline     VARCHAR(100),
  published_iata        VARCHAR(3),
  geo_summary           VARCHAR(20),
  geo_region            VARCHAR(50),
  landing_aircraft_type VARCHAR(50),
  body_type             VARCHAR(50),
  aircraft_manufacturer VARCHAR(50),
  aircraft_model        VARCHAR(50),
  aircraft_version      VARCHAR(50),
  landing_count         INTEGER,
  total_landed_weight   BIGINT,
  -- foreign keys into dimensions:
  airline_id            INTEGER      NOT NULL
    REFERENCES airlines(airline_id),
  airport_id            INTEGER      NOT NULL
    REFERENCES airports(airport_id),
  runway_id             INTEGER      NOT NULL
    REFERENCES runways(runway_id),
  weather_id            INTEGER      NOT NULL
    REFERENCES weather_conditions(weather_id),
  flight_id             INTEGER      NOT NULL
    REFERENCES flights(flight_id),
  pilot_id              INTEGER      NOT NULL
    REFERENCES pilots(pilot_id),
  delay_id              INTEGER      NOT NULL
    REFERENCES delays(delay_id),
  maintenance_id        INTEGER      NOT NULL
    REFERENCES maintenance_logs(maintenance_id),
  aircraft_capacity     INTEGER
);