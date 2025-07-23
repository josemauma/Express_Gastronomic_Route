# tests/services/test_route_optimizer.py

import os
import json
from types import SimpleNamespace
import pytest
from datetime import datetime, timedelta

import googlemaps
from express_gastronomic_route.Services.route_optimizer import RouteOptimizer

# --- Fixtures & helpers ---

class DummyDirectionsResult:
    """Stand‑in for googlemaps directions() return value."""
    def __init__(self, overview_polyline):
        self.overview_polyline = {"points": overview_polyline}

def dummy_decode_polyline(points):
    """Decode a fake polyline string into lat/lng tuples."""
    # Return two points for simplicity
    return [{"lat": 1.1, "lng": 2.2}, {"lat": 3.3, "lng": 4.4}]

@pytest.fixture(autouse=True)
def patch_googlemaps(monkeypatch):
    """Monkey‑patch googlemaps.Client so no real HTTP calls occur."""
    class FakeClient:
        def __init__(self, key):
            self.key = key

        def geocode(self, address):
            # Return a fake geometry
            return [{"geometry": {"location": {"lat": 10.0, "lng": 20.0}}}]

        def directions(self, origin, destination, mode, waypoints,
                       optimize_waypoints, departure_time):
            # Return one dummy route with an 'overview_polyline'
            return [{"overview_polyline": {"points": "FAKEPOLY"}}]

    monkeypatch.setattr(googlemaps, "Client", lambda key: FakeClient(key))
    # Patch the convert.decode_polyline function
    monkeypatch.setattr("express_gastronomic_route.Services.route_optimizer.googlemaps.convert.decode_polyline",
                        dummy_decode_polyline)

# --- geocode tests ---

def test_geocode_success():
    """geocode() should return (lat, lng) tuple from client.geocode result."""
    optimizer = RouteOptimizer(api_key="KEY")
    lat, lng = optimizer.geocode("123 Main St")
    assert (lat, lng) == (10.0, 20.0)

def test_geocode_failure(monkeypatch):
    """geocode() should raise ValueError if no results returned."""
    # Patch to return empty list
    class EmptyClient:
        def __init__(self, key): pass
        def geocode(self, address): return []
    monkeypatch.setattr(googlemaps, "Client", lambda key: EmptyClient(key))
    optimizer = RouteOptimizer(api_key="KEY")
    with pytest.raises(ValueError) as exc:
        optimizer.geocode("Nowhere")
    assert "Failed to geocode" in str(exc.value)

# --- optimize_route tests ---

def test_optimize_route_returns_expected_coords(monkeypatch):
    """optimize_route() should return origin, waypoint coords, and decoded route coords."""
    # Freeze datetime for departure_time
    fixed = datetime(2025, 1, 1, 12, 0, 0)
    monkeypatch.setattr("express_gastronomic_route.Services.route_optimizer.datetime", 
                        SimpleNamespace(now=lambda: fixed))
    optimizer = RouteOptimizer(api_key="KEY", mode="driving")
    restaurants = [{"address": "A"}, {"address": "B"}]

    origin, waypoints, route = optimizer.optimize_route("Start", restaurants)
    # origin and each waypoint come from DummyClient.geocode
    assert origin == (10.0, 20.0)
    assert waypoints == [(10.0, 20.0), (10.0, 20.0)]
    # route_coords built from dummy_decode_polyline
    assert route == [(1.1, 2.2), (3.3, 4.4)]

# --- plot_route tests ---

def test_plot_route_returns_html_path(tmp_path):
    """plot_route() should return the html filename without saving or opening."""
    optimizer = RouteOptimizer(api_key="KEY")
    origin = (0.0, 0.0)
    coords = [(1.0, 1.0), (2.0, 2.0)]
    restaurants = [{"name": "X"}, {"name": "Y"}]
    route_coords = [(0.1, 0.2), (0.3, 0.4)]
    out = optimizer.plot_route(origin, coords, restaurants, route_coords, html_file="test.html")
    assert out == "test.html"

# --- get_google_maps_url tests ---

def test_get_google_maps_url_encodes_addresses():
    """get_google_maps_url() should build a correct Google Maps directions URL."""
    optimizer = RouteOptimizer(api_key="KEY", mode="walking")
    start = "Home"
    restaurants = [{"address": "A & B"}, {"address": "C/D"}]
    url = optimizer.get_google_maps_url(start, restaurants)
    # Ensure travelmode and encoded path parts are present
    assert "travelmode=walking" in url
    assert "Home" in url  # unquoted
    assert "%26" in url  # & encoded
    assert "%2F" in url  # / encoded

# --- save_route_json tests ---

def test_save_route_json_creates_file(tmp_path, capsys):
    """save_route_json() should write JSON file with the provided data."""
    optimizer = RouteOptimizer(api_key="KEY")
    start = "S"
    restaurants = [{"name": "X"}]
    route_coords = [(1, 2), (3, 4)]
    filename = str(tmp_path / "out.json")

    optimizer.save_route_json(start, restaurants, route_coords, filename=filename)
    captured = capsys.readouterr()
    # File exists
    assert os.path.exists(filename)
    # Content matches structure
    data = json.loads(open(filename, encoding="utf-8").read())
    assert data["start"] == start
    assert data["restaurants"] == restaurants
    # JSON serializes tuples as lists
    assert data["route_coords"] == [[1, 2], [3, 4]]
        # Print message confirms save
    assert "Route data saved as" in captured.out
