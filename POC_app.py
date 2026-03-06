import streamlit as st
import requests
from datetime import datetime

st.markdown('''
# Taxi Fare Prediction
''')

st.markdown("Enter ride information to estimate the fare.")

pickup_date = st.date_input("Pickup date")
pickup_time = st.time_input("Pickup time")

pickup_longitude = st.number_input("Pickup longitude", value=-73.99)
pickup_latitude = st.number_input("Pickup latitude", value=40.73)

dropoff_longitude = st.number_input("Dropoff longitude", value=-73.98)
dropoff_latitude = st.number_input("Dropoff latitude", value=40.76)

passenger_count = st.slider("Passenger count", 1, 8, 1)

pickup_datetime = datetime.combine(pickup_date, pickup_time)

params = {
    "pickup_datetime": pickup_datetime.isoformat(),
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

my_api = "https://y-215481049324.europe-west1.run.app/predict"

if st.button("Predict fare"):
    response = requests.get(my_api, params=params)
    prediction = round(response.json()["fare"], 2)
    st.write(f"Estimated fare: ${prediction}")
