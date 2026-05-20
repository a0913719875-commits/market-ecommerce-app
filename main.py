import asyncio
from supabase_async import create_client, SupabaseAsyncClient

SUPABASE_URL = 'https://your-supabase-url.supabase.co'
SUPABASE_KEY = 'your-supabase-key'

async def main():
    supabase: SupabaseAsyncClient = create_client(SUPABASE_URL, SUPABASE_KEY)

    data = {
        'column1': 'value1',
        'column2': 'value2'
    }

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = await supabase.table('your_table_name').insert(data).execute()
            print(f"Insert success: {response}")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                raise

if __name__ == '__main__':
    asyncio.run(main())