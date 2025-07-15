import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

api_key = os.getenv("API_WEATHER_KEY") 

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather_info(self, city):
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None

    def get_weather_forecast(self, city):
        url = "http://api.openweathermap.org/data/2.5/forecast/daily"
        params = {'q': city, 'appid': self.api_key, 'cnt': 10, 'units': 'metric'}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            forecast = []
            for day in data['list']:
                date_corrected = datetime.fromtimestamp(day['dt']).strftime('%d/%m/%Y')
                day_forecast = {
                    'date': date_corrected,
                    'temperature_avg': day['temp']['day'],
                    'wind_speed': day['speed'],
                    'rain_probability': day.get('rain', 0)
                }
                forecast.append(day_forecast)
            return forecast
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return None

    def get_best_day_to_go_out(self, forecast, start_date, end_date):
        try:
            start_timestamp = int(datetime.strptime(start_date, '%d/%m/%Y').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%d/%m/%Y').timestamp())
        except ValueError:
            print("Error: Formato de fecha inválido. Use 'DD/MM/AAAA'.")
            return None

        filtered_forecast = [
            day for day in forecast
            if start_timestamp <= int(datetime.strptime(day['date'], '%d/%m/%Y').timestamp()) <= end_timestamp
        ]

        if not filtered_forecast:
            print("No hay datos de pronóstico para el rango de fechas proporcionado.")
            return None

        best_day = min(
            filtered_forecast,
            key=lambda day: (
                day['rain_probability'],
                abs(day['temperature_avg'] - 25),
                day['wind_speed']
            )
        )

        return {
            'best_date': best_day['date'],
            'best_temperature_avg': best_day['temperature_avg'],
            'best_wind_speed': best_day['wind_speed'],
            'best_rain_probability': best_day['rain_probability']
        }
        
            
    def filter_temp_range(self, forecast, start_date, end_date):
        """Filtra el pronóstico para quedarse solo con los días entre start_date y end_date (incluidos)."""
        # Convierte las fechas a objetos datetime para comparar
        fmt = "%d/%m/%Y"
        try:
            start = datetime.strptime(start_date, fmt)
            end = datetime.strptime(end_date, fmt)
        except ValueError:
            print("Error: Formato de fecha inválido. Use 'DD/MM/AAAA'.")
            return []
        # Filtra los días dentro del rango
        return [
            day for day in forecast
            if start <= datetime.strptime(day['date'], fmt) <= end
        ]
