st
import requests
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Weather App", layout="centered")

st.title("🌤️ Weather")

# 1. Get Location
# Use a timeout of 5-10 seconds and lower accuracy for faster results
location = streamlit_geolocation(timeout=10000, enableHighAccuracy=False)


if location and location.get("latitude"):
    lat, lon = location["latitude"], location["longitude"]
    
    # 2. Fetch Data
    @st.cache_data(ttl=600) # Cache weather for 10 minutes
    def get_weather(lat, lon):
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&temperature_unit=fahrenheit").json()
        return w['current']['temperature_2m']

    temp = get_weather(lat, lon)
    
    # 3. UI Tabs
    tab1, tab2, tab3 = st.tabs(["Current", "Radar", "Settings"])
    
          with tab2:
              
