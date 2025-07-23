from fpdf import FPDF
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

photo_dir = os.getenv("PHOTO_DIR")


class GastronomyPDF:
    def __init__(self, filename=None, title="Ruta Gastronómica"):
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ruta_gastronomica_{ts}.pdf"
        self.filename = filename
        self.title = title
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(True, margin=18)

    @staticmethod
    def safe_latin1(text):
        return text.encode('latin-1', 'ignore').decode('latin-1')

    @staticmethod
    def split_dossier_sections(dossier):
        sections = {"Description": "", "Reviews": [], "Opening hours": []}
        current = None
        for line in dossier.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # NUEVO: Si es línea de cabecera (empieza con "#"), actúa en consecuencia
            if stripped.startswith("#"):
                header = stripped.lstrip("#").strip().lower()
                if "description" == header:
                    current = "Description"
                    continue
                if "reviews" == header:
                    current = "Reviews"
                    continue
                if header in ("opening hours", "weekly opening hours"):
                    current = "Opening hours"
                    continue
                # Si es un "#" que no reconoces, baja a siguiente
                continue

            # Sólo aquí procesas el contenido
            if current == "Description":
                sections["Description"] += stripped + " "
            elif current in ("Reviews", "Opening hours"):
                sections[current].append(stripped)

        # Trim or fallback
        if not any([sections["Description"], sections["Reviews"], sections["Opening hours"]]):
            sections["Description"] = dossier.strip()
        else:
            sections["Description"] = sections["Description"].strip()

        return sections


    def portada(self, maps_url=None):
        self.pdf.add_page()
        self.pdf.ln(15)
        self.pdf.set_font("Arial", 'B', 26)
        self.pdf.set_text_color(0, 90, 158)
        self.pdf.cell(0, 20, self.safe_latin1(self.title), ln=True, align='C')
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("Arial", '', 14)
        self.pdf.ln(10)
        self.pdf.ln(20)
        self.pdf.image(os.path.join(photo_dir, "malagaPortada.jpg"), x=30, w=150)
        self.pdf.ln(20)
        if maps_url:
            self.pdf.set_font("Arial", 'B', 14)
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.cell(0, 10, "Optimized Walking Route", ln=True, align='C')
            self.pdf.set_font("Arial", 'U', 12)
            self.pdf.set_text_color(0, 0, 255)
            self.pdf.cell(0, 10, "Link to the route", ln=True, align='C', link=maps_url)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.ln(15)
        self.pdf.set_font("Arial", '', 14)
        self.pdf.cell(0, 10, f"Generation Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
            
    def add_restaurant(self, restaurant, idx):
        self.pdf.add_page()
        # Header color bar
        self.pdf.set_fill_color(0, 90, 158)
        self.pdf.rect(0, 0, 210, 20, style='F')
        self.pdf.set_y(7)
        self.pdf.set_font("Arial", 'B', 18)
        self.pdf.set_text_color(255,255,255)
        self.pdf.cell(0, 10, self.safe_latin1(f"{idx}. {restaurant['name']}"), ln=True, align='C')
        self.pdf.set_text_color(0,0,0)

        # Two blank lines before address
        self.pdf.ln(14)
        self.pdf.set_font("Arial", '', 12)
        self.pdf.multi_cell(0, 7, self.safe_latin1(f"Address: {restaurant.get('address', 'Not available')}"))
        phone = restaurant.get('phone_number', 'Not Available')
        self.pdf.multi_cell(0, 7, self.safe_latin1(f"Phone Number: {phone}"))
        takeout = restaurant.get('takeout')
        if takeout is not None:
            takeout_str = "Yes" if takeout else "No"
            self.pdf.multi_cell(0, 7, self.safe_latin1(f"Takeout: {takeout_str}"))
        delivery = restaurant.get('delivery')
        if delivery is not None:
            delivery_str = "Yes" if delivery else "No"
            self.pdf.multi_cell(0, 7, self.safe_latin1(f"Delivery: {delivery_str}"))
        reservable = restaurant.get('reservable')
        if reservable is not None:
            reservable_str = "Yes" if reservable else "No"
            self.pdf.multi_cell(0, 7, self.safe_latin1(f"Reservable: {reservable_str}"))
        wheelchair_accessible = restaurant.get('wheelchair_accessible_entrance')
        if wheelchair_accessible is not None:
            wheelchair_str = "Yes" if wheelchair_accessible else "No"
            self.pdf.multi_cell(0, 7, self.safe_latin1(f"Wheelchair Accessible: {wheelchair_str}"))
        price_level = restaurant.get('price_level', -1)
        if price_level == 1:
            price_str = "Inexpensive"
        elif price_level == 2:
            price_str = "Moderate"
        elif price_level == 3:
            price_str = "Expensive"
        elif price_level == 4:
            price_str = "Very Expensive"
        else:
            price_str = "No Info"
        if price_str:
            self.pdf.multi_cell(0, 7, self.safe_latin1(f"Price Level: {price_str}"))
        website = restaurant.get('website')
        if website:
            self.pdf.set_font("Arial", '', 12)
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.cell(self.pdf.get_string_width("Website: "), 7, "Website: ", ln=0)
            self.pdf.set_font("Arial", 'U', 12)
            self.pdf.cell(0, 7, self.safe_latin1(f"{website}"), ln=True, link=website)
            self.pdf.set_font("Arial", '', 12)
            self.pdf.set_text_color(0, 0, 0)
        if restaurant.get("score") is not None:
            self.pdf.set_font("Arial", 'B', 12)
            self.pdf.set_text_color(0, 150, 0)
            self.pdf.cell(0, 8, f"Score: {restaurant['score']}/10", ln=True)
            self.pdf.set_text_color(0,0,0)
        self.pdf.ln(1)

        # Section: Description (only LLM output, not reviews)
        self.pdf.ln(7)
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.cell(0, 8, "Description:", ln=True)
        self.pdf.set_font("Arial", '', 12)
        llm_desc = restaurant.get("llm_description") or "No description available."
        self.pdf.multi_cell(0, 7, self.safe_latin1(llm_desc))
        self.pdf.ln(2)

        # Section: Reviews
        self.pdf.ln(6)
        reviews = restaurant.get("reviews", [])
        if reviews:
            self.pdf.set_font("Arial", 'B', 13)
            self.pdf.cell(0, 7, "Reviews:", ln=True)
            self.pdf.set_font("Arial", '', 12)
            for rev in reviews:
                name = rev.get("author_name", "Anonymous")
                rating = rev.get("rating", "")
                text = rev.get("text", "")
                self.pdf.cell(0, 8, f"- {name} ({rating}/5)", ln=True)
                self.pdf.multi_cell(0, 7, self.safe_latin1(text))
                self.pdf.ln(4)

        # Section: Weekly opening hours (ONLY ONCE)
        self.pdf.ln(6)
        self.pdf.set_font("Arial", 'B', 13)
        self.pdf.cell(0, 7, "Weekly opening hours:", ln=True)
        self.pdf.set_font("Arial", '', 12)
        if restaurant.get("opening_hours"):
            for h in restaurant["opening_hours"]:
                formatted = self.safe_latin1(h).lstrip("- ").strip()
                self.pdf.cell(0, 6, formatted, ln=True)
        else:
            self.pdf.cell(0, 6, self.safe_latin1("No opening hours available."), ln=True)

        # Visual separator
        self.pdf.ln(6)
        self.pdf.set_draw_color(210,210,210)
        y = self.pdf.get_y()
        self.pdf.line(15, y, 195, y)
        self.pdf.ln(5)

    def add_weather_summary(self, forecast, best_day, city):
        self.pdf.add_page()
        self.pdf.set_font("Arial", 'B', 18)
        self.pdf.cell(0, 12, f"Weather summary: {city}", ln=1)
        self.pdf.set_font("Arial", '', 12)
        self.pdf.cell(0, 8, "Forecast for selected dates:", ln=1)
        for day in forecast:
            self.pdf.cell(0, 8, f"{day['date']}: {day['temperature_avg']}ºC, wind {day['wind_speed']} m/s, rain {day['rain_probability']}%", ln=1)
        self.pdf.ln(5)
        if best_day:
            self.pdf.set_font("Arial", 'B', 13)
            self.pdf.cell(0, 8, "Best day to eat:", ln=1)
            self.pdf.set_font("Arial", '', 12)
            self.pdf.cell(0, 8,
                f"{best_day['best_date']}: {best_day['best_temperature_avg']}ºC, wind {best_day['best_wind_speed']} m/s, rain {best_day['best_rain_probability']}%",
                ln=1
            )


    def generate(self, restaurants, forecast=None, best_day=None, city="Málaga",maps_url=None):
        self.portada(maps_url)
        for idx, rest in enumerate(restaurants, 1):
            self.add_restaurant(rest, idx)
        if forecast:
            self.add_weather_summary(forecast, best_day, city)
        self.pdf.output(self.filename)
        
