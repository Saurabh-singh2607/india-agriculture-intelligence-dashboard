
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="India Agriculture Dashboard", page_icon="🌾", layout="wide")

st.title("🌾 India Agriculture & Crop Price Dashboard")
st.caption("Explore crop production trends, seasonal patterns, state-wise performance and market prices.")

@st.cache_data
def load_data():
    base = Path(__file__).parent
    production = pd.read_csv(base / "crop_production.csv")
    prices = pd.read_csv(base / "india-crop-prices.csv")
    production["Crop_Year"] = pd.to_numeric(production["Crop_Year"], errors="coerce")
    production["Area"] = pd.to_numeric(production["Area"], errors="coerce")
    production["Production"] = pd.to_numeric(production["Production"], errors="coerce")
    prices["modal_rs_per_quintal"] = pd.to_numeric(prices["modal_rs_per_quintal"], errors="coerce")
    prices["msp"] = pd.to_numeric(prices["msp"], errors="coerce")
    return production, prices

try:
    df, prices = load_data()
except Exception as e:
    st.error(f"Could not load the CSV files. Keep both CSV files in the same folder as app.py. Details: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")
years = sorted(df["Crop_Year"].dropna().astype(int).unique().tolist())
states = sorted(df["State_Name"].dropna().unique().tolist())
seasons = sorted(df["Season"].dropna().unique().tolist())
crops = sorted(df["Crop"].dropna().unique().tolist())

year_range = st.sidebar.select_slider(
    "Crop year range", options=years,
    value=(years[0], years[-1])
)
selected_states = st.sidebar.multiselect("States", states, default=[])
selected_seasons = st.sidebar.multiselect("Seasons", seasons, default=[])
selected_crops = st.sidebar.multiselect("Crops", crops, default=[])

filtered = df[df["Crop_Year"].between(year_range[0], year_range[1])]
if selected_states:
    filtered = filtered[filtered["State_Name"].isin(selected_states)]
if selected_seasons:
    filtered = filtered[filtered["Season"].isin(selected_seasons)]
if selected_crops:
    filtered = filtered[filtered["Crop"].isin(selected_crops)]
filtered = filtered.dropna(subset=["Production", "Area"])

# Summary metrics
total_production = filtered["Production"].sum()
total_area = filtered["Area"].sum()
crop_count = filtered["Crop"].nunique()
state_count = filtered["State_Name"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Production", f"{total_production:,.0f}")
c2.metric("Total Cultivated Area", f"{total_area:,.0f}")
c3.metric("Unique Crops", f"{crop_count:,}")
c4.metric("States / UTs", f"{state_count:,}")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Production Trend by Year")
    yearly = filtered.groupby("Crop_Year", as_index=False)["Production"].sum()
    fig = px.line(yearly, x="Crop_Year", y="Production", markers=True,
                  labels={"Crop_Year": "Year", "Production": "Production"},
                  title="Annual crop production")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top 10 Crops by Production")
    top_crops = (filtered.groupby("Crop", as_index=False)["Production"].sum()
                 .nlargest(10, "Production").sort_values("Production"))
    fig = px.bar(top_crops, x="Production", y="Crop", orientation="h",
                 title="Highest producing crops",
                 labels={"Production": "Production", "Crop": "Crop"})
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("State-wise Production")
    state_data = (filtered.groupby("State_Name", as_index=False)["Production"].sum()
                  .nlargest(12, "Production").sort_values("Production"))
    fig = px.bar(state_data, x="Production", y="State_Name", orientation="h",
                 title="Top 12 states / UTs",
                 labels={"Production": "Production", "State_Name": "State"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Seasonal Production Share")
    season_data = filtered.groupby("Season", as_index=False)["Production"].sum()
    fig = px.pie(season_data, names="Season", values="Production", hole=0.45,
                 title="Production by agricultural season")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.header("💰 Crop Market Prices & MSP")
st.caption("Price figures are shown in ₹ per quintal, based on the supplied crop-price dataset.")
price_search = st.text_input("Search crop name", "")
price_view = prices.copy()
if price_search:
    price_view = price_view[
        price_view["crop"].str.contains(price_search, case=False, na=False) |
        price_view["crop_hindi"].str.contains(price_search, case=False, na=False)
    ]
price_view = price_view.sort_values("modal_rs_per_quintal", ascending=False)
p1, p2 = st.columns(2)
with p1:
    st.subheader("Modal Price vs MSP")
    chart_prices = price_view.dropna(subset=["modal_rs_per_quintal", "msp"]).melt(
        id_vars=["crop"], value_vars=["modal_rs_per_quintal", "msp"],
        var_name="Price Type", value_name="₹ / Quintal"
    )
    fig = px.bar(chart_prices, x="crop", y="₹ / Quintal", color="Price Type",
                 barmode="group", title="Market modal price compared with MSP")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
with p2:
    st.subheader("Price Range")
    range_view = price_view.nlargest(12, "modal_rs_per_quintal").sort_values("modal_rs_per_quintal")
    fig = px.bar(range_view, x="modal_rs_per_quintal", y="crop", orientation="h",
                 error_x=range_view["max"] - range_view["modal_rs_per_quintal"],
                 title="Top crops by modal price",
                 labels={"modal_rs_per_quintal": "₹ / Quintal", "crop": "Crop"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Crop Price Dataset")
st.dataframe(price_view, use_container_width=True, hide_index=True)

with st.expander("About this dashboard"):
    st.write("""
    **Data sources:** `crop_production.csv` and `india-crop-prices.csv` supplied with this project.

    **Production section:** filters by year, state, season and crop; calculates total production and area;
    and visualizes yearly, crop-wise, state-wise and seasonal patterns.

    **Price section:** compares modal market prices with Minimum Support Price (MSP), displays price ranges,
    and provides a searchable crop table.

    **Note:** The two source files have different structures and are analyzed in separate sections.
    Production units follow the source dataset; price values are ₹ per quintal.
    """)
