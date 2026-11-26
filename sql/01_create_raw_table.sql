-- PostgreSQL 15+
CREATE SCHEMA IF NOT EXISTS aerovista;
DROP TABLE IF EXISTS aerovista.flights_raw;
CREATE TABLE aerovista.flights_raw (
 flight_id TEXT, flight_number TEXT, scheduled_departure TEXT, origin_airport TEXT,
 destination_airport TEXT, origin_city TEXT, destination_city TEXT, destination_country TEXT,
 destination_region TEXT, aircraft_type TEXT, seat_capacity TEXT, distance_miles TEXT,
 season TEXT, departure_period TEXT, weather_condition TEXT, airport_congestion TEXT,
 departure_delay_minutes TEXT, turnaround_minutes TEXT, delay_cause TEXT, flight_status TEXT,
 cancellation_reason TEXT, on_time_flag TEXT, passengers TEXT, economy_passengers TEXT,
 business_passengers TEXT, load_factor TEXT, average_fare_usd TEXT, passenger_revenue_usd TEXT,
 ancillary_revenue_usd TEXT, cargo_revenue_usd TEXT, total_revenue_usd TEXT, fuel_cost_usd TEXT,
 crew_cost_usd TEXT, airport_fees_usd TEXT, maintenance_cost_usd TEXT,
 passenger_compensation_usd TEXT, other_operating_cost_usd TEXT, total_operating_cost_usd TEXT,
 operating_profit_usd TEXT, mishandled_bags TEXT, customer_satisfaction TEXT
);
-- From psql at the project root:
-- \copy aerovista.flights_raw FROM 'data/raw/aerovista_flights_raw.csv' CSV HEADER;
