from fpdf import FPDF
from datetime import datetime


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
        secciones = {"Descripción": "", "Reseñas": [], "Horario": []}
        current = None
        for line in dossier.splitlines():
            key = line.strip().lower().replace(":", "").replace("#", "")
            if "descrip" in key:
                current = "Descripción"; continue
            if "reseñ" in key:
                current = "Reseñas"; continue
            if "horario" in key:
                current = "Horario"; continue
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if current == "Descripción":
                secciones["Descripción"] += line_stripped + " "
            elif current in ("Reseñas", "Horario"):
                 secciones[current].append(line_stripped)
        if not any([secciones["Descripción"], secciones["Reseñas"], secciones["Horario"]]):
            secciones["Descripción"] = dossier.strip()
        else:
            secciones["Descripción"] = secciones["Descripción"].strip()
        return secciones



    def portada(self, weather=None):
        self.pdf.add_page()
        self.pdf.ln(15)
        self.pdf.set_font("Arial", 'B', 26)
        self.pdf.set_text_color(0, 90, 158)
        self.pdf.cell(0, 20, self.safe_latin1(self.title), ln=True, align='C')
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("Arial", '', 14)
        self.pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
        self.pdf.ln(10)
        self.pdf.ln(20)
        # Inserta la imagen centrada (ajusta path y tamaño)
        self.pdf.image("malagaPortada.jpg", x=30, w=150)  # Ajusta el path y ancho según tu imagen
        self.pdf.ln(15)
        
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
        self.pdf.ln(16)
        self.pdf.set_font("Arial", '', 12)
        self.pdf.multi_cell(0, 7, self.safe_latin1(f"Address: {restaurant.get('address', 'Not available')}"))
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
        # Aquí deberías pasar el texto que da el LLM como argumento, ej: restaurant['llm_description']
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
                # Cambia el bullet '•' por un guion '-' para evitar problemas de codificación
                self.pdf.cell(0, 8, f"- {name} ({rating}/5) Stars", ln=True)
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

    def add_weather_summary(self, forecast, best_day, city="Málaga"):
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
            self.pdf.cell(0, 8, "Best day to visit:", ln=1)
            self.pdf.set_font("Arial", '', 12)
            self.pdf.cell(0, 8,
                f"{best_day['best_date']}: {best_day['best_temperature_avg']}ºC, wind {best_day['best_wind_speed']} m/s, rain {best_day['best_rain_probability']}%",
                ln=1
            )


    def generate(self, restaurants, weather=None, forecast=None, best_day=None, city="Málaga"):
        self.portada(weather)
        for idx, rest in enumerate(restaurants, 1):
            self.add_restaurant(rest, idx)
        # Añade el resumen meteorológico AL FINAL (ahora sí)
        if forecast:
            self.add_weather_summary(forecast, best_day, city)
        self.pdf.output(self.filename)
        
