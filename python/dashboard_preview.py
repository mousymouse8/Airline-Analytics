"""Render a static preview of the recommended Power BI Executive Overview page."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from eda_analysis import clean, RAW

ROOT=Path(__file__).resolve().parents[1]
df=clean(pd.read_csv(RAW))
c=df[df.flight_status.eq("Completed")].copy()
NAVY="#102A43"; TEAL="#168C8C"; GOLD="#D4A72C"; RED="#C84C4C"; BG="#F5F7FA"; MUTED="#627D98"

fig=plt.figure(figsize=(16,9),facecolor=BG)
ax=fig.add_axes([0,0,1,1]); ax.axis("off")
ax.add_patch(Rectangle((0,0),.075,1,color=NAVY))
ax.text(.0375,.945,"AV",ha="center",va="center",color="white",fontsize=22,fontweight="bold")
for y,t in zip([.80,.70,.60,.50],["Overview","Routes","Operations","Experience"]):
    ax.text(.0375,y,t,ha="center",va="center",rotation=90,color="white" if y==.80 else "#AFC7D7",fontsize=9)
ax.text(.105,.94,"Executive Overview",fontsize=24,fontweight="bold",color=NAVY,va="center")
ax.text(.105,.905,"Network performance  |  January 2024 – December 2025",fontsize=10,color=MUTED)

def card(x,y,w,h,title,value,subtitle,color=TEAL):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.006,rounding_size=.012",fc="white",ec="#D9E2EC",lw=1))
    ax.add_patch(Rectangle((x,y+h-.008),w,.008,color=color))
    ax.text(x+.015,y+h-.035,title,fontsize=9,color=MUTED,va="top")
    ax.text(x+.015,y+.043,value,fontsize=20,fontweight="bold",color=NAVY,va="bottom")
    ax.text(x+.015,y+.018,subtitle,fontsize=8,color=color)

revenue=c.total_revenue_usd.sum(); profit=df.operating_profit_usd.sum(); margin=profit/revenue
cards=[("Revenue",f"${revenue/1e9:.2f}B","▲ 19.1% YoY",TEAL),("Operating Profit",f"${profit/1e6:.1f}M","15.0% margin",TEAL),("Load Factor",f"{c.load_factor.mean():.1%}","2.9 pts above 2024",GOLD),("On-Time",f"{c.on_time_bool.mean():.1%}","15-minute standard",RED),("Passengers",f"{c.passengers.sum()/1e6:.1f}M","Completed flights",TEAL)]
for i,v in enumerate(cards): card(.105+i*.174,.75,.158,.115,*v)

def panel(x,y,w,h,title):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.005,rounding_size=.01",fc="white",ec="#D9E2EC",lw=1))
    ax.text(x+.014,y+h-.028,title,fontsize=11,fontweight="bold",color=NAVY,va="top")

panel(.105,.40,.515,.31,"How are revenue and profit trending?")
monthly=c.groupby("month_start").agg(revenue=("total_revenue_usd","sum"),profit=("operating_profit_usd","sum")).reset_index()
a1=fig.add_axes([.13,.445,.46,.21],facecolor="white"); a1.plot(monthly.month_start,monthly.revenue/1e6,color=NAVY,lw=2.3,label="Revenue"); a1.plot(monthly.month_start,monthly.profit/1e6,color=TEAL,lw=2.3,label="Profit"); a1.spines[:].set_visible(False); a1.grid(axis="y",color="#E9EFF4"); a1.tick_params(labelsize=8,colors=MUTED); a1.set_ylabel("USD millions",fontsize=8,color=MUTED); a1.legend(frameon=False,fontsize=8,ncol=2,loc="upper left")

panel(.64,.40,.315,.31,"Which routes create the most profit?")
routes=c.groupby("route").operating_profit_usd.sum().nlargest(6).sort_values()
a2=fig.add_axes([.68,.445,.245,.21],facecolor="white"); a2.barh(routes.index,routes.values/1e6,color=TEAL); a2.spines[:].set_visible(False); a2.grid(axis="x",color="#E9EFF4"); a2.tick_params(labelsize=8,colors=MUTED); a2.set_xlabel("USD millions",fontsize=8,color=MUTED)

panel(.105,.08,.27,.275,"What causes material delays?")
cause=c[c.departure_delay_minutes>15].delay_cause.value_counts().sort_values()
a3=fig.add_axes([.14,.12,.205,.17],facecolor="white"); a3.barh(cause.index,cause.values,color=GOLD); a3.spines[:].set_visible(False); a3.grid(axis="x",color="#E9EFF4"); a3.tick_params(labelsize=7,colors=MUTED)

panel(.395,.08,.27,.275,"Revenue mix")
mix=[c.passenger_revenue_usd.sum(),c.ancillary_revenue_usd.sum(),c.cargo_revenue_usd.sum()]; labels=["Passenger","Ancillary","Cargo"]
a4=fig.add_axes([.44,.12,.18,.17],facecolor="white"); a4.pie(mix,labels=labels,colors=[NAVY,TEAL,GOLD],autopct="%1.0f%%",textprops={"fontsize":8},wedgeprops={"width":.42,"edgecolor":"white"})

panel(.685,.08,.27,.275,"Route performance snapshot")
tbl=c.groupby("route").agg(flights=("flight_id","count"),load=("load_factor","mean"),otp=("on_time_bool","mean"),profit=("operating_profit_usd","sum")).sort_values("profit",ascending=False).head(5).reset_index()
a5=fig.add_axes([.71,.115,.22,.185]); a5.axis("off")
rows=[[r.route,f"{r.load:.0%}",f"{r.otp:.0%}",f"${r.profit/1e6:.1f}M"] for r in tbl.itertuples()]
t=a5.table(cellText=rows,colLabels=["Route","Load","OTP","Profit"],loc="center",cellLoc="left"); t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1,1.45)
for (r,col),cell in t.get_celld().items(): cell.set_edgecolor("#E5EBF0"); cell.set_facecolor("#EDF5F5" if r==0 else "white"); cell.set_text_props(color=NAVY,weight="bold" if r==0 else "normal")

out=ROOT/"powerbi/AeroVista_Dashboard_Preview.png"; plt.savefig(out,dpi=160,bbox_inches="tight",facecolor=BG); plt.close(); print(out)
