# Power Query setup

Create a text parameter named `ProjectFolder` that points to the local `powerbi/data` directory. Then create one query per CSV using this pattern:

```powerquery
let
    Source = Csv.Document(
        File.Contents(ProjectFolder & "\\fact_flights.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"flight_id", type text}, {"flight_number", type text},
        {"flight_date", type date}, {"scheduled_departure", type datetime},
        {"route", type text}, {"origin_airport", type text},
        {"destination_airport", type text}, {"aircraft_type", type text},
        {"departure_delay_minutes", Int64.Type}, {"passengers", Int64.Type},
        {"seat_capacity", Int64.Type}, {"load_factor", Percentage.Type},
        {"total_revenue_usd", Currency.Type},
        {"total_operating_cost_usd", Currency.Type},
        {"operating_profit_usd", Currency.Type},
        {"customer_satisfaction", type number}
    })
in
    Types
```

Repeat for `dim_date.csv`, `dim_route.csv`, `dim_aircraft.csv`, and `dim_airport.csv`. Power BI normally infers the dimension types correctly; confirm date, integer, decimal, and text fields before applying changes.

## Relationships

| From | To | Cardinality | Filter direction |
|---|---|---|---|
| dim_date[date] | fact_flights[flight_date] | One-to-many | Single |
| dim_route[route] | fact_flights[route] | One-to-many | Single |
| dim_aircraft[aircraft_type] | fact_flights[aircraft_type] | One-to-many | Single |

Use `dim_airport` as a disconnected lookup for tooltip and reference use. A single airport table cannot actively filter both origin and destination without role-playing dimensions. If needed, duplicate it as `dim_origin_airport` and `dim_destination_airport`.

Mark `dim_date` as the date table using `dim_date[date]`, and sort `month_name` by `month_number`.
