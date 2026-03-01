import httpx
from bs4 import BeautifulSoup
import asyncio

async def search_google_shopping(query):
    url = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.get(url)
        print("Status", res.status_code)
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # In Google Shopping, products are usually in elements with class "sh-dgr__content" or "i0X6df"
        items = soup.find_all('div', class_='sh-dgr__grid-result')
        if not items:
            items = soup.find_all('div', class_='sh-dgr__content')
            
        print(f"Found {len(items)} items")
        for item in items[:5]:
            title = item.find('h3')
            price = item.find('span', class_='a8Pemb')
            merchant = item.find('div', class_='aULzUe')
            link = item.find('a')
            
            print("---")
            if title: print("Title:", title.text)
            if price: print("Price:", price.text)
            if merchant: print("Merchant:", merchant.text)
            if link: print("URL:", link.get('href'))

if __name__ == "__main__":
    asyncio.run(search_google_shopping("Amul Milk 500ml"))
