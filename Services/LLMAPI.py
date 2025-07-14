import os
from dotenv import load_dotenv
import requests

load_dotenv()


class LLMAPI:
    BASE_URL = os.getenv('BASE_URL_LLM')
    
    def __init__(self):
        pass
    
    def get_models(self):
        response = requests.get(f"{self.BASE_URL}/models")
        return response.json()
    
    def post_chat_completion(self, data):
        response = requests.post(f"{self.BASE_URL}/chat/completions", json=data)
        return response.json()
    
    def post_completion(self, data):
        response = requests.post(f"{self.BASE_URL}/completions", json=data)
        return response.json()