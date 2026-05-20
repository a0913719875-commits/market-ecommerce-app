import asyncio
import aiohttp
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
import json

# Load your service account credentials
with open('service_account.json') as f:
    service_account_info = json.load(f)

creds = ServiceAccountCreds(**service_account_info)

async def update_google_sheet(spreadsheet_id, range_name, values):
    async with Aiogoogle(service_account_creds=creds) as google:
        sheets_v4 = await google.discover('sheets', 'v4')
        request = sheets_v4.spreadsheets.values.update(spreadsheetId=spreadsheet_id,
                                                       range=range_name,
                                                       valueInputOption='RAW',
                                                       json={'values': values})

        for attempt in range(3):  # Retry up to 3 times
            try:
                response = await google.as_service_account(request)
                print(f"Update success: {response}")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise

# Example usage
spreadsheet_id = 'your_spreadsheet_id_here'
range_name = 'Sheet1!A1:D5'
values = [
    ["Value1", "Value2"],
    ["Value3", "Value4"]
]

asyncio.run(update_google_sheet(spreadsheet_id, range_name, values))