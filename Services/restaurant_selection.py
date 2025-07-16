import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

class RestaurantSelection:
    def __init__(self, api_key=None):
        # Load API key from .env if not provided
        if not api_key:
            load_dotenv()
            api_key = os.getenv('API_GOOGLE_PLACES')
        if not api_key:
            raise ValueError("Google API key not set.")
        self.api_key = api_key

    def get_coordinates(self, address):
        """Geocode an address to get latitude and longitude."""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {'address': address, 'key': self.api_key}
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data['status'] == 'OK':
                loc = data['results'][0]['geometry']['location']
                return loc['lat'], loc['lng']
            print(f"Geocoding error: {data['status']}")
            return None, None
        except Exception as e:
            print(f"Geocoding request error: {e}")
            return None, None

    def search_restaurants(self, latitude, longitude, radius=5000, food_type=None, max_results=25):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{latitude},{longitude}",
            'type': 'restaurant',
            'key': self.api_key,
            'language': 'en'
        }
        if food_type:
            # If food_type is specified, use 'keyword' and 'radius' (Google requires radius)
            params['keyword'] = food_type
            params['radius'] = radius
        else:
            # If food_type is not specified, use rankby=distance (no radius allowed)
            params['rankby'] = 'distance'
        # Remove invalid parameter combinations
        if params.get('rankby') == 'distance' and 'radius' in params:
            del params['radius']

        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data['status'] == 'OK':
                results = data['results'][:max_results]
                # If filtering by food_type, sort results by proximity
                if food_type:
                    def dist(item):
                        loc = item['geometry']['location']
                        return (loc['lat'] - latitude)**2 + (loc['lng'] - longitude)**2
                    results = sorted(results, key=dist)
                return results
            print(f"Restaurant search error: {data['status']}")
            return []
        except Exception as e:
            print(f"Restaurant search request error: {e}")
            return []

    def get_restaurant_details(self, place_id):
        """Get all details about a restaurant using its place_id."""
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {'place_id': place_id, 'key': self.api_key, 'language': 'en'}
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data['status'] == 'OK':
                return data['result']
            print(f"Details error: {data['status']}")
            return None
        except Exception as e:
            print(f"Details request error: {e}")
            return None

    def get_all_restaurant_details(self, restaurants):
        """
        For a list of search results, fetch detailed info for each.
        Only the desired fields are retained in the output.
        """
        desired_fields = [
            'name', 'formatted_address', 'formatted_phone_number', 'website',
            'opening_hours', 'current_opening_hours', 'rating', 'user_ratings_total',
            'reviews', 'price_level', 'wheelchair_accessible_entrance', 'delivery',
            'dine_in', 'takeout', 'reservable'
        ]
        details_list = []
        for rest in restaurants:
            place_id = rest.get('place_id')
            if place_id:
                details = self.get_restaurant_details(place_id)
                if details:
                    filtered = {field: details.get(field) for field in desired_fields if field in details}
                    details_list.append(filtered)
        return details_list

    def save_details_to_json(self, details, filename):
        """
        Save restaurant details to a timestamped JSON file.
        Returns the output filename.
        """
        try:
            base, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_with_time = f"{base}_{timestamp}{ext}"
            with open(filename_with_time, "w", encoding="utf-8") as f:
                json.dump(details, f, ensure_ascii=False, indent=2)
            print(f"\nDetails successfully saved to {filename_with_time}")
            return filename_with_time
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

    def fetch_and_save(self, address, food_type=None, out_file="restaurants.json"):
        """
        High-level method: geocode address, search for restaurants,
        get details, and save to file in one go.
        """
        lat, lng = self.get_coordinates(address)
        if lat is None or lng is None:
            raise Exception("Could not geocode the address.")
        found = self.search_restaurants(lat, lng, food_type=food_type)
        detailed = self.get_all_restaurant_details(found)
        saved_file = self.save_details_to_json(detailed, out_file)
        return detailed, saved_file
