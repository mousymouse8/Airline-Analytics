"""Generate a reproducible synthetic airline operations and profitability dataset."""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20260924
N_FLIGHTS = 50000
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

AIRPORTS = {
    "BAH": ("Bahrain International", "Manama", "Bahrain", "GCC", 0.07),
    "DXB": ("Dubai International", "Dubai", "UAE", "GCC", 0.11),
    "DOH": ("Hamad International", "Doha", "Qatar", "GCC", 0.07),
    "RUH": ("King Khalid International", "Riyadh", "Saudi Arabia", "GCC", 0.08),
    "JED": ("King Abdulaziz International", "Jeddah", "Saudi Arabia", "GCC", 0.08),
    "KWI": ("Kuwait International", "Kuwait City", "Kuwait", "GCC", 0.06),
    "MCT": ("Muscat International", "Muscat", "Oman", "GCC", 0.05),
    "LHR": ("Heathrow", "London", "United Kingdom", "Europe", 0.12),
    "CDG": ("Charles de Gaulle", "Paris", "France", "Europe", 0.08),
    "IST": ("Istanbul Airport", "Istanbul", "Türkiye", "Europe", 0.09),
    "BOM": ("Chhatrapati Shivaji Maharaj", "Mumbai", "India", "South Asia", 0.10),
    "CAI": ("Cairo International", "Cairo", "Egypt", "MENA", 0.09),
}

AIRCRAFT = {
    "A320neo": (180, 3500, 0.78, 0.82),
    "A321neo": (220, 4000, 0.91, 0.90),
    "B737 MAX 8": (178, 3550, 0.80, 0.83),
    "B787-9": (290, 7600, 1.55, 1.55),
    "A350-900": (315, 8000, 1.66, 1.62),
}


def weighted(rng, values, weights, n):
    p = np.array(weights, dtype=float); p /= p.sum()
    return rng.choice(values, n, p=p)


def main():
    rng = np.random.default_rng(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    date_pool = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    date_weight = np.ones(len(date_pool))
    date_weight *= np.where(date_pool.year == 2025, 1.13, 1.0)
    date_weight *= np.where(date_pool.month.isin([6, 7, 8, 12]), 1.24, 1.0)
    dates = pd.Series(rng.choice(date_pool, N_FLIGHTS, p=date_weight/date_weight.sum()))

    # Hub-and-spoke network with Bahrain as the main base and realistic regional/international mix.
    codes = list(AIRPORTS)
    destinations = weighted(rng, codes, [AIRPORTS[c][4] for c in codes], N_FLIGHTS)
    hub_origin = rng.random(N_FLIGHTS) < 0.55
    origins = np.where(hub_origin, "BAH", destinations)
    destinations = np.where(origins == destinations, weighted(rng, codes[1:], [AIRPORTS[c][4] for c in codes[1:]], N_FLIGHTS), destinations)
    destinations = np.where((origins != "BAH") & (rng.random(N_FLIGHTS) < .72), "BAH", destinations)
    same = origins == destinations
    destinations[same] = "DXB"

    distance_lookup = {
        "DXB": 303, "DOH": 92, "RUH": 263, "JED": 790, "KWI": 270, "MCT": 515,
        "LHR": 3170, "CDG": 3000, "IST": 1610, "BOM": 1515, "CAI": 1210, "BAH": 350
    }
    distance = np.array([max(90, distance_lookup.get(d, 600) + distance_lookup.get(o, 350)*(.22 if o != "BAH" else 0)) for o,d in zip(origins,destinations)])
    distance = np.round(distance * rng.normal(1, .025, N_FLIGHTS)).astype(int)
    international_long = distance > 2500
    medium = (distance > 1200) & ~international_long
    aircraft = np.where(international_long, weighted(rng,["B787-9","A350-900"],[.52,.48],N_FLIGHTS),
               np.where(medium, weighted(rng,["A321neo","B737 MAX 8","B787-9"],[.56,.34,.10],N_FLIGHTS),
                        weighted(rng,["A320neo","A321neo","B737 MAX 8"],[.46,.30,.24],N_FLIGHTS)))
    capacity = np.array([AIRCRAFT[x][0] for x in aircraft])

    season = np.select([dates.dt.month.isin([12,1,2]), dates.dt.month.isin([3,4,5]), dates.dt.month.isin([6,7,8])], ["Winter","Spring","Summer"], default="Autumn")
    departure_hour = weighted(rng, np.arange(24), [1,1,1,1,2,4,7,8,7,6,5,4,5,5,6,7,8,9,10,10,9,7,5,3], N_FLIGHTS).astype(int)
    scheduled_departure = dates + pd.to_timedelta(departure_hour, unit="h") + pd.to_timedelta(rng.integers(0,60,N_FLIGHTS), unit="m")
    peak = np.isin(departure_hour, [6,7,8,17,18,19,20])

    weather = np.where(dates.dt.month.isin([6,7,8,9]), weighted(rng,["Clear","Extreme Heat","Dust"],[.49,.43,.08],N_FLIGHTS), weighted(rng,["Clear","Rain","Fog","Dust","Mild"],[.49,.14,.08,.08,.21],N_FLIGHTS))
    congestion = weighted(rng,["Low","Medium","High"],[.25,.53,.22],N_FLIGHTS)
    base_delay = rng.gamma(1.35, 3.4, N_FLIGHTS)
    dep_delay = base_delay + 8*(congestion=="High") + 4*peak + 12*(weather=="Rain") + 18*(weather=="Fog") + 8*(weather=="Dust") + 5*(weather=="Extreme Heat")
    dep_delay = np.maximum(0, np.round(dep_delay + rng.normal(0,4,N_FLIGHTS))).astype(int)
    cancel_p = .006 + .016*(weather=="Fog") + .010*(weather=="Dust") + .006*(congestion=="High")
    cancelled = rng.random(N_FLIGHTS) < cancel_p
    cancellation_reason = np.where(~cancelled,"Not Cancelled",weighted(rng,["Weather","Technical","Crew","Air Traffic Control","Commercial"],[.31,.24,.16,.21,.08],N_FLIGHTS))
    dep_delay = np.where(cancelled, 0, dep_delay)
    turnaround = np.clip(np.round(rng.normal(48,8,N_FLIGHTS) + 9*(congestion=="High") + 6*(dep_delay>45)),25,100).astype(int)
    on_time = (~cancelled) & (dep_delay <= 15)

    demand = .77 + .08*np.isin(dates.dt.month,[6,7,8,12]) + .04*(dates.dt.year==2025) + .025*(scheduled_departure.dt.dayofweek>=4) + rng.normal(0,.075,N_FLIGHTS)
    load_factor = np.clip(demand, .46, .99)
    passengers = np.where(cancelled,0,np.floor(capacity*load_factor)).astype(int)
    load_factor = np.where(cancelled,0,passengers/capacity)
    business_share = np.clip(.08 + .08*international_long + .03*(destinations=="LHR") + rng.normal(0,.018,N_FLIGHTS),.03,.25)
    business_passengers = np.floor(passengers*business_share).astype(int)
    economy_passengers = passengers-business_passengers

    fare_per_mile = np.where(international_long,.105,np.where(medium,.13,.22))
    avg_fare = distance*fare_per_mile*(1 + .22*np.isin(dates.dt.month,[6,7,8,12]))*rng.lognormal(0,.10,N_FLIGHTS)
    passenger_revenue = passengers*avg_fare*(1 + 1.35*business_share)
    ancillary_revenue = passengers*rng.normal(np.where(international_long,31,19),5,N_FLIGHTS)
    cargo_revenue = distance*np.where(international_long,4.8,np.where(medium,2.5,.65))*rng.uniform(.72,1.30,N_FLIGHTS)
    total_revenue = np.where(cancelled,0,passenger_revenue+ancillary_revenue+cargo_revenue)
    fuel_rate = np.array([AIRCRAFT[x][2] for x in aircraft])
    maintenance_rate = np.array([AIRCRAFT[x][3] for x in aircraft])
    fuel_cost = np.where(cancelled, total_revenue*.015, distance*fuel_rate*(1.08 + .06*(dates.dt.year==2025))*rng.uniform(.92,1.08,N_FLIGHTS))
    crew_cost = np.where(cancelled, 2200 + distance*.20, 1900 + distance*.72 + 350*international_long)
    airport_fees = np.where(cancelled, 800, 1100 + capacity*5.2 + 550*np.isin(destinations,["LHR","CDG","DXB"]))
    maintenance_cost = np.where(cancelled, 950, distance*maintenance_rate + 700)
    compensation = np.where(cancelled, passengers*38, np.where(dep_delay>180,passengers*90,np.where(dep_delay>60,passengers*24,0)))
    other_operating_cost = np.where(cancelled, 1450, total_revenue * rng.normal(.665,.025,N_FLIGHTS))
    other_operating_cost = np.maximum(0, other_operating_cost)
    total_cost = fuel_cost+crew_cost+airport_fees+maintenance_cost+compensation+other_operating_cost
    operating_profit = total_revenue-total_cost

    delay_cause = np.select([cancelled, dep_delay<=15, weather!="Clear", congestion=="High", dep_delay>45], ["Cancelled","No Material Delay","Weather","Air Traffic Control","Late Aircraft"], default="Technical / Other")
    mishandled_bags = np.where(cancelled,0,rng.binomial(np.maximum(passengers,1), np.clip(.004 + .004*international_long + .003*(turnaround<38),0,.03)))
    satisfaction = 4.75 - .018*np.maximum(dep_delay-5,0) - .45*cancelled - .025*mishandled_bags + rng.normal(0,.42,N_FLIGHTS)
    satisfaction = np.clip(np.round(satisfaction,1),1,5)
    satisfaction = np.where((~cancelled)&(rng.random(N_FLIGHTS)<.58),satisfaction,np.nan)

    df = pd.DataFrame({
        "flight_id":[f"AV-{i:07d}" for i in range(1,N_FLIGHTS+1)],
        "flight_number":[f"AV{n:04d}" for n in rng.integers(100,1899,N_FLIGHTS)],
        "scheduled_departure":scheduled_departure.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "origin_airport":origins,"destination_airport":destinations,
        "origin_city":[AIRPORTS[x][1] for x in origins],"destination_city":[AIRPORTS[x][1] for x in destinations],
        "destination_country":[AIRPORTS[x][2] for x in destinations],"destination_region":[AIRPORTS[x][3] for x in destinations],
        "aircraft_type":aircraft,"seat_capacity":capacity,"distance_miles":distance,"season":season,
        "departure_period":pd.cut(departure_hour,[-1,5,11,16,21,23],labels=["Overnight","Morning","Afternoon","Evening","Late Night"]).astype(str),
        "weather_condition":weather,"airport_congestion":congestion,"departure_delay_minutes":dep_delay,
        "turnaround_minutes":turnaround,"delay_cause":delay_cause,
        "flight_status":np.where(cancelled,"Cancelled","Completed"),"cancellation_reason":cancellation_reason,
        "on_time_flag":np.where(cancelled,"Not Applicable",np.where(on_time,"Yes","No")),
        "passengers":passengers,"economy_passengers":economy_passengers,"business_passengers":business_passengers,
        "load_factor":np.round(load_factor,4),"average_fare_usd":np.round(avg_fare,2),
        "passenger_revenue_usd":np.round(passenger_revenue,2),"ancillary_revenue_usd":np.round(ancillary_revenue,2),
        "cargo_revenue_usd":np.round(cargo_revenue,2),"total_revenue_usd":np.round(total_revenue,2),
        "fuel_cost_usd":np.round(fuel_cost,2),"crew_cost_usd":np.round(crew_cost,2),"airport_fees_usd":np.round(airport_fees,2),
        "maintenance_cost_usd":np.round(maintenance_cost,2),"passenger_compensation_usd":np.round(compensation,2),
        "other_operating_cost_usd":np.round(other_operating_cost,2),
        "total_operating_cost_usd":np.round(total_cost,2),"operating_profit_usd":np.round(operating_profit,2),
        "mishandled_bags":mishandled_bags,"customer_satisfaction":satisfaction
    })

    # Controlled quality defects: duplicates, inconsistent codes, missing types, and sentinel delays.
    idx = rng.choice(df.index, 260, replace=False)
    df.loc[idx[:70],"origin_airport"] = df.loc[idx[:70],"origin_airport"].str.lower()
    df.loc[idx[70:130],"destination_airport"] = " " + df.loc[idx[70:130],"destination_airport"] + " "
    df.loc[idx[130:180],"aircraft_type"] = None
    df.loc[idx[180:220],"departure_delay_minutes"] = -1
    df.loc[idx[220:],"airport_congestion"] = df.loc[idx[220:],"airport_congestion"].str.upper()
    df = pd.concat([df,df.sample(220,random_state=SEED)],ignore_index=True).sample(frac=1,random_state=SEED).reset_index(drop=True)
    df.to_csv(RAW_DIR/"aerovista_flights_raw.csv",index=False)
    print(f"Created {len(df):,} raw rows and {df.flight_id.nunique():,} unique flights.")

if __name__ == "__main__":
    main()
