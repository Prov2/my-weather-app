import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic
import json

# Configuration
API_URL = "https://api.open-meteo.com/v1/forecast"
API_TIMEOUT = 5
WEATHER_CACHE_TTL = 600  # 10 minutes

st.set_page_config(page_title="Weather App", layout="wide", initial_sidebar_state="expanded")

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .temperature-display {
        font-size: 48px;
        font-weight: bold;
    }
    .city-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .city-card:hover {
        transform: scale(1.02);
        background: #e0e2e6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'lon' not in st.session_state:
    st.session_state.lon = None
if 'current_city' not in st.session_state:
    st.session_state.current_city = None

# Load US cities database (all cities with population > 70,000)
US_CITIES = [
    {"name": "New York", "state": "NY", "lat": 40.7128, "lon": -74.0060, "population": 8335897},
    {"name": "Los Angeles", "state": "CA", "lat": 34.0522, "lon": -118.2437, "population": 3971883},
    {"name": "Chicago", "state": "IL", "lat": 41.8781, "lon": -87.6298, "population": 2696156},
    {"name": "Houston", "state": "TX", "lat": 29.7604, "lon": -95.3698, "population": 2320268},
    {"name": "Phoenix", "state": "AZ", "lat": 33.4484, "lon": -112.0742, "population": 1580574},
    {"name": "Philadelphia", "state": "PA", "lat": 39.9526, "lon": -75.1652, "population": 1567872},
    {"name": "San Antonio", "state": "TX", "lat": 29.4241, "lon": -98.4936, "population": 1547253},
    {"name": "San Diego", "state": "CA", "lat": 32.7157, "lon": -117.1611, "population": 1386932},
    {"name": "Dallas", "state": "TX", "lat": 32.7767, "lon": -96.7970, "population": 1343573},
    {"name": "San Jose", "state": "CA", "lat": 37.3382, "lon": -121.8863, "population": 1021795},
    {"name": "Austin", "state": "TX", "lat": 30.2672, "lon": -97.7431, "population": 978908},
    {"name": "Jacksonville", "state": "FL", "lat": 30.3322, "lon": -81.6557, "population": 949611},
    {"name": "Fort Worth", "state": "TX", "lat": 32.7555, "lon": -97.3308, "population": 909585},
    {"name": "Columbus", "state": "OH", "lat": 39.9612, "lon": -82.9988, "population": 898553},
    {"name": "Charlotte", "state": "NC", "lat": 35.2271, "lon": -80.8431, "population": 885708},
    {"name": "San Francisco", "state": "CA", "lat": 37.7749, "lon": -122.4194, "population": 883305},
    {"name": "Indianapolis", "state": "IN", "lat": 39.7684, "lon": -86.1581, "population": 876384},
    {"name": "Seattle", "state": "WA", "lat": 47.6062, "lon": -122.3321, "population": 753675},
    {"name": "Denver", "state": "CO", "lat": 39.7392, "lon": -104.9903, "population": 727211},
    {"name": "Boston", "state": "MA", "lat": 42.3601, "lon": -71.0589, "population": 692600},
    {"name": "El Paso", "state": "TX", "lat": 31.7619, "lon": -106.4850, "population": 678121},
    {"name": "Nashville", "state": "TN", "lat": 36.1627, "lon": -86.7816, "population": 715884},
    {"name": "Detroit", "state": "MI", "lat": 42.3314, "lon": -83.0458, "population": 639111},
    {"name": "Oklahoma City", "state": "OK", "lat": 35.4676, "lon": -97.5164, "population": 655057},
    {"name": "Portland", "state": "OR", "lat": 45.5152, "lon": -122.6784, "population": 652503},
    {"name": "Las Vegas", "state": "NV", "lat": 36.1699, "lon": -115.1398, "population": 603488},
    {"name": "Memphis", "state": "TN", "lat": 35.1264, "lon": -90.0176, "population": 628127},
    {"name": "Louisville", "state": "KY", "lat": 38.2527, "lon": -85.7585, "population": 633045},
    {"name": "Baltimore", "state": "MD", "lat": 39.2904, "lon": -76.6122, "population": 585708},
    {"name": "Milwaukee", "state": "WI", "lat": 43.0389, "lon": -87.9065, "population": 577222},
    {"name": "Albuquerque", "state": "NM", "lat": 35.0844, "lon": -106.6504, "population": 564559},
    {"name": "Tucson", "state": "AZ", "lat": 32.2226, "lon": -110.9747, "population": 525796},
    {"name": "Fresno", "state": "CA", "lat": 36.7378, "lon": -119.7871, "population": 525010},
    {"name": "Sacramento", "state": "CA", "lat": 38.5816, "lon": -121.4944, "population": 524943},
    {"name": "Long Beach", "state": "CA", "lat": 33.7701, "lon": -118.1937, "population": 462632},
    {"name": "Kansas City", "state": "MO", "lat": 39.0997, "lon": -94.5786, "population": 508090},
    {"name": "Mesa", "state": "AZ", "lat": 33.4152, "lon": -111.8313, "population": 504258},
    {"name": "Virginia Beach", "state": "VA", "lat": 36.8529, "lon": -75.9780, "population": 450189},
    {"name": "Atlanta", "state": "GA", "lat": 33.7490, "lon": -84.3880, "population": 498044},
    {"name": "New Orleans", "state": "LA", "lat": 29.9511, "lon": -90.2623, "population": 383997},
    {"name": "Cleveland", "state": "OH", "lat": 41.4993, "lon": -81.6944, "population": 372624},
    {"name": "Wichita", "state": "KS", "lat": 37.6872, "lon": -97.3301, "population": 389577},
    {"name": "Arlington", "state": "TX", "lat": 32.7357, "lon": -97.2250, "population": 394266},
    {"name": "Bakersfield", "state": "CA", "lat": 35.3733, "lon": -119.0187, "population": 403455},
    {"name": "Tampa", "state": "FL", "lat": 27.9506, "lon": -82.4572, "population": 399700},
    {"name": "Aurora", "state": "CO", "lat": 39.7294, "lon": -104.8202, "population": 397337},
    {"name": "Anaheim", "state": "CA", "lat": 33.8353, "lon": -117.9129, "population": 346411},
    {"name": "Santa Ana", "state": "CA", "lat": 33.7455, "lon": -117.8677, "population": 310127},
    {"name": "St. Louis", "state": "MO", "lat": 38.6270, "lon": -90.1994, "population": 301578},
    {"name": "Riverside", "state": "CA", "lat": 33.9381, "lon": -117.2961, "population": 303871},
    {"name": "Corpus Christi", "state": "TX", "lat": 27.5604, "lon": -97.3964, "population": 317863},
    {"name": "Lexington", "state": "KY", "lat": 38.2009, "lon": -84.8733, "population": 322147},
    {"name": "Henderson", "state": "NV", "lat": 36.0395, "lon": -115.0227, "population": 320189},
    {"name": "Plano", "state": "TX", "lat": 33.0198, "lon": -96.6989, "population": 299426},
    {"name": "Orlando", "state": "FL", "lat": 28.5421, "lon": -81.3723, "population": 307573},
    {"name": "Chula Vista", "state": "CA", "lat": 32.6401, "lon": -117.0842, "population": 275487},
    {"name": "Chandler", "state": "AZ", "lat": 33.3062, "lon": -111.8413, "population": 276228},
    {"name": "Irving", "state": "TX", "lat": 32.8140, "lon": -96.9489, "population": 256373},
    {"name": "Garland", "state": "TX", "lat": 32.9126, "lon": -96.6345, "population": 238002},
    {"name": "Glendale", "state": "AZ", "lat": 33.5389, "lon": -112.1853, "population": 246709},
    {"name": "Winston-Salem", "state": "NC", "lat": 36.0999, "lon": -80.2453, "population": 248657},
    {"name": "Laredo", "state": "TX", "lat": 27.5364, "lon": -97.5090, "population": 260654},
    {"name": "Lubbock", "state": "TX", "lat": 33.5779, "lon": -101.8552, "population": 253537},
    {"name": "Madison", "state": "WI", "lat": 43.0731, "lon": -89.4012, "population": 269840},
    {"name": "Durham", "state": "NC", "lat": 35.9940, "lon": -78.6985, "population": 283506},
    {"name": "Raleigh", "state": "NC", "lat": 35.7796, "lon": -78.6382, "population": 474069},
    {"name": "Baton Rouge", "state": "LA", "lat": 30.4515, "lon": -91.1871, "population": 227818},
    {"name": "Norfolk", "state": "VA", "lat": 36.8507, "lon": -76.2859, "population": 238005},
    {"name": "Anchorage", "state": "AK", "lat": 61.2181, "lon": -149.9003, "population": 291826},
    {"name": "Stockton", "state": "CA", "lat": 37.9577, "lon": -121.2908, "population": 320554},
    {"name": "Toledo", "state": "OH", "lat": 41.6639, "lon": -83.5552, "population": 274975},
    {"name": "Saint Paul", "state": "MN", "lat": 44.9537, "lon": -93.0900, "population": 311527},
    {"name": "Minneapolis", "state": "MN", "lat": 44.9778, "lon": -93.2650, "population": 429954},
    {"name": "Greensboro", "state": "NC", "lat": 36.0726, "lon": -79.7920, "population": 290711},
    {"name": "Irvine", "state": "CA", "lat": 33.6846, "lon": -117.8265, "population": 287401},
    {"name": "Boise", "state": "ID", "lat": 43.6150, "lon": -116.2023, "population": 228959},
    {"name": "Spokane", "state": "WA", "lat": 47.6587, "lon": -117.4260, "population": 222081},
    {"name": "Modesto", "state": "CA", "lat": 37.6688, "lon": -120.9967, "population": 219230},
    {"name": "Fontana", "state": "CA", "lat": 34.0922, "lon": -117.4350, "population": 208393},
    {"name": "Santa Clarita", "state": "CA", "lat": 34.3917, "lon": -118.6425, "population": 228673},
    {"name": "Moreno Valley", "state": "CA", "lat": 33.7534, "lon": -117.2297, "population": 208634},
    {"name": "Fayetteville", "state": "NC", "lat": 35.0527, "lon": -78.8784, "population": 210122},
    {"name": "Huntsville", "state": "AL", "lat": 34.7304, "lon": -86.5861, "population": 215006},
    {"name": "Brownsville", "state": "TX", "lat": 25.9017, "lon": -97.4975, "population": 182860},
]

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
        
        for city in US_CITIES:
            city_location = (city["lat"], city["lon"])
            distance = geodesic(user_location, city_location).miles
            distances.append((city["name"], city["state"], city["lat"], city["lon"], distance))
        
        distances.sort(key=lambda x: x[4])
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

def get_weather_emoji(code):
    """Get emoji for weather condition."""
    emoji_map = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌦️", 55: "🌦️",
        61: "🌧️", 63: "🌧️", 65: "⛈️", 71: "🌨️", 73: "🌨️", 75: "🌨️",
        77: "🌨️", 80: "🌧️", 81: "⛈️", 82: "⛈️", 85: "🌨️", 86: "🌨️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return emoji_map.get(code, "🌤️")

# 5. Display Weather Data
def display_weather(city_name, lat, lon, weather):
    """Display weather information in tabs."""
    emoji = get_weather_emoji(weather['weather_code'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"<div class='weather-card'><div class='temperature-display'>{emoji} {int(weather['temperature_2m'])}°F</div><p>{get_weather_description(weather['weather_code'])}</p></div>", unsafe_allow_html=True)
    
    with col2:
        st.metric("Humidity", f"{int(weather['relative_humidity_2m'])}%")
        st.metric("Wind Speed", f"{int(weather['wind_speed_10m'])} mph")
    
    st.divider()
    
    # Display radar
    st.subheader("Live Weather Radar")
    radar_url = f"https://embed.windy.com/embed.html?lat={lat}&lon={lon}&overlay=radar&menu=&type=map&location=coordinates"
    st.components.v1.html(
        f'<iframe src="{radar_url}" height="500" width="100%" frameborder="0"></iframe>',
        height=500,
        scrolling=False
    )

# Page functions
def home_page():
    """Homepage similar to Weather Channel."""
    st.markdown("""
    <div class='main-header'>
        <h1>🌤️ Weather Channel</h1>
        <p>Your local weather forecast and alerts</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📍 Get My Location", use_container_width=True, key="home_location"):
            st.session_state.page = 'location'
            st.rerun()
    
    with col2:
        if st.button("🔍 Search Cities", use_container_width=True, key="home_search"):
            st.session_state.page = 'search'
            st.rerun()
    
    with col3:
        if st.button("📍 Nearby Cities", use_container_width=True, key="home_nearby"):
            if st.session_state.lat is not None and st.session_state.lon is not None:
                st.session_state.page = 'nearby'
                st.rerun()
            else:
                st.warning("Please get your location first!")
    
    st.divider()
    
    # Featured cities
    st.subheader("Featured Cities")
    featured = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    
    cols = st.columns(5)
    for idx, city_name in enumerate(featured):
        with cols[idx]:
            city = next((c for c in US_CITIES if c['name'] == city_name), None)
            if city and st.button(f"📍 {city['name']}, {city['state']}", use_container_width=True, key=f"featured_{city_name}"):
                st.session_state.lat = city['lat']
                st.session_state.lon = city['lon']
                st.session_state.current_city = f"{city['name']}, {city['state']}"
                st.session_state.page = 'weather'
                st.rerun()

def location_page():
    """Get location page."""
    st.title("📍 Get Your Location")
    
    if st.button("← Back to Home", key="back_location"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Option 1: Auto-Detect")
        if st.button("📍 Get My Location"):
            location = streamlit_geolocation()
            is_valid, location_data = validate_location(location)
            
            if is_valid:
                lat, lon = location_data
                st.session_state.lat = lat
                st.session_state.lon = lon
                st.session_state.current_city = f"({lat:.2f}, {lon:.2f})"
                st.session_state.page = 'weather'
                st.rerun()
            else:
                st.warning("⚠️ " + str(location_data))
                st.info("Please enable location access in your browser.")
    
    with col2:
        st.subheader("Option 2: Manual Entry")
        lat = st.number_input("Latitude", value=40.7128, min_value=-90.0, max_value=90.0)
        lon = st.number_input("Longitude", value=-74.0060, min_value=-180.0, max_value=180.0)
        
        if st.button("🔍 Get Weather"):
            st.session_state.lat = lat
            st.session_state.lon = lon
            st.session_state.current_city = f"({lat:.2f}, {lon:.2f})"
            st.session_state.page = 'weather'
            st.rerun()

def search_page():
    """Search cities page."""
    st.title("🔍 Search All US Cities")
    
    if st.button("← Back to Home", key="back_search"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.divider()
    
    # Search box
    search_query = st.text_input("Search for a city:", placeholder="Type city name or state abbreviation...")
    
    # Filter cities
    if search_query:
        filtered_cities = [
            c for c in US_CITIES 
            if search_query.lower() in c['name'].lower() or search_query.lower() in c['state'].lower()
        ]
    else:
        filtered_cities = US_CITIES
    
    st.write(f"Found {len(filtered_cities)} cities")
    
    # Display filtered cities in a scrollable container
    for idx, city in enumerate(filtered_cities):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{city['name']}, {city['state']}** (Pop: {city['population']:,})")
        with col2:
            if st.button("📍 View", key=f"search_view_{idx}_{city['lat']}_{city['lon']}"):
                st.session_state.lat = city['lat']
                st.session_state.lon = city['lon']
                st.session_state.current_city = f"{city['name']}, {city['state']}"
                st.session_state.page = 'weather'
                st.rerun()

def nearby_page():
    """Nearby cities page."""
    st.title("📍 Nearby Cities")
    
    if st.button("← Back to Home", key="back_nearby"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.divider()
    
    if st.session_state.lat and st.session_state.lon:
        nearby = find_nearby_cities(st.session_state.lat, st.session_state.lon, max_results=20)
        
        if nearby:
            st.write(f"Cities near ({st.session_state.lat:.2f}, {st.session_state.lon:.2f})")
            
            for idx, (city_name, state, city_lat, city_lon, distance) in enumerate(nearby):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{city_name}, {state}** - {distance:.1f} miles away")
                with col2:
                    if st.button("📍 View", key=f"nearby_view_{idx}_{city_lat}_{city_lon}"):
                        st.session_state.lat = city_lat
                        st.session_state.lon = city_lon
                        st.session_state.current_city = f"{city_name}, {state}"
                        st.session_state.page = 'weather'
                        st.rerun()
        else:
            st.info("No nearby cities found.")
    else:
        st.warning("Please get your location first!")

def weather_page():
    """Weather display page."""
    st.title(f"🌤️ Weather for {st.session_state.current_city}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("← Back to Home", key="back_weather"):
            st.session_state.page = 'home'
            st.rerun()
    with col2:
        if st.button("🔄 Refresh", key="refresh_weather"):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    try:
        with st.spinner("Loading weather data..."):
            weather = get_weather(st.session_state.lat, st.session_state.lon)
        display_weather(st.session_state.current_city, st.session_state.lat, st.session_state.lon, weather)
    except Exception as e:
        st.error(f"❌ Error fetching weather data: {str(e)}")
        st.info("Please try again in a moment.")

# Navigation
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'location':
    location_page()
elif st.session_state.page == 'search':
    search_page()
elif st.session_state.page == 'nearby':
    nearby_page()
elif st.session_state.page == 'weather':
    weather_page()
