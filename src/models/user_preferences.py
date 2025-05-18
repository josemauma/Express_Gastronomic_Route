import streamlit as st
import json
from datetime import time
import os
from datetime import datetime

# Ruta a tu carpeta predefinida
DATABASE_DIR = "/Users/josemanuelmuelas/Desktop/Express_Gastronomic_Route/src/database/Users_preferences"
os.makedirs(DATABASE_DIR, exist_ok=True)

def show_preferences_form():
    st.set_page_config(page_title="Gastronomic Routes", page_icon="🍽️", layout="centered")

    st.title("🗺️ Gastronomic Routes App")

    # User preferences form
    with st.form("preferences_form"):
        # Food
        food_type = st.selectbox("Type of food", ["Spanish", "Italian", "Japanese", "Mexican", "Chinese", "Indian", "Vegetarian", "Vegan", "Other"])
        allergies = st.multiselect("Allergies/Intolerances", ["Gluten", "Lactose", "Spicy", "Nuts", "Seafood", "Eggs"])

        # Budget
        budget = st.selectbox("Budget (per person)", ["< 15€", "15€ - 30€", "> 30€"])

        # Location
        location = st.text_input("Current location or address")
        transport_mode = st.selectbox("Transport mode", ["Walking", "Car", "Bike", "Public transport"])
        distance = st.selectbox("Maximum distance", ["< 1 km", "1 km – 5 km", "> 5 km"])

        # Schedule
        available_time = st.selectbox("Available time", ["< 1h", "1h – 2h", "> 2h"])
        time_range_start = st.time_input("Time range - Start", time(12, 0))
        time_range_end = st.time_input("Time range - End", time(23, 0))

        # Outdoor
        avoid_terraces = st.checkbox("Avoid terraces (in case of bad weather)")

        # Experience type
        experience_type = st.selectbox("Type of experience", ["Fast and cheap", "Gourmet tasting", "Tapas route", "Romantic plan", "Family/kids"])

        # Reviews
        stars = st.selectbox("Stars", ["< 3", "3 – 4", "> 4"])
        reviews_count = st.selectbox("Number of reviews", ["< 100", "100 – 200", "200 – 300", "> 300"])

        # Number of restaurants/bars
        restaurants_count = st.selectbox("Number of restaurants/bars", ["2", "3", "4", "5"])

        # Brochure type
        brochure_type = st.selectbox("Brochure type", ["Fun", "Formal", "No description, only address"])

        # Username
        username = st.text_input("Your name (for saving preferences)")

        # Save button
        submitted = st.form_submit_button("Save preferences")

    # Save data to the predefined folder
    if submitted:
        if username.strip() == "":
            st.error("Please enter your name before saving preferences.")
        else:
            data = {
                "food_type": food_type,
                "allergies": allergies,
                "budget": budget,
                "location": location,
                "transport_mode": transport_mode,
                "distance": distance,
                "available_time": available_time,
                "time_range": {
                    "start": str(time_range_start),
                    "end": str(time_range_end)
                },
                "avoid_terraces": avoid_terraces,
                "experience_type": experience_type,
                "stars": stars,
                "reviews_count": reviews_count,
                "restaurants_count": restaurants_count,
                "brochure_type": brochure_type,
                "username": username.strip()
            }

            # Generate the filename with date
            filename = f"{username.strip()}_route_preferences_{datetime.now().strftime('%Y%m%d')}.json"
            json_file_path = os.path.join(DATABASE_DIR, filename)

            # Save the preferences
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            st.success(f"Preferences saved successfully in {json_file_path}!")


# Run the preferences form
if __name__ == "__main__":
    show_preferences_form()
