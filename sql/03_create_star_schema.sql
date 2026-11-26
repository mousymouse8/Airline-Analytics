DROP VIEW IF EXISTS aerovista.fact_flights CASCADE;
CREATE VIEW aerovista.fact_flights AS SELECT * FROM aerovista.flights_clean;

DROP MATERIALIZED VIEW IF EXISTS aerovista.dim_date;
CREATE MATERIALIZED VIEW aerovista.dim_date AS
SELECT d::date AS date, EXTRACT(YEAR FROM d)::int AS year,
 'Q'||EXTRACT(QUARTER FROM d)::int AS quarter, EXTRACT(MONTH FROM d)::int AS month_number,
 TO_CHAR(d,'Month') AS month_name, DATE_TRUNC('month',d)::date AS month_start,
 EXTRACT(WEEK FROM d)::int AS week_number, TO_CHAR(d,'Day') AS day_name,
 EXTRACT(ISODOW FROM d) IN (5,6,7) AS is_weekend
FROM GENERATE_SERIES((SELECT MIN(flight_date) FROM aerovista.flights_clean),
                     (SELECT MAX(flight_date) FROM aerovista.flights_clean),'1 day') d;

DROP MATERIALIZED VIEW IF EXISTS aerovista.dim_route;
CREATE MATERIALIZED VIEW aerovista.dim_route AS
SELECT route, origin_airport, destination_airport,
 PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY distance_miles)::int AS distance_miles,
 CASE WHEN PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY distance_miles)<=500 THEN 'Short haul'
      WHEN PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY distance_miles)<=1500 THEN 'Medium haul'
      WHEN PERCENTILE_CONT(.5) WITHIN GROUP(ORDER BY distance_miles)<=3000 THEN 'Long haul'
      ELSE 'Ultra-long haul' END AS distance_band
FROM aerovista.flights_clean GROUP BY 1,2,3;

DROP MATERIALIZED VIEW IF EXISTS aerovista.dim_aircraft;
CREATE MATERIALIZED VIEW aerovista.dim_aircraft AS
SELECT aircraft_type, MAX(seat_capacity) AS seat_capacity
FROM aerovista.flights_clean GROUP BY 1;
