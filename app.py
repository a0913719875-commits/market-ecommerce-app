import os
import requests
from secret_manager import get_secret
from token_manager import TokenManager

def fetch_data():
    # Use the secret manager to retrieve the API token securely
    api_token = get_secret('ShioajiAPIToken')
    
    headers = {
        'Authorization': f'Bearer {api_token}'
    }

    response = requests.get('https://api.shioaji.com/v1/data', headers=headers)
    return response.json()

if __name__ == '__main__':
    token_manager = TokenManager()
    new_token = token_manager.rotate_token()
    print("Fetched Data:", fetch_data())