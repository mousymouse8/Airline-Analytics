"""Clean the synthetic flight data, create Power BI star-schema files, and render EDA charts."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/aerovista_flights_raw.csv"
PROCESSED = ROOT / "data/processed"
POWERBI = ROOT / "powerbi/data"
CHARTS = ROOT / "charts"


def clean(df):
    df = df.copy().drop_duplicates("flight_id", keep="last")
    df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"], errors="coerce")
    df["origin_airport"] = df["origin_airport"].str.strip().str.upper()
    df["destination_airport"] = df["destination_airport"].str.strip().str.upper()
    df["airport_congestion"] = df["airport_congestion"].str.strip().str.title()
    df["aircraft_type"] = df["aircraft_type"].fillna("Unknown")
    df["departure_delay_minutes"] = pd.to_numeric(df["departure_delay_minutes"], errors="coerce").replace(-1,np.nan)
    numeric = [c for c in df.columns if c.endswith("_usd") or c in ["seat_capacity","distance_miles","turnaround_minutes","passengers","economy_passengers","business_passengers","load_factor","mishandled_bags","customer_satisfaction"]]
    for c in numeric: df[c] = pd.to_numeric(df[c], errors="coerce")
    df["flight_date"] = df["scheduled_departure"].dt.normalize()
    df["month_start"] = df["scheduled_departure"].dt.to_period("M").dt.to_timestamp()
    df["year"] = df["scheduled_departure"].dt.year
    df["month_name"] = df["scheduled_departure"].dt.month_name().str[:3]
    df["day_name"] = df["scheduled_departure"].dt.day_name().str[:3]
    df["route"] = df["origin_airport"] + "–" + df["destination_airport"]
    df["completed_flag"] = df["flight_status"].eq("Completed")
    df["cancelled_flag"] = df["flight_status"].eq("Cancelled")
    df["on_time_bool"] = df["on_time_flag"].eq("Yes")
    df["operating_margin_pct"] = df["operating_profit_usd"] / df["total_revenue_usd"].replace(0,np.nan)
    return df


def save(name):
    plt.tight_layout(); plt.savefig(CHARTS/name,dpi=180,bbox_inches="tight",facecolor="white"); plt.close()


def create_star(df):
    POWERBI.mkdir(parents=True,exist_ok=True)
    airports = pd.concat([
        df[["origin_airport","origin_city"]].rename(columns={"origin_airport":"airport_code","origin_city":"city"}),
        df[["destination_airport","destination_city","destination_country","destination_region"]].rename(columns={"destination_airport":"airport_code","destination_city":"city","destination_country":"country","destination_region":"region"})
    ]).groupby("airport_code",as_index=False).first().fillna({"country":"Bahrain","region":"GCC"})
    aircraft = df[["aircraft_type","seat_capacity"]].drop_duplicates().sort_values(["aircraft_type","seat_capacity"])
    aircraft = aircraft.drop_duplicates("aircraft_type",keep="last")
    routes = df[["route","origin_airport","destination_airport","distance_miles"]].groupby(["route","origin_airport","destination_airport"],as_index=False).agg(distance_miles=("distance_miles","median"))
    routes["distance_band"] = pd.cut(routes.distance_miles,[0,500,1500,3000,10000],labels=["Short haul","Medium haul","Long haul","Ultra-long haul"])
    dates = pd.DataFrame({"date":pd.date_range(df.flight_date.min(),df.flight_date.max(),freq="D")})
    dates["year"]=dates.date.dt.year; dates["quarter"]="Q"+dates.date.dt.quarter.astype(str)
    dates["month_number"]=dates.date.dt.month; dates["month_name"]=dates.date.dt.month_name(); dates["month_start"]=dates.date.dt.to_period("M").dt.to_timestamp()
    dates["week_number"]=dates.date.dt.isocalendar().week.astype(int); dates["day_name"]=dates.date.dt.day_name(); dates["is_weekend"]=dates.date.dt.dayofweek>=4
    fact_cols = ["flight_id","flight_number","flight_date","scheduled_departure","route","origin_airport","destination_airport","aircraft_type","season","departure_period","weather_condition","airport_congestion","departure_delay_minutes","turnaround_minutes","delay_cause","flight_status","cancellation_reason","on_time_flag","passengers","economy_passengers","business_passengers","seat_capacity","load_factor","average_fare_usd","passenger_revenue_usd","ancillary_revenue_usd","cargo_revenue_usd","total_revenue_usd","fuel_cost_usd","crew_cost_usd","airport_fees_usd","maintenance_cost_usd","passenger_compensation_usd","other_operating_cost_usd","total_operating_cost_usd","operating_profit_usd","operating_margin_pct","mishandled_bags","customer_satisfaction"]
    df[fact_cols].to_csv(POWERBI/"fact_flights.csv",index=False)
    airports.to_csv(POWERBI/"dim_airport.csv",index=False); aircraft.to_csv(POWERBI/"dim_aircraft.csv",index=False)
    routes.to_csv(POWERBI/"dim_route.csv",index=False); dates.to_csv(POWERBI/"dim_date.csv",index=False)


def main():
    PROCESSED.mkdir(parents=True,exist_ok=True); CHARTS.mkdir(parents=True,exist_ok=True)
    df=clean(pd.read_csv(RAW)); df.to_csv(PROCESSED/"flights_clean.csv",index=False); create_star(df)
    complete=df[df.completed_flag].copy(); sns.set_theme(style="whitegrid",context="talk")
    navy,teal,gold,red="#102A43","#168C8C","#D4A72C","#C84C4C"
    monthly=complete.groupby("month_start").agg(revenue=("total_revenue_usd","sum"),profit=("operating_profit_usd","sum")).reset_index()
    fig,ax=plt.subplots(figsize=(12,6)); ax.plot(monthly.month_start,monthly.revenue/1e6,color=navy,marker="o",label="Revenue"); ax.plot(monthly.month_start,monthly.profit/1e6,color=teal,marker="o",label="Operating profit"); ax.set(title="Monthly revenue and operating profit",xlabel="",ylabel="USD millions"); ax.legend(frameon=False); ax.tick_params(axis="x",rotation=45); save("01_monthly_financials.png")
    route=complete.groupby("route").agg(flights=("flight_id","count"),revenue=("total_revenue_usd","sum"),profit=("operating_profit_usd","sum"),load_factor=("load_factor","mean")).query("flights>=100").sort_values("profit",ascending=False).head(12).reset_index()
    plt.figure(figsize=(11,7)); sns.barplot(data=route,x="profit",y="route",color=teal); plt.title("Most profitable routes"); plt.xlabel("Operating profit (USD)"); plt.ylabel(""); save("02_route_profit.png")
    delay=complete.groupby(["weather_condition","airport_congestion"]).agg(delay=("departure_delay_minutes","mean"),flights=("flight_id","count")).reset_index(); pivot=delay.pivot(index="weather_condition",columns="airport_congestion",values="delay").reindex(columns=["Low","Medium","High"])
    plt.figure(figsize=(9,6)); sns.heatmap(pivot,annot=True,fmt=".1f",cmap="YlOrRd",cbar_kws={"label":"Minutes"}); plt.title("Average departure delay by operating condition"); plt.xlabel("Airport congestion"); plt.ylabel("Weather"); save("03_delay_heatmap.png")
    cause=complete[complete.departure_delay_minutes>15].groupby("delay_cause").flight_id.count().sort_values().reset_index(); plt.figure(figsize=(10,5)); sns.barplot(data=cause,x="flight_id",y="delay_cause",color=gold); plt.title("Material delays by primary cause"); plt.xlabel("Flights delayed more than 15 minutes"); plt.ylabel(""); save("04_delay_causes.png")
    sat=complete.dropna(subset=["customer_satisfaction","departure_delay_minutes"]).copy(); sat["delay_band"]=pd.cut(sat.departure_delay_minutes,[-1,15,30,60,120,1000],labels=["On time","16–30","31–60","61–120","120+"])
    s=sat.groupby("delay_band",observed=True).customer_satisfaction.mean().reset_index(); plt.figure(figsize=(9,5)); sns.lineplot(data=s,x="delay_band",y="customer_satisfaction",marker="o",linewidth=3,color=red); plt.ylim(1,5); plt.title("Customer satisfaction declines with delay length"); plt.xlabel("Departure delay (minutes)"); plt.ylabel("Average satisfaction"); save("05_satisfaction_delay.png")
    fleet=complete.groupby("aircraft_type").agg(flights=("flight_id","count"),load_factor=("load_factor","mean"),margin=("operating_margin_pct","mean"),profit=("operating_profit_usd","sum")).reset_index(); plt.figure(figsize=(10,6)); sns.scatterplot(data=fleet,x="load_factor",y="margin",size="flights",hue="aircraft_type",sizes=(150,700),palette="deep"); plt.axhline(0,color="#777",lw=1); plt.title("Fleet utilization and operating margin"); plt.xlabel("Average load factor"); plt.ylabel("Average operating margin"); plt.legend(bbox_to_anchor=(1.02,1),loc="upper left"); save("06_fleet_performance.png")
    by_year=complete.groupby("year").agg(revenue=("total_revenue_usd","sum"),profit=("operating_profit_usd","sum"),flights=("flight_id","count"))
    summary={"raw_rows":int(len(pd.read_csv(RAW))),"clean_flights":int(len(df)),"completed_flights":int(len(complete)),"total_revenue_usd":round(float(complete.total_revenue_usd.sum()),2),"operating_profit_usd":round(float(df.operating_profit_usd.sum()),2),"operating_margin_pct":round(float(df.operating_profit_usd.sum()/complete.total_revenue_usd.sum()*100),2),"on_time_performance_pct":round(float(complete.on_time_bool.mean()*100),2),"cancellation_rate_pct":round(float(df.cancelled_flag.mean()*100),2),"average_load_factor_pct":round(float(complete.load_factor.mean()*100),2),"average_satisfaction":round(float(complete.customer_satisfaction.mean()),2),"revenue_growth_pct":round(float((by_year.loc[2025,'revenue']/by_year.loc[2024,'revenue']-1)*100),1),"top_profit_route":str(route.iloc[0].route),"worst_delay_condition":f"{delay.sort_values('delay',ascending=False).iloc[0].weather_condition} / {delay.sort_values('delay',ascending=False).iloc[0].airport_congestion} congestion"}
    (ROOT/"analysis_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8"); print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
