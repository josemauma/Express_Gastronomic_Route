# tests/services/test_restaurant_selection.py

import os
import json
import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace

import requests
from express_gastronomic_route.Services.restaurant_selection import RestaurantSelection

# --- Fixtures & helpers ---

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    """Ensure no API key in the environment and disable dotenv loading."""
    # Remove any existing API key
    monkeypatch.delenv("API_GOOGLE_PLACES", raising=False)
    # Stub out load_dotenv so it cannot repopulate the env
    import express_gastronomic_route.Services.restaurant_selection as rs
    monkeypatch.setattr(rs, "load_dotenv", lambda: None)

class DummyResponse:
    """Minimal stand‑in for requests.Response."""
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.HTTPError(f"{self.status_code} Error")

    def json(self):
        return self._data

# --- Initialization tests ---

def test_init_without_api_key_raises_value_error():
    """If no API key is provided or in .env, constructor should fail."""
    with pytest.raises(ValueError) as exc:
        RestaurantSelection(api_key=None)
    assert "Google API key not set" in str(exc.value)

def test_init_with_api_key_argument_succeeds(monkeypatch):
    """Providing api_key argument should bypass environment lookup."""
    selection = RestaurantSelection(api_key="TEST_KEY")
    assert selection.api_key == "TEST_KEY"

# --- get_coordinates ---

def test_get_coordinates_success(monkeypatch):
    """get_coordinates should return (lat, lng) on OK status."""
    dummy_data = {
        "status": "OK",
        "results": [
            {"geometry": {"location": {"lat": 12.34, "lng": 56.78}}}
        ]
    }
    monkeypatch.setenv("API_GOOGLE_PLACES", "ENV_KEY")
    monkeypatch.setattr(requests, "get",
                        lambda url, params: DummyResponse(200, dummy_data))

    sel = RestaurantSelection()
    lat, lng = sel.get_coordinates("Some Address")
    assert pytest.approx(lat) == 12.34
    assert pytest.approx(lng) == 56.78

def test_get_coordinates_non_ok_status(monkeypatch, capsys):
    """Non‑OK status should print an error and return (None, None)."""
    monkeypatch.setenv("API_GOOGLE_PLACES", "ENV_KEY")
    bad_data = {"status": "ZERO_RESULTS", "results": []}
    monkeypatch.setattr(requests, "get",
                        lambda url, params: DummyResponse(200, bad_data))

    sel = RestaurantSelection()
    lat, lng = sel.get_coordinates("Nowhere")
    captured = capsys.readouterr()
    assert "Geocoding error: ZERO_RESULTS" in captured.out
    assert (lat, lng) == (None, None)

# --- save_details_to_json ---

def test_save_details_to_json_creates_timestamped_file(tmp_path):
    """save_details_to_json should write a JSON with timestamped filename."""
    sel = RestaurantSelection(api_key="DUMMY")
    details = [{"name": "A"}, {"name": "B"}]
    base = str(tmp_path / "out")
    filename = f"{base}.json"

    out_name = sel.save_details_to_json(details, filename)
    # Filename should be base_YYYYMMDD_HHMMSS.json
    assert out_name.startswith(base + "_")
    assert out_name.endswith(".json")

    # File must exist and contain the dumped details
    data = json.loads((tmp_path / os.path.basename(out_name)).read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data == details

# --- fetch_and_save high‑level flow ---

def test_fetch_and_save_calls_all_steps(monkeypatch, tmp_path):
    """
    fetch_and_save should chain get_coordinates, search_restaurants,
    get_all_restaurant_details, and save_details_to_json.
    """
    dummy_coords = (1.1, 2.2)
    dummy_found = [{"place_id": "P1"}]
    dummy_details = [{"name": "X"}]
    saved_file = str(tmp_path / "saved.json")

    sel = RestaurantSelection(api_key="KEY")

    # Patch internal methods
    monkeypatch.setattr(sel, "get_coordinates", lambda addr: dummy_coords)
    monkeypatch.setattr(sel, "search_restaurants", lambda lat, lng, food_type=None: dummy_found)
    monkeypatch.setattr(sel, "get_all_restaurant_details", lambda lst: dummy_details)
    monkeypatch.setattr(sel, "save_details_to_json", lambda details, fn: saved_file)

    result_details, result_file = sel.fetch_and_save("Addr", food_type="pizza", out_file="ignored.json")
    assert result_details == dummy_details
    assert result_file == saved_file
