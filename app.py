
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
            
    except Exception
