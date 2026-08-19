
import asyncio
from playwright.async_api import async_playwright

async def main():
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=False,
        args=["--start-maximized", "--no-sandbox"]
    )
    page = await browser.new_page()
    await page.goto("https://www.naukri.com/nlogin/login")
    print("PHYSICAL WINDOW LAUNCHED ON USER DESKTOP SCREEN!")
    await asyncio.sleep(600)

asyncio.run(main())
