EXPLAIN ANALYZE
SELECT * FROM landings
WHERE operating_airline = 'Delta Air Lines';



-- Results for first problem with no indexing:

-- "Seq Scan on landings  (cost=0.00..811.59 rows=1 width=158) (actual time=5.473..5.473 rows=0 loops=1)"
-- "  Filter: ((operating_airline)::text = 'Delta Air Lines'::text)"
-- "  Rows Removed by Filter: 22047"
-- "Planning Time: 0.539 ms"
-- "Execution Time: 5.548 ms"


CREATE INDEX idx_landings_airline
  ON landings(operating_airline);


EXPLAIN ANALYZE
SELECT * FROM landings
WHERE operating_airline = 'Delta Air Lines';


-- Improved results for first problem with indexing:

-- "Index Scan using idx_landings_airline on landings  (cost=0.29..8.30 rows=1 width=158) (actual time=0.046..0.046 rows=0 loops=1)"
-- "  Index Cond: ((operating_airline)::text = 'Delta Air Lines'::text)"
-- "Planning Time: 0.986 ms"
-- "Execution Time: 0.440 ms"



EXPLAIN ANALYZE
SELECT aircraft_id, COUNT(*) FROM flights
GROUP BY aircraft_id
HAVING COUNT(*) > 100;



-- Results for second problem with no indexing:

-- "HashAggregate  (cost=471.71..509.14 rows=998 width=12) (actual time=26.908..26.910 rows=0 loops=1)"
-- "  Group Key: aircraft_id"
-- "  Filter: (count(*) > 100)"
-- "  Batches: 1  Memory Usage: 369kB"
-- "  Rows Removed by Filter: 2995"
-- "  ->  Seq Scan on flights  (cost=0.00..361.47 rows=22047 width=4) (actual time=0.278..16.621 rows=22047 loops=1)"
-- "Planning Time: 0.898 ms"
-- "Execution Time: 27.837 ms"


-- DROP INDEX idx_flights_aircraft;



CREATE INDEX idx_flights_aircraft
  ON flights(aircraft_id);

EXPLAIN ANALYZE
SELECT aircraft_id, COUNT(*) FROM flights
GROUP BY aircraft_id
HAVING COUNT(*) > 100;


-- Improved results in terms of execution time for second problem with indexing:

-- "HashAggregate  (cost=471.71..509.14 rows=998 width=12) (actual time=9.826..9.827 rows=0 loops=1)"
-- "  Group Key: aircraft_id"
-- "  Filter: (count(*) > 100)"
-- "  Batches: 1  Memory Usage: 369kB"
-- "  Rows Removed by Filter: 2995"
-- "  ->  Seq Scan on flights  (cost=0.00..361.47 rows=22047 width=4) (actual time=0.013..2.395 rows=22047 loops=1)"
-- "Planning Time: 0.648 ms"
-- "Execution Time: 10.308 ms"

-- DROP INDEX idx_delays_duration;


EXPLAIN ANALYZE
SELECT * FROM delays
WHERE delay_duration > 200
ORDER BY delay_duration DESC;

-- Results for third problem with no indexing:

-- "Sort  (cost=645.43..654.44 rows=3603 width=25) (actual time=9.971..10.239 rows=3588 loops=1)"
-- "  Sort Key: delay_duration DESC"
-- "  Sort Method: quicksort  Memory: 257kB"
-- "  ->  Seq Scan on delays  (cost=0.00..432.59 rows=3603 width=25) (actual time=0.242..8.883 rows=3588 loops=1)"
-- "        Filter: (delay_duration > 200)"
-- "        Rows Removed by Filter: 18459"
-- "Planning Time: 0.721 ms"
-- "Execution Time: 10.418 ms"




CREATE INDEX idx_delays_duration
  ON delays(delay_duration);

EXPLAIN ANALYZE
SELECT * FROM delays
WHERE delay_duration > 200
ORDER BY delay_duration DESC;


-- Improved results in terms of execution time and cost for third problem with indexing:

-- "Sort  (cost=459.10..468.10 rows=3603 width=25) (actual time=1.983..2.293 rows=3588 loops=1)"
-- "  Sort Key: delay_duration DESC"
-- "  Sort Method: quicksort  Memory: 257kB"
-- "  ->  Bitmap Heap Scan on delays  (cost=44.21..246.25 rows=3603 width=25) (actual time=0.477..1.268 rows=3588 loops=1)"
-- "        Recheck Cond: (delay_duration > 200)"
-- "        Heap Blocks: exact=157"
-- "        ->  Bitmap Index Scan on idx_delays_duration  (cost=0.00..43.31 rows=3603 width=0) (actual time=0.448..0.449 rows=3588 loops=1)"
-- "              Index Cond: (delay_duration > 200)"
-- "Planning Time: 0.794 ms"
-- "Execution Time: 2.828 ms"