import os
import googlemaps
from datetime import datetime
import urllib.parse
import folium
import webbrowser

class RouteOptimizer:
    def __init__(self, api_key, mode="walking"):
        self.gmaps = googlemaps.Client(key=api_key)
        self.mode = mode

    def geocode(self, address):
        results = self.gmaps.geocode(address)
        if not results:
            raise ValueError(f"Failed to geocode the address: {address}")
        loc = results[0]['geometry']['location']
        return loc['lat'], loc['lng']

    def optimize_route(self, start, restaurants):
        origin_coord = self.geocode(start)
        coords = [self.geocode(p['address']) for p in restaurants]
        waypoints = [f"{lat},{lng}" for lat, lng in coords]

        directions_result = self.gmaps.directions(
            origin=origin_coord,
            destination=origin_coord,
            mode=self.mode,
            waypoints=waypoints,
            optimize_waypoints=True,
            departure_time=datetime.now()
        )
        if not directions_result:
            raise RuntimeError("No route steps were returned")

        from googlemaps import convert
        overview = directions_result[0]['overview_polyline']['points']
        decoded = convert.decode_polyline(overview)
        route_coords = [(p['lat'], p['lng']) for p in decoded]
        return origin_coord, coords, route_coords

    def plot_route(self, origin_coord, coords, restaurants, route_coords, html_file="optimal_route.html"):
        m = folium.Map(location=origin_coord, zoom_start=14)
        folium.Marker(location=origin_coord, popup="🏁 Start", icon=folium.Icon(color="green")).add_to(m)
        for (lat, lng), p in zip(coords, restaurants):
            folium.Marker(location=(lat, lng), popup=p['name'], icon=folium.Icon(color="red")).add_to(m)
        folium.PolyLine(locations=route_coords, weight=6, opacity=0.7).add_to(m)
        m.save(html_file)
        print("Folium map saved at:", os.path.abspath(html_file))
        # Optional: open map
        webbrowser.open(f"file://{os.path.abspath(html_file)}", new=3)
        return html_file

    def get_google_maps_url(self, start, restaurants):
        stops = [start] + [p['address'] for p in restaurants] + [start]
        path = "/".join(urllib.parse.quote_plus(s) for s in stops)
        return f"https://www.google.com/maps/dir/{path}/?travelmode={self.mode}"

    def save_route_json(self, start, restaurants, route_coords, filename="route_data.json"):
        data = {
            "start": start,
            "restaurants": restaurants,
            "route_coords": route_coords
        }
        with open(filename, "w", encoding="utf-8") as f:
            import json
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Route data saved as {filename}")
