import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from geopy.geocoders import Nominatim
import time

# ---------------- PAGE ----------------
st.set_page_config(layout="wide")

st.title("🚚 Transportation Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_csv("transport.csv")

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

# ---------------- KPI ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Routes", len(df))

col2.metric(
    "Total Avg Distance",
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
    top_routes,
    x="Avg Distance Per Month",
    y="Source",
    orientation="h",
    color="Avg Distance Per Month",
    hover_data=["Destination"],
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- MAP ----------------
st.subheader("🗺 Route Map")

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

# Coordinates
source_lat = []
source_lon = []

dest_lat = []
dest_lon = []

for _, row in df.iterrows():

    slat, slon = get_coordinates(row["Source"])
    dlat, dlon = get_coordinates(row["Destination"])

    source_lat.append(slat)
    source_lon.append(slon)

    dest_lat.append(dlat)
    dest_lon.append(dlon)

df["source_lat"] = source_lat
df["source_lon"] = source_lon

df["dest_lat"] = dest_lat
df["dest_lon"] = dest_lon

# Remove blanks
map_df = df.dropna()

# ---------------- ARC LAYER ----------------
arc_layer = pdk.Layer(
    "ArcLayer",
    data=map_df,

    get_source_position='[source_lon, source_lat]',
    get_target_position='[dest_lon, dest_lat]',

    get_width='Avg Distance Per Month / 200',

    get_source_color='[255, 0, 0]',
    get_target_color='[0, 128, 255]',

    pickable=True,
    auto_highlight=True
)

# ---------------- VIEW ----------------
view_state = pdk.ViewState(
    latitude=22.5937,
    longitude=78.9629,
    zoom=4,
    pitch=40
)

# ---------------- TOOLTIP ----------------
tooltip = {
    "html": """
    <b>Source:</b> {Source}<br/>
    <b>Destination:</b> {Destination}<br/>
    <b>Avg Distance:</b> {Avg Distance Per Month} KM
    """,

    "style": {
        "backgroundColor": "black",
        "color": "white"
    }
}

# ---------------- MAP ----------------
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",

    initial_view_state=view_state,

    layers=[arc_layer],

    tooltip=tooltip
)

st.pydeck_chart(deck)

# ---------------- DATA ----------------
st.subheader("📄 Transportation Data")

st.dataframe(df)
