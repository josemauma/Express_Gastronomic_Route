import requests
from datetime import datetime

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather_info(self, city):
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {'q': city, 'appid': self.api_key}
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
        params = {'q': city, 'appid': self.api_key, 'cnt': 7, 'units': 'metric'}
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

    def get_best_day_to_go_out(self, forecast, start_date, end_date):
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
                day['rain_probability'],
                abs(day['temperature_avg'] - 25),
                day['wind_speed']
            )
        )

        return {
            'date': datetime.utcfromtimestamp(best_day['date']).strftime('%d/%m/%Y'),
            'temperature_avg': best_day['temperature_avg'],
            'wind_speed': best_day['wind_speed'],
            'rain_probability': best_day['rain_probability']
        }
