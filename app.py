import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from geopy.geocoders import Nominatim
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Transportation Dashboard",
    layout="wide"
)

st.title("🚚 Transportation Route Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("transport.csv")

# Clean column names
df.columns = df.columns.str.strip()

# ---------------- KPI SECTION ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Routes", len(df))

col2.metric(
    "Total Distance",
    int(df["Avg Distance Per Month"].sum())
)

col3.metric(
    "Longest Route",
    int(df["Avg Distance Per Month"].max())
)

# ---------------- BAR CHART ----------------
st.subheader("📊 Top Transportation Routes")

top_routes = df.sort_values(
    by="Avg Distance Per Month",
    ascending=False
)

fig = px.bar(
    top_routes.head(10),
    x="Avg Distance Per Month",
    y="Source",
    orientation="h",
    color="Avg Distance Per Month",
    hover_data=["Destination"],
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- GEOCODER ----------------
geolocator = Nominatim(user_agent="transport_dashboard")

@st.cache_data
def get_coordinates(place):

    try:
        location = geolocator.geocode(place)

        time.sleep(1)

        if location:
            return location.latitude, location.longitude

    except:
        pass

    return None, None

# ---------------- CREATE MAP DATA ----------------
map_data = []

for _, row in df.iterrows():

    s_lat, s_lon = get_coordinates(row["Source"])
    d_lat, d_lon = get_coordinates(row["Destination"])

    if None not in [s_lat, s_lon, d_lat, d_lon]:

        map_data.append({
            "from_name": row["Source"],
            "to_name": row["Destination"],

            "from_lat": s_lat,
            "from_lon": s_lon,

            "to_lat": d_lat,
            "to_lon": d_lon,

            "distance": row["Avg Distance Per Month"]
        })

map_df = pd.DataFrame(map_data)

# ---------------- ARC LAYER ----------------
arc_layer = pdk.Layer(
    "ArcLayer",
    data=map_df,

    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],

    get_source_color=[255, 0, 0],
    get_target_color=[0, 128, 255],

    get_width=3,

    pickable=True,
    auto_highlight=True
)

# ---------------- VIEW ----------------
view_state = pdk.ViewState(
    latitude=22.5937,
    longitude=78.9629,
    zoom=4,
    pitch=30
)

# ---------------- TOOLTIP ----------------
tooltip = {
    "html": """
    <b>Source:</b> {from_name}<br/>
    <b>Destination:</b> {to_name}<br/>
    <b>Distance:</b> {distance} KM
    """,

    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# ---------------- MAP ----------------
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",

    initial_view_state=view_state,

    layers=[arc_layer],

    tooltip=tooltip
)

# ---------------- SHOW MAP ----------------
st.subheader("🗺 Route Map")

st.pydeck_chart(deck)

# ---------------- TABLE ----------------
st.subheader("📄 Transportation Data")

st.dataframe(df)
