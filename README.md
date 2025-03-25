# 🗺️🍽️ Ruta Gastronómica Express

> _Itinerarios à la carte para paladares inquietos_

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-ff4b4b)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 ¿Qué es esto?

**Ruta Gastronómica Express** es una aplicación web inteligente que te sugiere rutas personalizadas por los mejores restaurantes según tus gustos, tu presupuesto, el clima... ¡y tu hambre de aventuras!  
Todo esto en tiempo real y acompañado de un itinerario interactivo y un PDF con estilo.

---

## 🧠 ¿Cómo funciona?

```mermaid
graph TD;
    A[👤 Usuario] --> B[📝 Preferencias en Streamlit];
    B --> C[🧠 Backend Flask];
    C --> D1[📍 Módulo Recomendador];
    C --> D2[🗺️ Módulo Rutas Óptimas];
    C --> D3[📄 Generador PDF];
    D1 --> E[🌐 APIs externas (Google Maps, TripAdvisor, OpenWeather)];
    D2 --> E;
    D3 --> F[📥 Itinerario y mapa];
