import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Weather App", layout="centered")

st.title("🌤️ Weather")

# 1. Get Location
location = streamlit_geolocation(timeout=10000, enableHighAccuracy=False)

if location and location.get("latitude"):
    lat = location["latitude"]
    lon = location["longitude"]
    
    # 2. Fetch Data
    @st.cache_data(ttl=600)  # Cache weather for 10 minutes
    def get_weather(lat, lon):
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&temperature_unit=fahrenheit").json()
        return w['current']['temperature_2m']
    
    try:
        temp = get_weather(lat, lon)
        
        tab1, tab2 = st.tabs(["Current", "Radar"])
        
        with tab1:
            st.metric("Current Temperature", f"{temp}°F")
            
        with tab2:
            st.write("Live Radar")
            radar_url = f"https://embed.windy.com/embed.html?lat={lat}&lon={lon}&overlay=radar"
            st.components.v1.iframe(radar_url, height=300)
            
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
else:
    st.info("Please enable location access to see the weather for your area.")
