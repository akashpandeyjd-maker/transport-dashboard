# ---------------------------------------------------

# MAP SECTION

# ---------------------------------------------------

with right:

```
st.subheader("🗺 Route Map")

# ROUTE LINES
arc_layer = pdk.Layer(
    "ArcLayer",
    data=map_df,

    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],

    get_source_color=[255, 0, 0],
    get_target_color=[0, 128, 255],

    get_width=4,

    pickable=True,
    auto_highlight=True
)

# SOURCE CITY POINTS
scatter_source = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,

    get_position=["from_lon", "from_lat"],

    get_radius=50000,

    get_fill_color=[255, 140, 0],

    pickable=True
)

# DESTINATION CITY POINTS
scatter_destination = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,

    get_position=["to_lon", "to_lat"],

    get_radius=50000,

    get_fill_color=[0, 128, 255],

    pickable=True
)

# INDIA VIEW
view_state = pdk.ViewState(
    latitude=22.5937,
    longitude=78.9629,
    zoom=4,
    pitch=35
)

# MAP
deck = pdk.Deck(
    map_style="light",

    initial_view_state=view_state,

    layers=[
        arc_layer,
        scatter_source,
        scatter_destination
    ],

    tooltip={
        "html": """
        <b>Source:</b> {from_name}<br/>
        <b>Destination:</b> {to_name}<br/>
        <b>Distance:</b> {distance} KM
        """,

        "style": {
            "backgroundColor": "black",
            "color": "white"
        }
    }
)

st.pydeck_chart(deck)
```
