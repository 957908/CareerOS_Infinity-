import os
import sys
import subprocess

def launch():
    print("Launching interactive Google Chrome on user desktop...")
    backend_dir = r"c:\Users\kadam\Downloads\CareerOS\backend"
    python_exe = os.path.join(backend_dir, r"venv\Scripts\python.exe")
    
    script_code = """
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
"""
    
    temp_script = os.path.join(backend_dir, "temp_desktop_launch.py")
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(script_code)
        
    cmd = f'start "" "{python_exe}" "{temp_script}"'
    subprocess.Popen(cmd, shell=True, cwd=backend_dir)
    print("Triggered Windows desktop interactive process via 'start' command!")

if __name__ == "__main__":
    launch()
