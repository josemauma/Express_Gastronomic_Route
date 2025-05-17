import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Perfiles Gastronómicos para tu TFM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Carga de credenciales ───────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.sidebar.error("🔑 Introduce tu OPENAI_API_KEY en el .env")
    st.stop()

llm_client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o-mini-2024-07-18"

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Eres un crítico gastronómico profesional con humor ágil e inteligente.
A partir de la información que el usuario proporcione sobre un restaurante,
genera una salida estructurada en cuatro bloques claros:

1. Descripción breve (3–4 frases).  
2. Mejores platos (3 ítems, nombre + motivo de su éxito).  
3. Comentarios positivos de clientes (3 reseñas ficticias, 1–2 frases cada una).  
4. Justificación de elección para un TFM sobre innovación y sostenibilidad (2–3 frases).

Siempre responde en español.
"""
}

# ─── Carga de datos ────────────────────────────────────────────────────────────
with open("/Users/josemanuelmuelas/Desktop/Express_Gastronomic_Route/restaurants.json", encoding="utf-8") as f:
    restaurantes = json.load(f)

# ─── Sidebar de información ───────────────────────────────────────────────────
st.sidebar.title("⚙️ Ajustes")
st.sidebar.write("Aquí podrás ver los restaurantes cargados y tu API Key.")

for r in restaurantes:
    st.sidebar.markdown(f"**{r['nombre']}**")  
st.sidebar.caption("Todos los datos salen de `restaurants.json`")

# ─── Título principal ─────────────────────────────────────────────────────────
st.title("🍽️ Perfiles Gastronómicos para tu TFM")

st.markdown(
    "Pulsa el botón y genera de una vez los perfiles **El Pimpi** y **La Tranca**, "
    "listos para copiar en tu trabajo fin de máster."
)

# ─── Botón único para generar ─────────────────────────────────────────────────
if st.button("🚀 Generar todos los perfiles"):

    # Creamos dos columnas para mostrar resultado de ambos
    col1, col2 = st.columns(2)

    for idx, resto in enumerate(restaurantes):
        user_msg = {
            "role": "user",
            "content": json.dumps(resto, ensure_ascii=False)
        }
        # Llamada al LLM
        response = llm_client.chat.completions.create(
            model=MODEL,
            messages=[SYSTEM_PROMPT, user_msg],
            temperature=0.7,
            max_tokens=600
        ).choices[0].message.content

        # Mostramos en la columna correspondiente
        with (col1 if idx == 0 else col2):
            st.markdown(f"### {resto['nombre']}")
            st.markdown(response)

else:
    st.info("Haz clic en **Generar todos los perfiles** para comenzar.")

