import time

class TokenManager:
    def __init__(self):
        self.token = None
        self.expiration_time = None

    def rotate_token(self):
        # Simulate token rotation
        # This function should interact with the API to get a new token
        self.token = 'new_secure_api_token'
        self.expiration_time = time.time() + 3600  # Token valid for 1 hour
        return self.token

    def is_token_expired(self):
        return time.time() > self.expiration_time

    def get_valid_token(self):
        if self.is_token_expired() or self.token is None:
            return self.rotate_token()
        return self.token