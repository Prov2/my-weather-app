import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic

# Configuration
API_URL = "https://api.open-meteo.com/v1/forecast"
API_TIMEOUT = 5
WEATHER_CACHE_TTL = 600  # 10 minutes

# Cities with population over 70,000
CITIES = [
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "population": 8335897},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "population": 3971883},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "population": 2696156},
    {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "population": 2320268},
    {"name": "Phoenix", "lat": 33.4484, "lon": -112.0742, "population": 1580574},
    {"name": "Philadelphia", "lat": 39.9526, "lon": -75.1652, "population": 1567872},
    {"name": "San Antonio", "lat": 29.4241, "lon": -98.4936, "population": 1547253},
    {"name": "San Diego", "lat": 32.7157, "lon": -117.1611, "population": 1386932},
    {"name": "Dallas", "lat": 32.7767, "lon": -96.7970, "population": 1343573},
    {"name": "San Jose", "lat": 37.3382, "lon": -121.8863, "population": 1021795},
    {"name": "Austin", "lat": 30.2672, "lon": -97.7431, "population": 978908},
    {"name": "Jacksonville", "lat": 30.3322, "lon": -81.6557, "population": 949611},
    {"name": "Fort Worth", "lat": 32.7555, "lon": -97.3308, "population": 909585},
    {"name": "Columbus", "lat": 39.9612, "lon": -82.9988, "population": 898553},
    {"name": "Charlotte", "lat": 35.2271, "lon": -80.8431, "population": 885708},
    {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194, "population": 883305},
    {"name": "Indianapolis", "lat": 39.7684, "lon": -86.1581, "population": 876384},
    {"name": "Seattle", "lat": 47.6062, "lon": -122.3321, "population": 753675},
    {"name": "Denver", "lat": 39.7392, "lon": -104.9903, "population": 727211},
    {"name": "Boston", "lat": 42.3601, "lon": -71.0589, "population": 692600},
    {"name": "El Paso", "lat": 31.7619, "lon": -106.4850, "population": 678121},
    {"name": "Nashville", "lat": 36.1627, "lon": -86.7816, "population": 715884},
    {"name": "Detroit", "lat": 42.3314, "lon": -83.0458, "population": 639111},
    {"name": "Oklahoma City", "lat": 35.4676, "lon": -97.5164, "population": 655057},
    {"name": "Portland", "lat": 45.5152, "lon": -122.6784, "population": 652503},
    {"name": "Las Vegas", "lat": 36.1699, "lon": -115.1398, "population": 603488},
    {"name": "Memphis", "lat": 35.1264, "lon": -90.0176, "population": 628127},
    {"name": "Louisville", "lat": 38.2527, "lon": -85.7585, "population": 633045},
    {"name": "Baltimore", "lat": 39.2904, "lon": -76.6122, "population": 585708},
    {"name": "Milwaukee", "lat": 43.0389, "lon": -87.9065, "population": 577222},
    {"name": "Albuquerque", "lat": 35.0844, "lon": -106.6504, "population": 564559},
    {"name": "Tucson", "lat": 32.2226, "lon": -110.9747, "population": 525796},
    {"name": "Fresno", "lat": 36.7378, "lon": -119.7871, "population": 525010},
    {"name": "Sacramento", "lat": 38.5816, "lon": -121.4944, "population": 524943},
    {"name": "Long Beach", "lat": 33.7701, "lon": -118.1937, "population": 462632},
    {"name": "Kansas City", "lat": 39.0997, "lon": -94.5786, "population": 508090},
    {"name": "Mesa", "lat": 33.4152, "lon": -111.8313, "population": 504258},
    {"name": "Virginia Beach", "lat": 36.8529, "lon": -75.9780, "population": 450189},
    {"name": "Atlanta", "lat": 33.7490, "lon": -84.3880, "population": 498044},
    {"name": "New Orleans", "lat": 29.9511, "lon": -90.2623, "population": 383997},
    {"name": "Cleveland", "lat": 41.4993, "lon": -81.6944, "population": 372624},
    {"name": "Wichita", "lat": 37.6872, "lon": -97.3301, "population": 389577},
    {"name": "Arlington", "lat": 32.7357, "lon": -97.2250, "population": 394266},
    {"name": "Bakersfield", "lat": 35.3733, "lon": -119.0187, "population": 403455},
    {"name": "Tampa", "lat": 27.9506, "lon": -82.4572, "population": 399700},
    {"name": "Aurora", "lat": 39.7294, "lon": -104.8202, "population": 397337},
    {"name": "Anaheim", "lat": 33.8353, "lon": -117.9129, "population": 346411},
    {"name": "Santa Ana", "lat": 33.7455, "lon": -117.8677, "population": 310127},
    {"name": "St. Louis", "lat": 38.6270, "lon": -90.1994, "population": 301578},
    {"name": "Riverside", "lat": 33.9381, "lon": -117.2961, "population": 303871},
    {"name": "Corpus Christi", "lat": 27.5604, "lon": -97.3964, "population": 317863},
    {"name": "Lexington", "lat": 38.2009, "lon": -84.8733, "population": 322147},
    {"name": "Henderson", "lat": 36.0395, "lon": -115.0227, "population": 320189},
    {"name": "Plano", "lat": 33.0198, "lon": -96.6989, "population": 299426},
    {"name": "Orlando", "lat": 28.5421, "lon": -81.3723, "population": 307573},
    {"name": "Chula Vista", "lat": 32.6401, "lon": -117.0842, "population": 275487},
    {"name": "Chandler", "lat": 33.3062, "lon": -111.8413, "population": 276228},
    {"name": "Irving", "lat": 32.8140, "lon": -96.9489, "population": 256373},
    {"name": "Garland", "lat": 32.9126, "lon": -96.6345, "population": 238002},
    {"name": "Glendale", "lat": 33.5389, "lon": -112.1853, "population": 246709},
    {"name": "Winston-Salem", "lat": 36.0999, "lon": -80.2453, "population": 248657},
    {"name": "Laredo", "lat": 27.5364, "lon": -97.5090, "population": 260654},
    {"name": "Lubbock", "lat": 33.5779, "lon": -101.8552, "population": 253537},
    {"name": "Madison", "lat": 43.0731, "lon": -89.4012, "population": 269840},
    {"name": "Durham", "lat": 35.9940, "lon": -78.8985, "population": 283506},
    {"name": "Raleigh", "lat": 35.7796, "lon": -78.6382, "population": 474069},
    {"name": "Baton Rouge", "lat": 30.4515, "lon": -91.1871, "population": 227818},
    {"name": "Norfolk", "lat": 36.8507, "lon": -76.2859, "population": 238005},
    {"name": "Anchorage", "lat": 61.2181, "lon": -149.9003, "population": 291826},
    {"name": "Stockton", "lat": 37.9577, "lon": -121.2908, "population": 320554},
    {"name": "Toledo", "lat": 41.6639, "lon": -83.5552, "population": 274975},
    {"name": "Saint Paul", "lat": 44.9537, "lon": -93.0900, "population": 311527},
    {"name": "Minneapolis", "lat": 44.9778, "lon": -93.2650, "population": 429954},
    {"name": "Greensboro", "lat": 36.0726, "lon": -79.7920, "population": 290711},
    {"name": "Henderson", "lat": 36.0395, "lon": -115.0227, "population": 320189},
]

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

# 2. Find nearby cities
def find_nearby_cities(lat, lon, max_results=10):
    """Find nearby cities sorted by distance."""
    try:
        user_location = (lat, lon)
        distances = []
        
        for city in CITIES:
            city_location = (city["lat"], city["lon"])
            distance = geodesic(user_location, city_location).miles
            distances.append((city["name"], city["lat"], city["lon"], distance))
        
        # Sort by distance and return top results
        distances.sort(key=lambda x: x[3])
        return distances[:max_results]
    except Exception as e:
        st.error(f"Error finding nearby cities: {str(e)}")
        return []

# 3. Fetch Weather Data
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

# 4. Get Weather Code Description
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

# 5. Display Weather Data
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

# Create three columns for location options
col1, col2, col3 = st.columns(3)

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

# Option 3: Select from nearby cities
with col3:
    st.subheader("Option 3: Nearby Cities")
    if hasattr(st.session_state, 'lat') and hasattr(st.session_state, 'lon'):
        nearby = find_nearby_cities(st.session_state.lat, st.session_state.lon, max_results=10)
        
        if nearby:
            city_options = [f"{city[0]} ({city[3]:.1f} mi)" for city in nearby]
            selected_city = st.selectbox("Select a nearby city:", city_options, key="nearby_city_select")
            
            if st.button("📍 View City Weather"):
                selected_idx = city_options.index(selected_city)
                city_name, city_lat, city_lon, _ = nearby[selected_idx]
                st.session_state.lat = city_lat
                st.session_state.lon = city_lon
        else:
            st.info("Get your location first to see nearby cities")
    else:
        st.info("Get your location first to see nearby cities")

# Option 4: Search all cities
st.subheader("Option 4: Search All Cities")
city_search = st.selectbox("Search cities with population over 70,000:", 
                           [f"{city['name']}" for city in CITIES],
                           key="city_search_select")

if st.button("🌍 View Weather for Selected City"):
    selected_city = next(c for c in CITIES if c['name'] == city_search)
    st.session_state.lat = selected_city['lat']
    st.session_state.lon = selected_city['lon']

# Process weather if coordinates exist
if hasattr(st.session_state, 'lat') and hasattr(st.session_state, 'lon'):
    try:
        with st.spinner("Loading weather data..."):
            weather = get_weather(st.session_state.lat, st.session_state.lon)
        display_weather(st.session_state.lat, st.session_state.lon, weather)
    except Exception as e:
        st.error(f"❌ Error fetching weather data: {str(e)}")
        st.info("Please try again in a moment.")
