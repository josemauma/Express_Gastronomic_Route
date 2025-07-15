# Express Gastronomic Route – Ruta fija + claves flexibles (PROMPT ACTUALIZADO)
# ---------------------------------------------------------------------------
# Ajustes clave:
#   1. Manejo de nombres de campos que pueden variar entre el JSON de Google
#      Maps (name, formatted_address, etc.) y las claves en español.
#   2. Sidebar y generación robustos: si falta 'nombre' o 'url' no revienta.
#   3. ***Nuevo prompt***: Descripción web, 2 reviews del JSON y **horario desglosado**.
# ---------------------------------------------------------------------------

import os
import json
from pathlib import Path
from typing import Any, Dict

import folium
from streamlit_folium import st_folium
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# ──────────────────────── Helpers ──────────────────────────────────────────

def obtener(d: Dict[str, Any], *claves, default="") -> Any:
    """Devuelve la primera clave existente en el dict (case-insensitive)."""
    for clave in claves:
        for k in (clave, clave.lower(), clave.capitalize()):
            if k in d:
                return d[k]
    return default


# ───────────────────── Configuración de página ─────────────────────────────
st.set_page_config(
    page_title="La elección perfecta para tu ruta Gastronómica",
    page_icon="🍽️",
    layout="wide",
)

# ───────────────────── Credenciales LLM ────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o-mini-2024-07-18"

# ───────────────────── Prompt del sistema (NUEVO) ──────────────────────────
SYSTEM_PROFILE = {
    "role": "system",
    "content": """
Eres un crítico gastronómico profesional con humor ágil e inteligente.
Usando la información que el usuario te entregue en un archivo **JSON exportado de Google Maps** y, cuando lo creas oportuno, buscando datos adicionales en internet, genera un *breve dossier* que contenga **tres bloques**:

1. **Descripción breve**  
   - Investiga en la web una sinopsis de 3-4 frases sobre el restaurante (estilo, especialidad, ambiente o historia).  
   - Añade un guiño de humor culinario.

2. **Reseñas destacadas**  
   - Localiza en el JSON las reseñas del restaurante.  
   - Selecciona las **2 reseñas más recientes** y muestra para cada una:  
     - **Autor** (`author_name`)  
     - **Puntuación en emojis** según `rating` (1-5 → ⭐️-⭐️⭐️⭐️⭐️⭐️).  
     - **Texto completo** (`text`)  
     - **Fecha** formateada como “15 de mayo de 2025”.

3. **Horario de apertura (desglosado)**  
   - Extrae del JSON el objeto `opening_hours` (o campos equivalentes).  
   - Desglosa **cada día de la semana** con su horario usando abreviaturas españolas: L, M, X, J, V, S, D.  
   - Si un día contiene varios tramos, sepáralos por coma.  
   - Si para algún día falta información, indica “Cerrado”.  
   - Si el JSON solo trae un horario general, repítelo para todos los días.  
   - Si no hay datos, indica: “Horario no disponible”.

**Formato de salida (en español)**
```
### Descripción
{párrafo}

### Reseñas (2)
• **Autor** – ⭐️⭐️⭐️⭐️☆
  “Texto…” (15 de mayo de 2025)
• **Autor** – ⭐️⭐️⭐️⭐️☆
  “Texto…” (14 de mayo de 2025)

### Horario
L 12:00-22:30  
M 12:00-22:30  
X 12:00-22:30  
J 12:00-22:30  
V 12:00-23:45  
S 12:00-23:45  
D 12:00-17:00
```

— No inventes reseñas ni horarios: si algún dato falta, dilo con claridad.  
— La puntuación en emojis debe reflejar **exactamente** la valoración.  
— Mantén un tono profesional, cercano y divertido.
""",
}

# ───────────────────── Carga de datos ──────────────────────────────────────
JSON_FILE = Path(
    "/Users/josemanuelmuelas/Desktop/Express_Gastronomic_Route/Database/Users_preferences/restaurant_details_20250522_163210.json"
)

if not JSON_FILE.exists():
    st.error(f"No se encontró el archivo {JSON_FILE}. Verifica la ruta.")
    st.stop()

with open(JSON_FILE, encoding="utf-8") as f:
    restaurantes = json.load(f)

# ───────────────────── Inicializa session_state ────────────────────────────
if "perfiles" not in st.session_state:
    st.session_state.perfiles = None

# ───────────────────── Sidebar ─────────────────────────────────────────────
st.sidebar.title("Restaurantes")
for r in restaurantes:
    nombre = obtener(r, "nombre", "name", default="(sin nombre)")
    url = obtener(r, "url", "maps_url", default="#")
    st.sidebar.markdown(f"- [{nombre}]({url})", unsafe_allow_html=True)

# ───────────────────── Título principal ────────────────────────────────────
st.title("🍽️ La elección perfecta para tu ruta Gastronómica")

# ───────────────────── Botón para generar ──────────────────────────────────
if st.button("Generar descripciones y mapa"):
    perfiles = []
    progress = st.progress(0)
    total = len(restaurantes)

    for idx, resto in enumerate(restaurantes, start=1):
        payload = {
            "nombre": obtener(resto, "nombre", "name"),
            "ubicación": obtener(resto, "ubicación", "formatted_address", "address"),
            "opening_hours": resto.get("opening_hours"),
            "reviews": resto.get("reviews", []),
        }

        msg = {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        try:
            resp = (
                llm.chat.completions.create(
                    model=MODEL,
                    messages=[SYSTEM_PROFILE, msg],
                    temperature=0.7,
                    timeout=60,
                )
            )
            perfil = resp.choices[0].message.content
        except Exception as exc:
            perfil = f"⚠️ Error al generar perfil: {exc}"

        perfiles.append((resto, perfil))
        progress.progress(idx / total, text=f"Generados {idx}/{total} perfiles…")

    progress.empty()
    st.session_state.perfiles = perfiles

# ───────────────────── Visualización ───────────────────────────────────────
if st.session_state.perfiles:
    cols = st.columns(2)
    for idx, (resto, perfil) in enumerate(st.session_state.perfiles):
        nombre = obtener(resto, "nombre", "name", default="(sin nombre)")
        with cols[idx % 2]:
            st.markdown(f"### {nombre}")
            st.markdown(perfil)

    st.subheader("📍 Ubicaciones en el mapa")

    lats = [resto.get("lat") for resto, _ in st.session_state.perfiles if resto.get("lat")]
    lons = [resto.get("lon") for resto, _ in st.session_state.perfiles if resto.get("lon")]

    if lats and lons:
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
    else:
        center_lat, center_lon = 36.7202, -4.4216

    mapa = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    for resto, _ in st.session_state.perfiles:
        lat, lon = resto.get("lat"), resto.get("lon")
        nombre = obtener(resto, "nombre", "name", default="(sin nombre)")
        if lat is not None and lon is not None:
            folium.Marker(
                [lat, lon],
                tooltip=nombre,
                icon=folium.Icon(icon="utensils", prefix="fa", color="darkred"),
            ).add_to(mapa)

    st_folium(mapa, width=900, height=450)
else:
    st.info("Pulsa el botón para generar las descripciones y ver el mapa.")