# AeroVista Power BI dashboard build guide

The report uses a 16:9 canvas, a light background (`#F5F7FA`), white visual cards, navy titles, teal primary data, gold highlights, and red only for adverse performance. Import `AeroVista_Executive_Theme.json` before formatting visuals.

## Navigation

Use a slim left navigation rail with four page buttons:

1. Executive Overview
2. Route & Revenue
3. Operations
4. Customer Experience

Keep navigation, page title, and slicer placement consistent. Use only Year, Month, Region, Route, and Aircraft slicers. Sync Year and Region across pages.

## Page 1 — Executive Overview

Purpose: answer “How is the airline performing?” within ten seconds.

- Top row: Total Revenue, Operating Profit, Operating Margin, Load Factor, On-Time Performance
- Middle-left: monthly Revenue and Operating Profit line chart
- Middle-right: top six routes by Operating Profit
- Bottom-left: Revenue by destination region
- Bottom-middle: Delay Cause distribution
- Bottom-right: compact table with Route, Flights, Load Factor, OTP, and Margin

Use conditional card subtitles for year-on-year change. Limit the route chart to six items and provide a tooltip page for detail.

## Page 2 — Route & Revenue

Purpose: compare network demand and profitability.

- KPI cards: Passengers, Revenue per Passenger, Profit per Flight, Cancellation Rate
- Scatter plot: Load Factor vs Operating Margin; bubble size = Revenue; legend = Distance Band
- Ranked bar chart: Operating Profit by Route
- Matrix: Route → Aircraft Type with Revenue, Profit, Margin, Load Factor, OTP
- Revenue mix: Passenger, Ancillary, and Cargo Revenue as a 100% stacked bar

Add a Route slicer with search. Use a drill-through page called `Route Detail` containing 24-month trends and delay breakdown.

## Page 3 — Operations

Purpose: show what is damaging punctuality.

- KPI cards: OTP, Average Delay, Average Turnaround, Cancelled Flights
- Heat map: Weather × Congestion colored by Average Delay Minutes
- Column chart: delayed flights by Delay Cause
- Line chart: OTP by Month
- Small multiples: Average Delay by Departure Period and Airport
- Detail table: Flight Number, Route, Date, Aircraft, Delay, Cause, Status

Color only values below 70% OTP or above 30 minutes delay in red. Do not use gauges; a KPI card with a target label uses less space and is easier to compare.

## Page 4 — Customer Experience

Purpose: connect operational performance to passenger outcomes.

- KPI cards: Average Satisfaction, Mishandled Bags per 1K, OTP, Average Delay
- Line chart: Satisfaction by Delay Band
- Scatter plot: Average Delay vs Satisfaction by Route
- Bar chart: Mishandled Bags per 1K by Aircraft Type
- Decomposition tree: Satisfaction explained by Region → Route → Weather → Delay Cause
- Tooltip: passengers, load factor, rating, delay, and mishandled bags

## Interaction and UX rules

- Use Edit Interactions so KPI cards respond to every global slicer.
- Keep visual titles phrased as questions or conclusions, not field names.
- Use one decimal for percentages and minutes; avoid unnecessary precision.
- Use tooltips for secondary metrics instead of adding labels everywhere.
- Maintain at least 16 px between visual containers and 24 px page margins.
- Keep each page to 8–10 visuals, including KPI cards.
- Use red only for problems and green only for confirmed positive status.
- Add an information tooltip defining OTP as departure within 15 minutes of schedule.
- Add a Reset Filters bookmark and button on every page.
- Test at 100% zoom and in Power BI Service reading view.

## Creating the final Power BI file

After loading the model, measures, theme, and report pages in Power BI Desktop:

1. Save as `AeroVista_Airline_Analytics.pbix` for normal portfolio sharing.
2. Also save as `AeroVista_Airline_Analytics.pbip` if you want Git-friendly source control.
3. Replace the local `ProjectFolder` parameter before refreshing on another computer.

Microsoft documents that PBIX/PBIP conversion must be completed from Power BI Desktop. The included files provide the complete model and report specification but do not pretend to be a Desktop-generated binary.
