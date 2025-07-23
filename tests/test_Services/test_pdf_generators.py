# tests/services/test_pdf_generators.py

import os
import pytest
from datetime import datetime
from fpdf import FPDF

from express_gastronomic_route.Services.pdf_generators import GastronomyPDF

# Automatically set PHOTO_DIR to a temporary folder containing a dummy image
@pytest.fixture(autouse=True)
def fake_photo_dir(tmp_path, monkeypatch):
    photo_folder = tmp_path / "photos"
    photo_folder.mkdir()
    # Create a placeholder JPEG so portada() can load it without error
    (photo_folder / "malagaPortada.jpg").write_bytes(b"FAKEJPEG")
    monkeypatch.setenv("PHOTO_DIR", str(photo_folder))
    return photo_folder

def test_safe_latin1_removes_unencodable_characters():
    """safe_latin1 should drop characters not mappable to Latin‑1."""
    original = "Café 😊"
    cleaned = GastronomyPDF.safe_latin1(original)
    assert "😊" not in cleaned
    assert "Café" in cleaned

def test_split_dossier_sections_with_and_without_headings():
    """split_dossier_sections should separate Description, Reviews, and Hours."""
    dossier_text = """
    # Description
    This is a test description.

    # Reviews
    Alice: Fantastic!
    Bob: Could be better.

    # Weekly opening hours
    - Mon 9–17
    - Tue 9–17
    """
    parts = GastronomyPDF.split_dossier_sections(dossier_text)
    assert parts["Description"] == "This is a test description."
    assert parts["Reviews"] == ["Alice: Fantastic!", "Bob: Could be better."]
    assert parts["Opening hours"] == ["- Mon 9–17", "- Tue 9–17"]

    # If there are no section headers, everything goes into Description
    plain = "Just some free‑form text"
    fallback = GastronomyPDF.split_dossier_sections(plain)
    assert fallback["Description"] == plain
    assert fallback["Reviews"] == []
    assert fallback["Opening hours"] == []

def test_generate_method_produces_pdf_file(tmp_path, monkeypatch):
    """
    generate() should invoke portada, add_restaurant, add_weather_summary,
    and finally call FPDF.output() with the expected filename.
    """
    # Minimal restaurant and weather data
    restaurants = [{
        "name": "Testaurant",
        "address": "123 Fake Street",
        # all other fields omitted on purpose
    }]
    forecast = [{
        "date": "2025-07-23",
        "temperature_avg": 25,
        "wind_speed": 5,
        "rain_probability": 10
    }]
    best_day = {
        "best_date": "2025-07-24",
        "best_temperature_avg": 26,
        "best_wind_speed": 4,
        "best_rain_probability": 5
    }

    # Monkey‑patch FPDF.output to capture the filename instead of writing a real PDF
    captured = {}
    def fake_output(self, filename):
        captured["filename"] = filename
        # Write minimal PDF header so file exists
        with open(filename, "wb") as f:
            f.write(b"%PDF-TEST")
    monkeypatch.setattr(FPDF, "output", fake_output)

    # Instantiate with a known output path
    output_file = tmp_path / "route_test.pdf"
    pdf = GastronomyPDF(filename=str(output_file), title="Test Title")

    # Run the full PDF generation flow
    pdf.generate(
        restaurants,
        forecast=forecast,
        best_day=best_day,
        city="TestCity",
        maps_url="http://example.com/route"
    )

    # Ensure output() was called with our path
    assert captured.get("filename") == str(output_file)
    # Ensure the file was actually created
    assert output_file.exists()
    # Check that the file starts with the PDF signature
    with open(output_file, "rb") as f:
        assert f.read().startswith(b"%PDF")
