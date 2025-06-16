import os
import googlemaps
from datetime import datetime
import urllib.parse
import folium
import webbrowser

# 1) Authentication
API_KEY = os.getenv("API_GOOGLE_PLACES")
if not API_KEY:
    raise ValueError("Define API_GOOGLE_PLACES in your environment")
gmaps = googlemaps.Client(key=API_KEY)

# 2) Geocoding function
def geocode(address):
    results = gmaps.geocode(address)
    if not results:
        raise ValueError(f"Failed to geocode the address: {address}")
    loc = results[0]['geometry']['location']
    return loc['lat'], loc['lng']

# 3) Example data
start = "Calle Larios, Málaga"
restaurants = [
    {"name": "El Pimpi",  "address": "Calle Granada, 62, Málaga"},
    {"name": "La Tranca", "address": "Calle Carretería, 92, Málaga"},
]

# 4) Geocode origin and waypoints
origin_coord = geocode(start)
coords = [geocode(p['address']) for p in restaurants]
waypoints = [f"{lat},{lng}" for lat, lng in coords]

# 5) Call to Directions API
directions_result = gmaps.directions(
    origin=origin_coord,
    destination=origin_coord,
    mode="walking",               # or "driving", depending on your needs
    waypoints=waypoints,
    optimize_waypoints=True,
    departure_time=datetime.now()
)
if not directions_result:
    raise RuntimeError("No route steps were returned")

# 6) Decode polyline
from googlemaps import convert
overview = directions_result[0]['overview_polyline']['points']
decoded = convert.decode_polyline(overview)
route_coords = [(p['lat'], p['lng']) for p in decoded]

# 7) Generate map with Folium
m = folium.Map(location=origin_coord, zoom_start=14)
folium.Marker(location=origin_coord, popup="🏁 Start", icon=folium.Icon(color="green")).add_to(m)
for (lat, lng), p in zip(coords, restaurants):
    folium.Marker(location=(lat, lng), popup=p['name'], icon=folium.Icon(color="red")).add_to(m)
folium.PolyLine(locations=route_coords, weight=6, opacity=0.7).add_to(m)

# 8) Save and open local HTML (optional)
html_file = "optimal_route.html"
m.save(html_file)
full_path = os.path.abspath(html_file)
file_url = f"file://{full_path}"
print("Folium map saved at:", file_url)
webbrowser.open(file_url, new=3)

# 9) Build and open a "human-friendly" link for Google Maps
mode = "walking"  # or "driving", "bicycling", etc.

# Prepare the list of stops: origin → waypoints → origin
stops = [start] + [p['address'] for p in restaurants] + [start]

# Escape each stop but keep slashes to separate
path = "/".join(urllib.parse.quote_plus(s) for s in stops)

maps_url = f"https://www.google.com/maps/dir/{path}/?travelmode={mode}"

print("\nOpen this link to view the route in Google Maps in a readable format:")
print(urllib.parse.unquote(maps_url))  # display it decoded

# And launch it
webbrowser.open(maps_url, new=2)

