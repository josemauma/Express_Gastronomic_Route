# tests/services/test_top_restaurants_info_top.py

import math
import pytest
from express_gastronomic_route.Services.RestaurantInfoTop import TopRestaurantsExtractor

# --- compute_score tests ---

def test_compute_score_with_valid_inputs():
    """compute_score should be rating * log10(num_reviews + 1)."""
    r = 4.5
    n = 99
    expected = r * math.log10(n + 1)
    assert TopRestaurantsExtractor.compute_score(r, n) == pytest.approx(expected)

def test_compute_score_with_none_inputs():
    """compute_score should return -1 if rating or num_reviews is None."""
    assert TopRestaurantsExtractor.compute_score(None, 10) == -1
    assert TopRestaurantsExtractor.compute_score(5.0, None) == -1
    assert TopRestaurantsExtractor.compute_score(None, None) == -1

# --- format_opening_hours tests ---

@pytest.mark.parametrize("raw,expected", [
    (
        "Mon: 09:00AM–05:00PM",
        ["- Mon: 09:00 AM - 05:00 PM"]
    ),
    (
        "Tue: 10:30AM\u2013\u202F06:45PM",  # mixed unicode dashes & thin spaces
        ["- Tue: 10:30 AM - 06:45 PM"]
    ),
    (
        "Wed: 08:00PM\u201410:00PM",       # em dash
        ["- Wed: 08:00 PM - 10:00 PM"]
    ),
    (
        "Thu: 07:15AM-11:30AM",            # ASCII dash, missing space
        ["- Thu: 07:15 AM - 11:30 AM"]
    ),
    (
        "Fri: closed",                    # unrecognized format
        ["- Fri: closed"]
    )
])
def test_format_opening_hours_various_formats(raw, expected):
    """
    format_opening_hours should:
      - Normalize unicode dashes and spaces
      - Insert spaces before AM/PM
      - Fallback to preserving text if pattern doesn’t match
    """
    out = TopRestaurantsExtractor([]).format_opening_hours([raw])
    assert out == expected

# --- get_top_3 tests ---

def make_rest(name, rating, reviews, time_stamps=None):
    """Helper to build a restaurant dict with given rating and review count."""
    if time_stamps is None:
        time_stamps = [100, 200, 50]
    reviews_list = [
        {"author_name": f"User{i}", "rating": 5 - i, "text": f"Comment{i}", "time": t}
        for i, t in enumerate(time_stamps)
    ]
    return {
        "name": name,
        "formatted_address": f"{name} Addr",
        "formatted_phone_number": "N/A",
        "website": None,
        "opening_hours": {"weekday_text": ["Sat: 12:00PM–03:00PM"]},
        "rating": rating,
        "user_ratings_total": reviews,
        "reviews": reviews_list,
        "price_level": 2,
        "wheelchair_accessible_entrance": True,
        "delivery": False,
        "takeout": True,
        "reservable": False,
    }

def test_get_top_3_empty_list():
    """get_top_3 on no restaurants should return empty list."""
    extractor = TopRestaurantsExtractor([])
    assert extractor.get_top_3() == []

def test_get_top_3_filters_and_sorts_correctly():
    """
    get_top_3 should:
      - Compute scores for each restaurant
      - Normalize scores to 0–10
      - Sort descending
      - Return only top N entries with minimal fields
    """
    a = make_rest("A", rating=5.0, reviews=100)
    b = make_rest("B", rating=4.0, reviews=400)
    c = make_rest("C", rating=3.0, reviews=900)
    d = make_rest("D", rating=None, reviews=10)   # invalid, should be dropped
    extractor = TopRestaurantsExtractor([a, b, c, d])

    top2 = extractor.get_top_3(n=2)
    # Should return 2 entries
    assert len(top2) == 2
    # Based on compute_score: B (4*log10(401)) > A > C
    names = [r["name"] for r in top2]
    assert names[0] == "B"
    assert names[1] == "A"
    
    # Check minimal fields presence and types
    entry = top2[0]
    assert set(entry.keys()) >= {
        "name", "address", "phone_number", "wheelchair_accessible_entrance",
        "takeout", "price_level", "website", "delivery", "reservable",
        "score", "opening_hours", "reviews"
    }
    # Score is rounded to two decimals
    assert isinstance(entry["score"], float)
    # opening_hours list was formatted
    assert entry["opening_hours"][0].startswith("- Sat:")
    # reviews limited to 2 entries, sorted by time descending
    assert len(entry["reviews"]) == 2
    times = [rev["time"] for rev in entry["reviews"]]
    assert times == sorted(times, reverse=True)
