import time
import logging
import requests
from shioaji import Shioaji
from linebot import LineBotApi
from linebot.models import TextSendMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Shioaji API
api = Shioaji()

# Line Notify Config
LINE_CHANNEL_ACCESS_TOKEN = 'your_line_channel_access_token'
LINE_USER_ID = 'your_line_user_id'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def exponential_backoff_retry(func, max_retries=3):
    for n in range(max_retries):
        try:
            return func()
        except Exception as e:
            wait_time = 2 ** n
            logger.warning(f"Retry {n + 1}/{max_retries} failed: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")

def health_check():
    try:
        # Placeholder for health check logic
        # Ideally this checks a specific endpoint or service status
        return api.Contracts.Stocks
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        send_line_alert(f"API Health Check Failed: {e}")
        return False

def send_line_alert(message):
    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))
    except Exception as e:
        logger.error(f"Failed to send LINE alert: {e}")

def connect_to_shioaji():
    try:
        api.login(
            person_id='YOUR_PERSON_ID',
            passwd='YOUR_PASSWORD'
        )
        logger.info("Connected to Shioaji API successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to Shioaji API: {e}")
        send_line_alert(f"Failed to connect to Shioaji API: {e}")
        return False
    return True

def main():
    # Retry connecting with exponential backoff
    success = exponential_backoff_retry(connect_to_shioaji)
    if not success:
        send_line_alert("Unable to establish a connection to Shioaji API after multiple attempts.")
    
    # Health check
    if not health_check():
        send_line_alert("Shioaji API health check failed.")
    else:
        logger.info("API Health is Good.")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60 * 5)  # Run the check every 5 minutes