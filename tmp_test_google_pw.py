import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def search_google_shopping(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        url = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
        print(f"Navigating to {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            print("Title:", soup.title.string if soup.title else "None")
            
            # Find shopping results
            items = soup.find_all('div', class_='sh-dgr__grid-result')
            if not items:
                items = soup.find_all('div', class_='sh-dgr__content')
                
            print(f"Found {len(items)} items")
            for item in items[:3]:
                title = item.find('h3')
                price = item.find('span', class_='a8Pemb')
                merchant = item.find('div', class_='aULzUe')
                print("---")
                if title: print("Title:", title.text)
                if price: print("Price:", price.text)
                if merchant: print("Merchant:", merchant.text)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(search_google_shopping("Amul Milk 500ml"))
