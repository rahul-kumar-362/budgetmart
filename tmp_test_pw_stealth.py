import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth
from bs4 import BeautifulSoup

async def fetch_blinkit(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a convincing user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        await stealth(page)
        
        url = f"https://blinkit.com/s/?q={query}"
        print(f"Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000) # give it time to load dynamic content
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            print(f"Blinkit Title: {soup.title.string if soup.title else 'None'}")
            
            if "Just a moment" in str(soup.title) or "Cloudflare" in str(soup):
                print("STILL BLOCKED BY CLOUDFLARE!")
            else:
                print("SUCCESSFUL BYPASS!")
                
        except Exception as e:
            print(f"Error fetching Blinkit: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_blinkit("milk"))
