import json
from fpdf import FPDF
from datetime import datetime
import re

def safe_latin1(text):
    return text.encode('latin-1', 'ignore').decode('latin-1')

def load_restaurants(json_path):
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)

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

    # Si no hay secciones detectadas, pasa todo a Descripción
    if not any([secciones["Descripción"], secciones["Reseñas"], secciones["Horario"]]):
        secciones["Descripción"] = dossier.strip()
    else:
        secciones["Descripción"] = secciones["Descripción"].strip()

    return secciones

def generate_pdf(restaurants, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)

    for idx, r in enumerate(restaurants, 1):
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 12, safe_latin1(f"{idx}. {r['name']}"), ln=True, align='C')
        pdf.ln(3)

        sec = split_dossier_sections(r['dossier'])

        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, safe_latin1("Descripción:"), ln=True)
        pdf.set_font("Arial", '', 12); pdf.multi_cell(0, 8, safe_latin1(sec["Descripción"]))
        pdf.ln(2)

        if sec["Reseñas"]:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, safe_latin1("Reseñas destacadas:"), ln=True)
            pdf.set_font("Arial", '', 12)
            for review in sec["Reseñas"]:
                # Elimina solo los asteriscos ** pero deja el nombre del autor
                if isinstance(review, str):
                    review_sin_asteriscos = re.sub(r"\*\*", "", review).strip()
                else:
                    review_sin_asteriscos = ""
                # Busca el nombre del autor (antes de ':') y el texto de la reseña
                match = re.match(r"([^:]+):(.*)", review_sin_asteriscos)
                if match:
                    autor = match.group(1).strip()
                    texto = match.group(2).strip()
                    pdf.cell(10)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 7, safe_latin1(autor + ":"), ln=True)
                    pdf.set_font("Arial", '', 12)
                    pdf.cell(15)
                    pdf.multi_cell(0, 7, safe_latin1(texto))
                else:
                    pdf.set_font("Arial", '', 12)
                    pdf.cell(10)
                    pdf.multi_cell(0, 7, safe_latin1(review_sin_asteriscos))
                pdf.ln(1)

        # Estrellas usando zapfdingbats
        if "rating" in r:
            pdf.set_font("zapfdingbats", '', 12)  # dingbats for stars :contentReference[oaicite:4]{index=4}
            count = int(round(r["rating"]))
            for _ in range(count):
                pdf.cell(5, 7, chr(51))  # 51 -> ★
            pdf.ln(5)
            pdf.set_font("Arial", '', 12)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, safe_latin1("Horario:"), ln=True)
        pdf.set_font("Arial", '', 12)
        if sec["Horario"]:
            for h in sec["Horario"]:
                pdf.cell(0, 7, safe_latin1(f"• {h}"), ln=True)
        else:
            pdf.cell(0, 7, safe_latin1("No hay horario disponible, llamar al restaurante para conocer la disponibilidad"), ln=True)
        pdf.ln(2)

    pdf.output(filename)
    print(f"📄 PDF guardado: {filename}")

def generate_all_pdfs(path):
    data = load_restaurants(path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    generate_pdf(data, f"ruta_gastronomica_{ts}.pdf")


