-- 1. Monthly financial performance and year-over-year revenue growth.
WITH m AS (
 SELECT month_start, COUNT(*) FILTER(WHERE flight_status='Completed') AS completed_flights,
  SUM(total_revenue_usd) AS revenue, SUM(operating_profit_usd) AS operating_profit
 FROM aerovista.flights_clean GROUP BY 1)
SELECT *, ROUND(100*(revenue/NULLIF(LAG(revenue,12) OVER(ORDER BY month_start),0)-1),1) AS revenue_yoy_pct
FROM m ORDER BY month_start;

-- 2. Route scorecard.
SELECT route, COUNT(*) AS flights, SUM(passengers) AS passengers,
 ROUND(100*AVG(load_factor),1) AS load_factor_pct,
 ROUND(SUM(total_revenue_usd),2) AS revenue, ROUND(SUM(operating_profit_usd),2) AS operating_profit,
 ROUND(100*SUM(operating_profit_usd)/NULLIF(SUM(total_revenue_usd),0),1) AS operating_margin_pct,
 ROUND(100*AVG(on_time_flag::int) FILTER(WHERE flight_status='Completed'),1) AS on_time_pct
FROM aerovista.flights_clean GROUP BY 1 HAVING COUNT(*)>=100 ORDER BY operating_profit DESC;

-- 3. Operational delay drivers.
SELECT weather_condition, airport_congestion, departure_period, COUNT(*) AS flights,
 ROUND(AVG(departure_delay_minutes),1) AS avg_delay_minutes,
 ROUND(100*AVG(on_time_flag::int),1) AS on_time_pct,
 ROUND(AVG(customer_satisfaction),2) AS avg_satisfaction
FROM aerovista.flights_clean WHERE flight_status='Completed' AND departure_delay_minutes IS NOT NULL
GROUP BY 1,2,3 HAVING COUNT(*)>=50 ORDER BY avg_delay_minutes DESC;

-- 4. Fleet economics.
SELECT aircraft_type, COUNT(*) AS flights, SUM(passengers) AS passengers,
 ROUND(100*AVG(load_factor),1) AS avg_load_factor_pct,
 ROUND(SUM(operating_profit_usd),2) AS operating_profit,
 ROUND(100*SUM(operating_profit_usd)/NULLIF(SUM(total_revenue_usd),0),1) AS operating_margin_pct,
 ROUND(AVG(departure_delay_minutes),1) AS avg_delay_minutes
FROM aerovista.flights_clean GROUP BY 1 ORDER BY operating_profit DESC;

-- 5. Customer experience by delay band.
SELECT CASE WHEN departure_delay_minutes<=15 THEN 'On time'
 WHEN departure_delay_minutes<=30 THEN '16–30' WHEN departure_delay_minutes<=60 THEN '31–60'
 WHEN departure_delay_minutes<=120 THEN '61–120' ELSE '120+' END AS delay_band,
 COUNT(*) AS rated_flights, ROUND(AVG(customer_satisfaction),2) AS avg_satisfaction,
 ROUND(AVG(mishandled_bags),2) AS avg_mishandled_bags
FROM aerovista.flights_clean WHERE customer_satisfaction IS NOT NULL
GROUP BY 1 ORDER BY MIN(departure_delay_minutes);

-- 6. Delay-cause Pareto analysis.
WITH c AS (SELECT delay_cause,COUNT(*) AS delayed_flights FROM aerovista.flights_clean
 WHERE departure_delay_minutes>15 GROUP BY 1)
SELECT delay_cause, delayed_flights,
 ROUND(100.0*delayed_flights/SUM(delayed_flights) OVER(),1) AS share_pct,
 ROUND(100.0*SUM(delayed_flights) OVER(ORDER BY delayed_flights DESC)/SUM(delayed_flights) OVER(),1) AS cumulative_share_pct
FROM c ORDER BY delayed_flights DESC;
