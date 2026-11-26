BEGIN;
DROP TABLE IF EXISTS aerovista.flights_clean CASCADE;
CREATE TABLE aerovista.flights_clean AS
WITH typed AS (
 SELECT
  TRIM(flight_id) AS flight_id, TRIM(flight_number) AS flight_number,
  scheduled_departure::timestamp AS scheduled_departure,
  UPPER(TRIM(origin_airport)) AS origin_airport, UPPER(TRIM(destination_airport)) AS destination_airport,
  TRIM(origin_city) AS origin_city, TRIM(destination_city) AS destination_city,
  TRIM(destination_country) AS destination_country, TRIM(destination_region) AS destination_region,
  COALESCE(NULLIF(TRIM(aircraft_type),''),'Unknown') AS aircraft_type,
  seat_capacity::int, distance_miles::int, TRIM(season) AS season,
  TRIM(departure_period) AS departure_period, TRIM(weather_condition) AS weather_condition,
  INITCAP(TRIM(airport_congestion)) AS airport_congestion,
  NULLIF(departure_delay_minutes::int,-1) AS departure_delay_minutes,
  turnaround_minutes::int, TRIM(delay_cause) AS delay_cause, INITCAP(TRIM(flight_status)) AS flight_status,
  TRIM(cancellation_reason) AS cancellation_reason,
  CASE LOWER(TRIM(on_time_flag)) WHEN 'yes' THEN TRUE WHEN 'no' THEN FALSE ELSE NULL END AS on_time_flag,
  passengers::int, economy_passengers::int, business_passengers::int, load_factor::numeric(7,4),
  average_fare_usd::numeric(12,2), passenger_revenue_usd::numeric(16,2),
  ancillary_revenue_usd::numeric(16,2), cargo_revenue_usd::numeric(16,2), total_revenue_usd::numeric(16,2),
  fuel_cost_usd::numeric(16,2), crew_cost_usd::numeric(16,2), airport_fees_usd::numeric(16,2),
  maintenance_cost_usd::numeric(16,2), passenger_compensation_usd::numeric(16,2),
  other_operating_cost_usd::numeric(16,2), total_operating_cost_usd::numeric(16,2),
  operating_profit_usd::numeric(16,2), mishandled_bags::int,
  NULLIF(customer_satisfaction,'')::numeric(2,1) AS customer_satisfaction,
  ROW_NUMBER() OVER(PARTITION BY TRIM(flight_id) ORDER BY scheduled_departure::timestamp DESC, ctid DESC) AS duplicate_rank
 FROM aerovista.flights_raw
), valid AS (
 SELECT * FROM typed
 WHERE duplicate_rank=1 AND flight_id ~ '^AV-[0-9]{7}$'
   AND origin_airport ~ '^[A-Z]{3}$' AND destination_airport ~ '^[A-Z]{3}$'
   AND seat_capacity BETWEEN 100 AND 500 AND passengers BETWEEN 0 AND seat_capacity
   AND load_factor BETWEEN 0 AND 1
   AND (customer_satisfaction BETWEEN 1 AND 5 OR customer_satisfaction IS NULL)
)
SELECT
 flight_id, flight_number, scheduled_departure, scheduled_departure::date AS flight_date,
 DATE_TRUNC('month',scheduled_departure)::date AS month_start,
 EXTRACT(YEAR FROM scheduled_departure)::int AS year,
 TO_CHAR(scheduled_departure,'Mon') AS month_name, TO_CHAR(scheduled_departure,'Dy') AS day_name,
 origin_airport, destination_airport, origin_airport||'–'||destination_airport AS route,
 origin_city, destination_city, destination_country, destination_region, aircraft_type,
 seat_capacity, distance_miles, season, departure_period, weather_condition, airport_congestion,
 departure_delay_minutes, turnaround_minutes, delay_cause, flight_status, cancellation_reason,
 on_time_flag, flight_status='Cancelled' AS cancelled_flag, passengers, economy_passengers,
 business_passengers, load_factor, average_fare_usd, passenger_revenue_usd,
 ancillary_revenue_usd, cargo_revenue_usd, total_revenue_usd, fuel_cost_usd, crew_cost_usd,
 airport_fees_usd, maintenance_cost_usd, passenger_compensation_usd, other_operating_cost_usd,
 total_operating_cost_usd, operating_profit_usd,
 ROUND(operating_profit_usd/NULLIF(total_revenue_usd,0),4) AS operating_margin_pct,
 mishandled_bags, customer_satisfaction
FROM valid;
ALTER TABLE aerovista.flights_clean ADD PRIMARY KEY(flight_id);
CREATE INDEX idx_flight_date ON aerovista.flights_clean(flight_date);
CREATE INDEX idx_route ON aerovista.flights_clean(route);
CREATE INDEX idx_aircraft ON aerovista.flights_clean(aircraft_type);
COMMIT;

-- Terminal data-quality checks: every result should be zero.
SELECT COUNT(*)-COUNT(DISTINCT flight_id) AS duplicate_ids,
 COUNT(*) FILTER(WHERE departure_delay_minutes<0) AS negative_delays,
 COUNT(*) FILTER(WHERE passengers>seat_capacity) AS impossible_capacity,
 COUNT(*) FILTER(WHERE customer_satisfaction NOT BETWEEN 1 AND 5) AS invalid_satisfaction
FROM aerovista.flights_clean;
