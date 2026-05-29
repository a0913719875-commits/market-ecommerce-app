import asyncio
from playwright.async_api import async_playwright

async def test_pomodoro_timer():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('file:///path/to/your/index.html')

        await page.click('button:text("Start")')
        await asyncio.sleep(2)  # Let the timer run for a few seconds
        time_before = await page.text_content('#time')
        
        await page.click('button:text("Stop")')
        await asyncio.sleep(2)
        time_after_stop = await page.text_content('#time')
        
        assert time_before != time_after_stop
        
        await page.click('button:text("Reset")')
        reset_time = await page.text_content('#time')
        assert reset_time == "25:00"
        
        await page.click('button:text("Start")')
        await asyncio.sleep(1500)  # Wait for timer to switch modes automatically
        new_mode = await page.text_content('#mode')
        new_time = await page.text_content('#time')
        assert new_mode == "Break Mode"
        assert new_time == "05:00"

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_pomodoro_timer())