import streamlit as st
import sys
import os
import json
import re
from utils import pretty_forecast_lines, pretty_best_day, convert_dateinput_to_str
from express_gastronomic_route.Services import LLMAPI, TopRestaurantsExtractor, SYSTEM_PROFILE, WeatherAPI, RestaurantSelection, RouteOptimizer, GastronomyPDF

from dotenv import load_dotenv

load_dotenv()

api_key_gmaps = os.getenv("API_GOOGLE_PLACES")
api_key_weather = os.getenv("API_WEATHER_KEY")
pdf_dir = os.getenv("PDF_OUTPUT_DIR", ".")
user_prefs_dir = os.getenv("USER_PREFS_DIR", ".")
photo_dir = os.getenv("PHOTO_DIR")

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown("""
        <div style="text-align: center;">
            <h1>Express Gastronomic Route</h1>
            <h3>Master's Thesis</h3>
            <p><b>Author:</b> José Manuel Muelas de la Linde</p>
            <p><b>Master in Artificial Intelligence, Big Data and Data Engineering</b></p>
        </div>
    """, unsafe_allow_html=True)
    st.image(os.path.join(photo_dir, "malagaPortada.jpg"), width=700)


    col1, col2, col3 = st.columns([1.3, 2, 1])
    with col2:
        if st.button("Start the gastronomic experience 🍽️"):
            st.session_state.started = True
    st.stop()  

st.sidebar.title("Route Parameters")
address = st.sidebar.text_input("Address", value="Calle Larios")
city = st.sidebar.text_input("City/Town", value="Málaga")
start_date = st.sidebar.date_input("Start date", format="DD/MM/YYYY")
end_date = st.sidebar.date_input("End date", format="DD/MM/YYYY")
food_type = st.sidebar.text_input("Food type (optional)", value="")


if st.sidebar.button("Search Restaurants and Plan Route"):
    st.info("Cooking up your gastronomic route... 🍽️")

    # 1. Restaurant Search
    restaurant_selector = RestaurantSelection()
    restaurant_list, restaurants_json_file = restaurant_selector.fetch_and_save(
        address=address,
        food_type=food_type or None,
        #out_file="/Users/josemanuelmuelas/Desktop/Express_Gastronomic_Route/Database/Users_preferences/restaurant_details.json"
        out_file = os.path.join(user_prefs_dir, "restaurant_details.json")
    )
    st.success(f"✅ {len(restaurant_list)} restaurants found.")

    # 2. Load restaurants from JSON
    with open(restaurants_json_file, "r", encoding="utf-8") as f:
        lista = json.load(f)

    # 3. Top 3 selection
    extractor = TopRestaurantsExtractor(lista)
    top3_restaurant = extractor.get_top_3(n=3)

    # 4. LLM summaries 
    llm = LLMAPI()
    descriptions = []
    for rest in top3_restaurant:
        rest['best_day'] = None  
        user_message = {
            "role": "user",
            "content": json.dumps(rest, ensure_ascii=False, indent=2)
        }
        messages = [SYSTEM_PROFILE, user_message]
        data = {
            "model": "microsoft/phi-4-mini-instruct",
            "messages": messages,
            "temperature": 0.2
        }
        response = llm.post_chat_completion(data)
        try:
            salida = response["choices"][0]["message"]["content"]
        except Exception:
            salida = str(response)
        match = re.search(
            r"Description:\s*[\(\[]*(.*?)[\)\]]*\s*(?:\n+Reviews:|\n+Weekly opening hours:|\Z)",
            salida,
            re.IGNORECASE | re.DOTALL
        )
        descripcion = match.group(1).strip() if match else salida.strip()
        rest["llm_description"] = descripcion
        descriptions.append(descripcion)

    # 5. Show restaurants and nice descriptions
    st.markdown(
        f"<h2 style='text-align:center; font-size:2.5em;'>{'Gastronomic Route: ' + city}</h2>",
        unsafe_allow_html=True
    )
    for i, r in enumerate(top3_restaurant):
        st.markdown(f"<span style='font-size:1.5em'><b>{r['name']}</b></span> — {r['address']}", unsafe_allow_html=True)
        st.markdown(f"> {descriptions[i]}")
        # Phone number
        phone = r.get('phone_number', 'Not available')
        st.write(f"Phone number: {phone}")
        # Takeout
        takeout = r.get('takeout', None)
        takeout_str = "Yes" if takeout is True else ("No" if takeout is False else "Not available")
        st.write(f"Takeout: {takeout_str}")
        # Delivery
        delivery = r.get('delivery', None)
        delivery_str = "Yes" if delivery is True else ("No" if delivery is False else "Not available")
        st.write(f"Delivery: {delivery_str}")
        # Reservable
        reservable = r.get('reservable', None)
        reservable_str = "Yes" if reservable is True else ("No" if reservable is False else "Not available")
        st.write(f"Reservable: {reservable_str}")
        # Wheelchair Accessible
        wheelchair = r.get('wheelchair_accessible', None)
        wheelchair_str = "Yes" if wheelchair is True else ("No" if wheelchair is False else "Not available")
        st.write(f"Wheelchair Accessible: {wheelchair_str}")
        website = r.get('website', None)
        if website:
            st.markdown(f"[Website]({website})")
        else:
            st.write("Website: Not available")
        # Price Level
        price_level = r.get('price_level', None)
        if price_level is not None:
            st.write(f"Price Level: {price_level}")
        else:
            st.write("Price Level: Not available")

        opening_hours = r.get('opening_hours', [])
        if opening_hours:
            st.write("Opening hours:")
            for line in opening_hours:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{line}")
        else:
            st.write("Opening hours: Not available")
        st.markdown(f"<span style='font-size:1.5em'><b>Score: {r.get('score')}</b></span>", unsafe_allow_html=True)
        st.markdown("---")

    # 6. Route Optimization
    route_optimizer = RouteOptimizer(api_key=api_key_gmaps, mode="walking")
    origin_coord, coords, route_coords = route_optimizer.optimize_route(
        start=address,
        restaurants=top3_restaurant
    )
    maps_url = route_optimizer.get_google_maps_url(address, top3_restaurant)
    st.subheader("Optimized Route")
    st.markdown(f"[View route in Google Maps]({maps_url})")

    # 7. Weather info 
    weather = WeatherAPI(api_key_weather)
    start_str = convert_dateinput_to_str(start_date)
    end_str = convert_dateinput_to_str(end_date)
    weather_info = weather.get_weather_info(city)
    forecast = weather.get_weather_forecast(city)
    temperature_range = weather.filter_temp_range(forecast, start_str, end_str)
    best_day = weather.get_best_day_to_go_out(forecast, start_str, end_str)

    st.markdown(f"## Weather summary: {city}")
    st.markdown(f"### Forecast for selected dates:")
    for line in pretty_forecast_lines(temperature_range):
        st.markdown(f"- {line}")
    st.markdown(f"### Best day to eat:")
    st.markdown(pretty_best_day(best_day))

    pdf_filename = os.path.join(pdf_dir, f"gastronomic_route_{city.replace(' ', '_')}.pdf")
    pdfgen = GastronomyPDF(
        filename=pdf_filename,
        title=f"Gastronomic Route: {city}",
    )
    pdfgen.generate(
        top3_restaurant,
        forecast=temperature_range,
        best_day=best_day,
        city=city,
        maps_url=maps_url
    )

    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        label="Download gastronomic route as PDF",
        data=pdf_bytes,
        file_name=os.path.basename(pdf_filename),
        mime="application/pdf"
    )

    st.success("Your gastronomic route is ready! 🍽️")

else:
    st.info("Adjust parameters and click the button to generate your route.")