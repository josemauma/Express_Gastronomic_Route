import requests
from dotenv import load_dotenv
import os
from datetime import datetime
#import json


def get_weather_info(city, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city, 'appid': api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None


def get_weather_forecast(city, api_key):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily"
    params = {'q': city, 'appid': api_key, 'cnt': 7, 'units': 'metric'}
            
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        forecast = []
        for day in data['list']:
            day_forecast = {
                'date': day['dt'],
                'temperature_avg': day['temp']['day'],
                'wind_speed': day['speed'],
                'rain_probability': day.get('rain', 0)
            }
            forecast.append(day_forecast)
        return forecast
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None



def get_best_day_to_go_out(forecast, start_date, end_date):
    try:
        start_timestamp = int(datetime.strptime(start_date, '%d/%m/%Y').timestamp())
        end_timestamp = int(datetime.strptime(end_date, '%d/%m/%Y').timestamp())
    except ValueError:
        print("Error: Formato de fecha inválido. Use 'DD/MM/AAAA'.")
        return None

    filtered_forecast = [
        day for day in forecast
        if start_timestamp <= day['date'] <= end_timestamp
    ]

    if not filtered_forecast:
        print("No hay datos de pronóstico para el rango de fechas proporcionado.")
        return None

    best_day = min(
        filtered_forecast,
        key=lambda day: (
            day['rain_probability'],  # Prioridad 1: mínima probabilidad de lluvia
            abs(day['temperature_avg'] - 25),  # Prioridad 2: temperatura más cercana a 25°C
            day['wind_speed']         # Prioridad 3: menor velocidad del viento
        )
    )

    return {
        'date': datetime.utcfromtimestamp(best_day['date']).strftime('%d/%m/%Y'),
        'temperature_avg': best_day['temperature_avg'],
        'wind_speed': best_day['wind_speed'],
        'rain_probability': best_day['rain_probability']
    }
    
 
   
def main():
    city = "Malaga"
    load_dotenv()
    api_key = os.getenv('API_WEATHER_KEY')
    
    if not api_key:
        print("Error: La clave de API no está configurada.")
        return
    
    # Información actual del clima
    data = get_weather_info(city, api_key)
    if data:
        city_name = data['name']
        weather = data['weather'][0]['description']
        temperature_k = data['main']['temp']
        temperature_c = temperature_k - 273.15  # Convertir a Celsius
        rain_probability = data.get('rain', {}).get('1h', 0)  # Probabilidad de lluvia en la última hora (en mm)
        
        print(f"Ciudad: {city_name}")
        print(f"Clima: {weather}")
        print(f"Temperatura: {temperature_c:.1f}°C")
        print(f"Probabilidad de lluvia (última hora): {rain_probability} mm")
    
    # Pronóstico del clima
    forecast = get_weather_forecast(city, api_key)
    if forecast:
        print("\nPronóstico del clima para los próximos días:")
        for day in forecast:
            formatted_date = datetime.utcfromtimestamp(day['date']).strftime('%d/%m/%Y')
            print(f"Fecha: {formatted_date}")
            print(f"Temperatura promedio: {day['temperature_avg']:.1f}°C")
            print(f"Velocidad del viento: {day['wind_speed']} m/s")
            print(f"Probabilidad de lluvia: {day['rain_probability']} mm")
            print("-" * 30)
        
        # Mejor día para salir
        start_date = input("\nIngrese la fecha de inicio (DD/MM/AAAA): ")
        end_date = input("Ingrese la fecha de fin (DD/MM/AAAA): ")
        best_day = get_best_day_to_go_out(forecast, start_date, end_date)
        if best_day:
            print("\nEl mejor día para salir es:")
            print(f"Fecha: {best_day['date']}")
            print(f"Temperatura promedio: {best_day['temperature_avg']:.1f}°C")
            print(f"Velocidad del viento: {best_day['wind_speed']} m/s")
            print(f"Probabilidad de lluvia: {best_day['rain_probability']} mm")

if __name__ == "__main__":
    main()
