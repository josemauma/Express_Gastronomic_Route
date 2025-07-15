import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Load Google API key from .env
GOOGLE_API_KEY = os.getenv('API_GOOGLE_PLACES')

if not GOOGLE_API_KEY:
    raise ValueError("Error: Google API key is not set.")


def get_coordinates(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': GOOGLE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding error: {data['status']}")
            return None, None
    except requests.RequestException as e:
        print(f"Geocoding request error: {e}")
        return None, None


def search_restaurants(latitude, longitude, radius=5000, food_type=None):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'type': 'restaurant',
        'key': GOOGLE_API_KEY,
        'rankby': 'distance' if not food_type else None  # rankby=distance does not allow radius, but allows keyword
    }
    # If using rankby=distance, radius cannot be used, so remove it
    if params.get('rankby') == 'distance':
        params.pop('radius')
    if food_type:
        params['keyword'] = food_type
        # If food_type is set, Google requires radius, so remove rankby
        params.pop('rankby', None)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            # Manually sort by distance if rankby=distance was not used
            if not food_type:
                return data['results']
            else:
                # If food_type is set, sort by proximity using location
                def distance(item):
                    loc = item['geometry']['location']
                    return (loc['lat'] - latitude) ** 2 + (loc['lng'] - longitude) ** 2
                return sorted(data['results'], key=distance)
        else:
            print(f"Restaurant search error: {data['status']}")
            return []
    except requests.RequestException as e:
        print(f"Restaurant search request error: {e}")
        return []


def get_restaurant_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'key': GOOGLE_API_KEY,
        'language': 'en'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            # Return all available restaurant data
            return data['result']
        else:
            print(f"Error getting restaurant details: {data['status']}")
            return None
    except requests.RequestException as e:
        print(f"Restaurant details request error: {e}")
        return None

def get_all_restaurant_details(restaurants):
    desired_fields = [
        'name',
        'formatted_address',
        'types',
        'formatted_phone_number',
        'website',
        'opening_hours',
        'current_opening_hours',
        'rating',
        'user_ratings_total',
        'reviews',
        'photos',
        'price_level',
        'wheelchair_accessible_entrance',
        'delivery',
        'dine_in',
        'takeout',
        'reservable'
    ]
    details_list = []
    for restaurant in restaurants:
        place_id = restaurant.get('place_id')
        if place_id:
            details = get_restaurant_details(place_id)
            if details:
                filtered = {field: details.get(field) for field in desired_fields if field in details}
                details_list.append(filtered)
    return details_list

def save_details_to_json(details, filename):
    try:
        # Add current time to the filename before the extension
        base, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_time = f"{base}_{timestamp}{ext}"
        with open(filename_with_time, "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        print(f"\nDetails successfully saved")
    except Exception as e:
        print(f"Error saving file: {e}")
