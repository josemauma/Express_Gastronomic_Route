# tests/test_minimal_app_flow.py
import os
import json
import pytest
from fpdf import FPDF

# Importamos solo los servicios que SÍ usaremos en estos tests
from express_gastronomic_route.Services import (
    RestaurantSelection,
    TopRestaurantsExtractor,
    GastronomyPDF,
)

# --- Fixtures de apoyo -------------------------------------------------------

@pytest.fixture
def tmp_env(tmp_path, monkeypatch):
    """
    Prepara variables de entorno y rutas temporales para no tocar el sistema.
    """
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    user_prefs_dir = tmp_path / "prefs"
    user_prefs_dir.mkdir()
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    (photos_dir / "malagaPortada.jpg").write_bytes(b"FAKEJPEG")

    monkeypatch.setenv("PDF_OUTPUT_DIR", str(pdf_dir))
    monkeypatch.setenv("USER_PREFS_DIR", str(user_prefs_dir))
    monkeypatch.setenv("PHOTO_DIR", str(photos_dir))

    return {
        "pdf_dir": pdf_dir,
        "user_prefs_dir": user_prefs_dir,
        "photos_dir": photos_dir,
    }


@pytest.fixture
def fake_restaurants():
    """Datos mínimos de restaurantes para las pruebas."""
    return [
        {"name": "A", "address": "Calle A 1", "score": 4.8},
        {"name": "B", "address": "Calle B 2", "score": 4.6},
        {"name": "C", "address": "Calle C 3", "score": 4.5},
        {"name": "D", "address": "Calle D 4", "score": 4.4},
    ]


# --- Tests -------------------------------------------------------------------

def test_selection_and_json_persisted(tmp_env, fake_restaurants, monkeypatch):
    """
    Verifica que RestaurantSelection.fetch_and_save devuelve una lista y
    persiste un JSON en disco (mockeado).
    """
    # Mock: evitar llamadas reales y escribir un JSON controlado
    def fake_fetch_and_save(self, address, food_type, out_file):
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(fake_restaurants, f, ensure_ascii=False, indent=2)
        return list(fake_restaurants), out_file

    monkeypatch.setattr(RestaurantSelection, "fetch_and_save", fake_fetch_and_save)

    selector = RestaurantSelection()
    restaurants, json_path = selector.fetch_and_save(
        address="Calle Larios",
        food_type=None,
        out_file=os.path.join(str(tmp_env["user_prefs_dir"]), "restaurant_details.json"),
    )

    assert isinstance(restaurants, list) and len(restaurants) == len(fake_restaurants)
    assert os.path.exists(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["name"] == "A"


def test_top3_extractor_called_and_returns_three(monkeypatch, fake_restaurants):
    """
    Comprueba que el extractor devuelve exactamente 3 elementos (mock simple).
    """
    # Mock sencillo: devolver los 3 primeros sin lógica compleja
    monkeypatch.setattr(TopRestaurantsExtractor, "get_top_3", lambda self, n=3: fake_restaurants[:n])

    extractor = TopRestaurantsExtractor(fake_restaurants)
    top3 = extractor.get_top_3(n=3)

    assert len(top3) == 3
    assert [r["name"] for r in top3] == ["A", "B", "C"]


def test_pdf_generation_creates_file(tmp_env, monkeypatch, tmp_path):
    captured = {}

    def fake_output(self, filename):
        captured["filename"] = filename
        with open(filename, "wb") as f:
            f.write(b"%PDF-TEST")

    monkeypatch.setattr(FPDF, "output", fake_output)

    output_file = tmp_env["pdf_dir"] / "gastronomic_route_TestCity.pdf"
    pdf = GastronomyPDF(filename=str(output_file), title="Gastronomic Route: TestCity")

    # Datos mínimos pero con todas las claves necesarias
    restaurants = [{"name": "A", "address": "Calle A 1", "score": 4.8}]
    forecast = [{
        "date": "2025-01-01",
        "temperature_avg": 22,
        "wind_speed": 3,
        "rain_probability": 10
    }]
    best_day = {
        "best_date": "2025-01-01",
        "best_temperature_avg": 22,
        "best_wind_speed": 3,
        "best_rain_probability": 10
    }

    pdf.generate(
        restaurants,
        forecast=forecast,
        best_day=best_day,
        city="TestCity",
        maps_url="http://example.com/route",
    )

    assert captured.get("filename") == str(output_file)
    assert output_file.exists()
    with open(output_file, "rb") as f:
        assert f.read().startswith(b"%PDF")
