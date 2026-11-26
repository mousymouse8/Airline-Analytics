# Power BI measures

Create a dedicated `_Measures` table and add the following measures.

```DAX
Total Flights = COUNTROWS ( fact_flights )

Completed Flights =
CALCULATE ( [Total Flights], fact_flights[flight_status] = "Completed" )

Cancelled Flights =
CALCULATE ( [Total Flights], fact_flights[flight_status] = "Cancelled" )

Cancellation Rate = DIVIDE ( [Cancelled Flights], [Total Flights] )

Total Passengers = SUM ( fact_flights[passengers] )

Available Seats = SUM ( fact_flights[seat_capacity] )

Load Factor = DIVIDE ( [Total Passengers], [Available Seats] )

Total Revenue = SUM ( fact_flights[total_revenue_usd] )

Passenger Revenue = SUM ( fact_flights[passenger_revenue_usd] )

Ancillary Revenue = SUM ( fact_flights[ancillary_revenue_usd] )

Cargo Revenue = SUM ( fact_flights[cargo_revenue_usd] )

Operating Cost = SUM ( fact_flights[total_operating_cost_usd] )

Operating Profit = SUM ( fact_flights[operating_profit_usd] )

Operating Margin = DIVIDE ( [Operating Profit], [Total Revenue] )

Revenue per Passenger = DIVIDE ( [Total Revenue], [Total Passengers] )

Profit per Flight = DIVIDE ( [Operating Profit], [Completed Flights] )

On-Time Flights =
CALCULATE ( [Total Flights], fact_flights[on_time_flag] = "Yes" )

On-Time Performance = DIVIDE ( [On-Time Flights], [Completed Flights] )

Average Delay Minutes =
CALCULATE (
    AVERAGE ( fact_flights[departure_delay_minutes] ),
    fact_flights[flight_status] = "Completed"
)

Average Turnaround Minutes = AVERAGE ( fact_flights[turnaround_minutes] )

Average Satisfaction = AVERAGE ( fact_flights[customer_satisfaction] )

Mishandled Bags per 1K Passengers =
DIVIDE ( SUM ( fact_flights[mishandled_bags] ) * 1000, [Total Passengers] )

Revenue PY =
CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Revenue YoY % = DIVIDE ( [Total Revenue] - [Revenue PY], [Revenue PY] )

Profit PY =
CALCULATE ( [Operating Profit], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Profit YoY % = DIVIDE ( [Operating Profit] - [Profit PY], [Profit PY] )

Route Rank by Profit =
RANKX ( ALLSELECTED ( dim_route[route] ), [Operating Profit], , DESC, DENSE )

Selected Route Summary =
VAR RouteName = SELECTEDVALUE ( dim_route[route], "All routes" )
RETURN RouteName & "  |  " & FORMAT ( [Load Factor], "0.0%" ) & " load factor  |  "
       & FORMAT ( [On-Time Performance], "0.0%" ) & " on time"
```

Formatting:

- Currency: `$#,0;($#,0)`
- Large currency cards: display units in millions, one decimal
- Rates: `0.0%`
- Counts: `#,0`
- Minutes and ratings: `0.0`
