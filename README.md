# 🗺️🍽️ Express Gastronomic Route

> _Itinerarios à la carte for adventurous foodies_

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-ff4b4b)](https://streamlit.io/)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)


---

---

## 🌟 What is this?

**Ruta Gastronómica Express** is a smart web app that suggests personalized routes through the best restaurants based on your tastes, budget, weather... and your hunger for adventure! 

All of this in real time, along with an interactive itinerary and a stylish PDF.

---

## 🧠 How does it work?

```mermaid
graph TD;
    A[User] --> B[Preferences in Streamlit UI];
    B --> C[API Calls
            - OpenWeather
            - Google];
    C --> D[Recommendation Module
            - Ranking & Filtering
            - Top 3 Selection];
    C --> E[Route Optimization Model
            - Google Maps Integration];
    D --> G[On-Screen Visualization];
    E --> G[On-Screen Visualization];
    G --> F[PDF Generator];
    F --> H[Downloadable Itinerary in PDF];
```
---
## 🎯 Key Features

- ✅ Restaurant recommendations based on your preferences

- ✅ Optimized routes based on time, transport, and weather

- ✅ Interactive map with itinerary

- ✅ Custom PDF generation with your route

- ✅ Modular, scalable, and applicable to other cities
  
---

## 🧪 Technologies

| Type             | Tools                                                          |
|------------------|----------------------------------------------------------------|
| Language         | Python                                                         |
| Web Backend      | Streamlit                                                      |
| Recommendations  | LLM phi4                                                       |
| APIs             | Google Maps, OpenWeather                                       |
| Visualization    | Streamlit Map + PDF Generator                                  |
| Dev Tools        | GitHub, VS Code                                                |

---

## 🛠️ Installation

```bash
git clone https://github.com/josemauma/TFM_Ruta_Gastronomica
cd TFM_Ruta_Gastronomica
pip install -r requirements.txt
streamlit run app.py

```

---

## 💡 Example of Use

1. The user accesses the interface and answers questions like:
   - Direction 
   - Preferred type of food
   - Available time  

2. The app connects to external APIs:
   - Google Maps   
   - OpenWeather  

3. An optimized route with personalized recommendations is generated.  
4. It is displayed on an interactive map.  
5. A downloadable PDF with the itinerary and suggestions is generated.  

---

## 🚧 Project Status

- 🔍 In development  

---

## 📄 License

This project is licensed under the **CC BY-NC-ND 4.0 License**.  
See the [`LICENSE`](./LICENSE) file for more details.

---

## 📫 Contact

**José Manuel Muelas de la Linde**  
Master’s Student in Big Data, AI & Data Engineering


📍 Málaga, Spain  
🔗 [LinkedIn](www.linkedin.com/in/josemanuel-muelas-delalinde)  
🐙 [GitHub](https://github.com/josemauma)

