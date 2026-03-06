import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
from geopy.distance import geodesic
import time

# -------------------------
# CONFIG
# -------------------------
API_URL = "https://y-215481049324.europe-west1.run.app/predict"

st.set_page_config(
    page_title="🚕 Ultimate Taxi Fare Estimator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# STYLES
# -------------------------
st.markdown("""
<style>
.title {font-size:48px;font-weight:bold;text-align:center;}
.sub {font-size:18px;color:grey;text-align:center;}
.result-big {
    padding:20px;
    border-radius:12px;
    font-size:34px;
    font-weight:700;
    text-align:center;
    margin-top:10px;
}
.stat-box {
    padding:15px;
    border-radius:8px;
    background:#e8eefc;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🚕 Ultimate Taxi Fare Estimator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub">Click on the map to choose pickup and dropoff</p>', unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
if "pickup" not in st.session_state:
    st.session_state.pickup = None
if "dropoff" not in st.session_state:
    st.session_state.dropoff = None
if "map_theme" not in st.session_state:
    st.session_state.map_theme = "CartoDB Dark_Matter"
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.header("Trip Settings")
    toggle = st.radio("Map Theme", ["Dark Mode", "Light Mode"])
    if toggle == "Dark Mode":
        st.session_state.map_theme = "CartoDB Dark_Matter"
        result_bg = "#1a1a1a"
        result_color = "#f6f6f8"
    else:
        st.session_state.map_theme = "CartoDB positron"
        result_bg = "#f6f6f8"
        result_color = "#1a1a1a"
    st.markdown("---")
    st.write("Click map → pickup → dropoff")

# -------------------------
# MAP
# -------------------------
m = folium.Map(location=[40.73, -73.99], zoom_start=12, tiles=st.session_state.map_theme)

if st.session_state.pickup:
    folium.Marker(
        st.session_state.pickup,
        tooltip="Pickup",
        icon=folium.Icon(color="green")
    ).add_to(m)

if st.session_state.dropoff:
    folium.Marker(
        st.session_state.dropoff,
        tooltip="Dropoff",
        icon=folium.Icon(color="red")
    ).add_to(m)

if st.session_state.pickup and st.session_state.dropoff:
    folium.PolyLine(
        [st.session_state.pickup, st.session_state.dropoff],
        color="orange", weight=4
    ).add_to(m)

map_data = st_folium(m, height=500, width=900)

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    point = (lat, lon)

    if st.session_state.pickup is None:
        st.session_state.pickup = point
        st.rerun()
    elif st.session_state.dropoff is None:
        st.session_state.dropoff = point
        st.rerun()

# -------------------------
# COORDINATES DISPLAY
# -------------------------
col1, col2 = st.columns(2)
with col1:
    if st.session_state.pickup:
        st.success(f"📍 Pickup: {st.session_state.pickup}")
with col2:
    if st.session_state.dropoff:
        st.success(f"🏁 Dropoff: {st.session_state.dropoff}")

# -------------------------
# TRIP DETAILS
# -------------------------
date_col, time_col = st.columns(2)
with date_col:
    pickup_date = st.date_input("Pickup Date")
with time_col:
    pickup_time = st.time_input("Pickup Time")

passenger_count = st.slider("Passengers", 1, 8, 1)

# -------------------------
# PREDICTION
# -------------------------
if st.button("Estimate Fare 💰"):

    if not (st.session_state.pickup and st.session_state.dropoff):
        st.warning("Select pickup and dropoff first!")
    else:

        # Loading animation
        load_slot = st.empty()
        bar = st.progress(0)
        for i in range(100):
            load_slot.markdown(f"🚕 Calculating... {i+1}%")
            bar.progress(i+1)
            time.sleep(0.01)
        load_slot.empty()

        pickup_datetime = datetime.combine(pickup_date, pickup_time).isoformat()
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": st.session_state.pickup[1],
            "pickup_latitude": st.session_state.pickup[0],
            "dropoff_longitude": st.session_state.dropoff[1],
            "dropoff_latitude": st.session_state.dropoff[0],
            "passenger_count": passenger_count
        }

        response = requests.get(API_URL, params=params).json()

        if "fare" in response:
            fare = response["fare"]

            st.session_state.history.append(fare)

            dist_km = geodesic(st.session_state.pickup, st.session_state.dropoff).km
            est_time = dist_km / 0.4  # ~40 km/h

            # ---- PRICE + GIF côte à côte ----
            col_price, col_gif = st.columns([2, 1])
            with col_price:
                st.markdown(
                    f'<div class="result-big" style="background:{result_bg}; color:{result_color};">💸 Fare: ${fare:.2f}</div>',
                    unsafe_allow_html=True
                )
            with col_gif:
                st.image("https://media.giphy.com/media/3o85xIO33l7RlmLR4I/giphy.gif", width=150)

            # Trip summary
            with st.expander("📊 Trip Summary", expanded=True):
                st.write(f"🛣️ Distance: {dist_km:.2f} km")
                st.write(f"⏱️ Estimated time: ~{int(est_time)} min")
                st.write(f"👥 Passengers: {passenger_count}")

        else:
            st.error("API Error!")
            st.write(response)

# -------------------------
# HISTORY
# -------------------------
if st.session_state.history:
    st.subheader("📈 Fare history")
    st.line_chart(st.session_state.history)

# -------------------------
# RESET
# -------------------------
if st.button("🧹 Reset Trip"):
    st.session_state.pickup = None
    st.session_state.dropoff = None
    st.session_state.history = []
    st.rerun()
