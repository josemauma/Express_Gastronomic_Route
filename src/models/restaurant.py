import os
import googlemaps
from datetime import datetime



class GastronomicRoute:
    def __init__(self, api_key):
        self.client = googlemaps.Client(key=api_key)

    def search_places(self, location, radius, query):
        """
        Busca lugares gastronómicos cerca de una ubicación.
        
        :param location: Tuple con latitud y longitud (lat, lng).
        :param radius: Radio de búsqueda en metros.
        :param query: Tipo de lugar o palabra clave (ej. "restaurant").
        :return: Lista de lugares encontrados.
        """
        places = self.client.places_nearby(
            location=location,
            radius=radius,
            keyword=query
        )
        return places.get('results', [])

    def get_place_details(self, place_id):
        """
        Obtiene detalles de un lugar específico.
        
        :param place_id: ID único del lugar.
        :return: Detalles del lugar.
        """
        details = self.client.place(place_id=place_id)
        return details.get('result', {})

# Ejemplo de uso
if __name__ == "__main__":
    API_KEY = os.getenv('API_GOOGLE_PLACES')
    route = GastronomicRoute(API_KEY)
    
    # Busca restaurantes cerca de una ubicación con un rango más pequeño
    location = (36.7213028, -4.4216366)  # Málaga, España
    results = route.search_places(location, 100, "restaurant")  
    for place in results:
        print(place["name"], "-", place["vicinity"])