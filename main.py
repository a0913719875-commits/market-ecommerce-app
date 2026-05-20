import os
from google.cloud import secretmanager
from cryptography.fernet import Fernet

# Initialize Secret Manager client
def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# Token rotation simulation
def rotate_token(current_token):
    # Example rotation logic
    return Fernet.generate_key().decode()

# Load Shioaji API token from Google Secret Manager
def get_shioaji_api_token():
    project_id = os.getenv('GCP_PROJECT_ID')
    secret_id = os.getenv('SHIOAJI_API_SECRET_ID')
    version_id = "latest"
    return access_secret_version(project_id, secret_id, version_id)

# Main function to demonstrate secure token handling
def main():
    # Obtain token securely
    api_token = get_shioaji_api_token()
    print("API Token fetched from Secret Manager:", api_token)

    # Rotate token (for demonstration)
    new_token = rotate_token(api_token)
    print("New rotated token:", new_token)

if __name__ == "__main__":
    main()