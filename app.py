import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

# Configuration
API_URL = "https://api.open-meteo.com/v1/forecast"
API_TIMEOUT = 5
WEATHER_CACHE_TTL = 600  # 10 minutes

st.set_page_config(page_title="Weather App", layout="centered")

st.title("🌤️ Weather App")

# 1. Get Location
def validate_location(location):
    """Validate location coordinates are within valid ranges."""
    if not location or not location.get("latitude") or not location.get("longitude"):
        return False, "Location data is incomplete"
    
    lat = location["latitude"]
    lon = location["longitude"]
    
    if not (-90 <= lat <= 90):
        return False, "Latitude must be between -90 and 90"
    if not (-180 <= lon <= 180):
        return False, "Longitude must be between -180 and 180"
    
    return True, (lat, lon)

# 2. Fetch Weather Data
@st.cache_data(ttl=WEATHER_CACHE_TTL)
def get_weather(lat, lon):
    """Fetch weather data from Open-Meteo API."""
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit"
        }
        
        response = requests.get(API_URL, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        return data['current']
    
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"API error: {response.status_code}")
    except (KeyError, ValueError):
        raise Exception("Invalid response format from weather API")

# 3. Get Weather Code Description
def get_weather_description(code):
    """Convert WMO weather code to human-readable description."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with large hail"
    }
    return weather_codes.get(code, "Unknown")

# 4. Display Weather Data
def display_weather(lat, lon, weather):
    """Display weather information in tabs."""
    # Display weather tabs
    tab1, tab2 = st.tabs(["Current Weather", "Radar"])
    
    # Tab 1: Current Weather
    with tab1:
        st.subheader(f"Weather at ({lat:.2f}, {lon:.2f})")
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Temperature",
                f"{int(weather['temperature_2m'])}°F"
            )
        
        with col2:
            st.metric(
                "Humidity",
                f"{int(weather['relative_humidity_2m'])}%"
            )
        
        with col3:
            st.metric(
                "Wind Speed",
                f"{int(weather['wind_speed_10m'])} mph"
            )
        
        # Display weather condition
        weather_desc = get_weather_description(weather['weather_code'])
        st.info(f"**Conditions**: {weather_desc}")
    
    # Tab 2: Radar
    with tab2:
        st.subheader("Live Weather Radar")
        radar_url = f"https://embed.windy.com/embed.html?lat={lat}&lon={lon}&overlay=radar&menu=&type=map&location=coordinates"
        
        st.components.v1.html(
            f'<iframe src="{radar_url}" height="500" width="100%" frameborder="0"></iframe>',
            height=500,
            scrolling=False
        )

# Main App Logic
st.write("Get weather for your location:")

# Create two columns for location options
col1, col2 = st.columns(2)

# Option 1: Auto-detect location
with col1:
    st.subheader("Option 1: Auto-Detect")
    if st.button("📍 Get My Location"):
        location = streamlit_geolocation()
        is_valid, location_data = validate_location(location)
        
        if is_valid:
            lat, lon = location_data
            st.session_state.lat = lat
            st.session_state.lon = lon
        else:
            st.warning("⚠️ " + str(location_data))
            st.info("Please enable location access in your browser to see weather for your area.")

# Option 2: Manual entry
with col2:
    st.subheader("Option 2: Manual Entry")
    lat = st.number_input("Latitude", value=0.0, min_value=-90.0, max_value=90.0, key="lat_input")
    lon = st.number_input("Longitude", value=0.0, min_value=-180.0, max_value=180.0, key="lon_input")
    
    if st.button("🔍 Get Weather"):
        st.session_state.lat = lat
        st.session_state.lon = lon

# Process weather if coordinates exist
if hasattr(st.session_state, 'lat') and hasattr(st.session_state, 'lon'):
    try:
        with st.spinner("Loading weather data..."):
            weather = get_weather(st.session_state.lat, st.session_state.lon)
        display_weather(st.session_state.lat, st.session_state.lon, weather)
    except Exception as e:
        st.error(f"❌ Error fetching weather data: {str(e)}")
        st.info("Please try again in a moment.")
