
import streamlit.components.v1 as components
import requests
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Weather App", layout="centered")

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&temperature_unit=fahrenheit"
    response = requests.get(url)
    data = response.json()
    return data['current']['temperature_2m']

st.title("🌤️ Weather")

location = streamlit_geolocation()

if location and location.get("latitude"):
    lat = location["latitude"]
    lon = location["longitude"]
    
    try:
        temp = get_weather(lat, lon)
        
        tab1, tab2 = st.tabs(["Current", "Radar"])
        
        with tab1:
            st.metric("Current Temperature", f"{temp}°F")
            
        with tab2:
            st.write("Live Radar")
            radar_url = f"https://embed.windy.com/embed.html?lat={lat}&lon={lon}&overlay=radar"
            components.iframe(radar_url, height=300)
            
    except Exception as e:
        st.error(f"Could
