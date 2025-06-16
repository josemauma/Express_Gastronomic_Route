import os
import json
import folium
from streamlit_folium import st_folium
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# ─── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="La elección perceta para tu ruta Gastronómica",
    page_icon="🍽️",
    layout="wide"
)

# ─── Credenciales LLM ──────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o-mini-2024-07-18"

# ─── Prompt sistema ─────────────────────────────────────────────────────────
SYSTEM_PROFILE = {
    "role": "system",
    "content": """
Eres un crítico gastronómico profesional con humor ágil e inteligente.  
A partir de la información que el usuario proporcione sobre un restaurante, sigue estos pasos:

1. **Búsqueda y extracción de reseñas**  
   - Activa tu modo navegador o plugin de “web browsing”.  
   - Ve a Google Reviews (o TripAdvisor) y busca el restaurante “[Nombre del Restaurante]” en “[Ciudad, País]”.  
   - Extrae las **10 reseñas más recientes** (o todas las disponibles si hay menos de 10), anotando para cada una:  
     - Autor   
     - Puntuación en emojis (de ⭐️ a ⭐️⭐️⭐️⭐️⭐️, según la valoración real)  
     - Texto completo de la reseña  

2. **Análisis y selección de comentarios positivos**  
   - De esas reseñas ordenadas de la más reciente a la más antigua, elige los **3 comentarios positivos** más elocuentes.

3. **Salida estructurada**  
   Genera tu respuesta en **español** y ordénala en **tres bloques claros**:

   **Bloque 1: Descripción breve**  
   - 3–4 frases con tu toque de humor, pintando ambiente, estilo y propuesta del restaurante.

   **Bloque 2: Mejores platos**  
   - Lista de 3 ítems. Para cada plato, indica:  
     - **Nombre del plato**  
     - **Motivo de su éxito** (sabor, presentación, originalidad…).

   **Bloque 3: Comentarios positivos**  
   - Lista con **viñetas** (•) para los 3 comentarios seleccionados, con este formato **idéntico** en cada uno:  
     ```
     • **Autor** – [emoji según valor real, p. ej. ⭐️⭐️⭐️⭐️☆]  
       “Texto completo de la reseña”
     ``` 

**Puntos clave para que funcione**   
- La puntuación en emojis debe reflejar **exactamente** la valoración real (1 a 5).  
- Mantén uniforme el estilo en ambas columnas. 
- Sé muy preciso con el nombre y la ubicación del restaurante.  
- Muestra siempre la fecha en formato “15 de mayo de 2025” para evitar ambigüedades.  
- Introduce tu humor con sutileza: un chiste ligero o una metáfora gastronómica.  
- Si no encuentras 10 reseñas, indícalo (“Solo he hallado 7 reseñas disponibles”).  
- Organiza cada bloque con encabezados claros y viñetas.  
- Usa un tono profesional, pero cercano y divertido.  
"""
}

# ─── Carga de datos ────────────────────────────────────────────────────────────
with open("/Users/josemanuelmuelas/Desktop/Express_Gastronomic_Route/restaurants.json", encoding="utf-8") as f:
    restaurantes = json.load(f)

# ─── Inicializa session_state ───────────────────────────────────────────────
if "perfiles" not in st.session_state:
    st.session_state.perfiles = None

# ─── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.title("Restaurantes")
for r in restaurantes:
    st.sidebar.markdown(
        f"- [{r['nombre']}]({r['url']})", 
        unsafe_allow_html=True
    )

# ─── Título principal ─────────────────────────────────────────────────────────
st.title("🍽️ La elección perfecta para tu ruta Gastronómica")

# ─── Botón para generar ──────────────────────────────────────────────────────
if st.button("Generar descripciones y mapa"):
    perfiles = []
    for resto in restaurantes:
        # 1) Generamos perfil
        msg = {"role": "user", "content": json.dumps({
            "nombre": resto["nombre"],
            "ubicación": resto["ubicación"],
            "cocina": resto["cocina"],
            "ambiente": resto["ambiente"],
            "precio_medio": resto["precio_medio"],
            "público": resto["público"],
            "extras": resto["extras"]
        }, ensure_ascii=False)}
        perfil = llm.chat.completions.create(
            model=MODEL,
            messages=[SYSTEM_PROFILE, msg],
            temperature=0.7
        ).choices[0].message.content
        perfiles.append((resto, perfil))

    # Guarda en estado
    st.session_state.perfiles = perfiles

# ─── Muestra perfiles y mapa si ya están generados ───────────────────────────
if st.session_state.perfiles:
    # Textos en dos columnas
    cols = st.columns(2)
    for idx, (resto, perfil) in enumerate(st.session_state.perfiles):
        with cols[idx]:
            st.markdown(f"### {resto['nombre']}")
            st.markdown(perfil)

    # Mapa justo debajo
    st.subheader("📍 Ubicaciones en el mapa")
    mapa = folium.Map(
        location=[36.7202, -4.4216], 
        zoom_start=15
    )
    # Asegúrate de que recorres todos los restaurantes
    for resto, _ in st.session_state.perfiles:
        lat = resto.get("lat")
        lon = resto.get("lon")
        if lat is not None and lon is not None:
            folium.Marker(
                [lat, lon],
                tooltip=resto["nombre"],
                icon=folium.Icon(icon='utensils', prefix='fa', color='darkred')
            ).add_to(mapa)
    st_folium(mapa, width=900, height=450)
else:
    st.info("Pulsa el botón para generar las descripciones y ver el mapa.")
