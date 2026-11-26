# Data dictionary

Each raw row represents one scheduled flight. All organizations, flights, routes, and results are synthetic.

| Field group | Example columns | Description |
|---|---|---|
| Flight identity | flight_id, flight_number, scheduled_departure | Unique service and schedule fields |
| Network | origin_airport, destination_airport, route, region, distance_miles | Route geography and distance |
| Fleet | aircraft_type, seat_capacity | Aircraft assigned to the service |
| Operating context | weather_condition, airport_congestion, departure_period | Conditions affecting delivery |
| Reliability | departure_delay_minutes, delay_cause, on_time_flag, flight_status | Punctuality and disruption outcomes |
| Demand | passengers, class passenger counts, load_factor | Capacity utilization |
| Revenue | fare, passenger, ancillary, cargo, and total revenue | Flight-level commercial performance |
| Cost | fuel, crew, airport, maintenance, compensation, other operating cost | Variable and allocated flight costs |
| Profit | operating_profit_usd, operating_margin_pct | Flight contribution after modeled operating costs |
| Experience | customer_satisfaction, mishandled_bags | Passenger outcome indicators |

Raw-data issues are deliberately included: 220 duplicate flights, inconsistent airport-code casing and whitespace, 50 missing aircraft types, 40 invalid delay sentinels, and inconsistent congestion capitalization.
