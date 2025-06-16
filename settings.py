import requests
import os
from dotenv import load_dotenv

def check_api_key(api_url, api_key, test_endpoint="/status"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(f"{api_url}{test_endpoint}", headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error comprobando la API KEY: {e}")
        return False

def check_api_key_from_env(api_key_var):
    load_dotenv()  # Carga las variables del archivo .env
    api_url = os.getenv("API_URL")
    api_key = os.getenv(api_key_var)
    if not api_url or not api_key:
        print(f"Faltan variables API_URL o {api_key_var} en el archivo .env")
        return False
    return check_api_key(api_url, api_key)
