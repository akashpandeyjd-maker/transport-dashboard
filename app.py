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

# Clean columns
df.columns = df.columns.str.strip()

# ---------------- KPI CARDS ----------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Routes",
    len(df)
)

col2.metric(
    "Total Avg Distance",
    int(df["Avg Distance Per Month"].sum())
)

col3.metric(
    "Longest Route",
    int(df["Avg Distance Per Month"].max())
)

# ---------------- TOP ROUTES ----------------
st.subheader("📊 Top Routes")

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
        location = geolocator.geocode(place + ", India")

        time.sleep(1)

        if location:
            return [location.longitude, location.latitude]

    except:
        pass

    return None

# ---------------- COORDINATES ----------------
paths = []

for _, row in df.iterrows():

    source = get_coordinates(row["Source"])
    destination = get_coordinates(row["Destination"])

    if source and destination:

        paths.append({
            "path": [source, destination],
            "distance": row["Avg Distance Per Month"],
            "source": row["Source"],
            "destination": row["Destination"]
        })

# ---------------- MAP LAYER ----------------
path_layer = pdk.Layer(
    "PathLayer",
    data=paths,

    get_path="path",

    get_width=5,

    get_color="[255, 0, 0]",

    width_min_pixels=2,

    pickable=True
)

# ---------------- VIEW ----------------
view_state = pdk.ViewState(
    latitude=22.5,
    longitude=80,
    zoom=4,
    pitch=0
)

# ---------------- TOOLTIP ----------------
tooltip = {
    "html": """
    <b>Source:</b> {source}<br/>
    <b>Destination:</b> {destination}<br/>
    <b>Distance:</b> {distance} KM
    """,

    "style": {
        "backgroundColor": "black",
        "color": "white"
    }
}

# ---------------- MAP ----------------
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",

    initial_view_state=view_state,

    layers=[path_layer],

    tooltip=tooltip
)

# ---------------- SHOW MAP ----------------
st.subheader("🗺 Transportation Route Map")

st.pydeck_chart(deck)

# ---------------- TABLE ----------------
st.subheader("📄 Transportation Data")

st.dataframe(df)
