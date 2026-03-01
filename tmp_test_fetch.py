import httpx
from bs4 import BeautifulSoup
import asyncio

async def test_platforms(query):
    print(f"Testing for: {query}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        # Blinkit
        print("\n--- Testing Blinkit ---")
        try:
            res_b = await client.get(f"https://blinkit.com/s/?q={query}")
            print(f"Status: {res_b.status_code}")
            if "Just a moment..." in res_b.text or "Cloudflare" in res_b.text:
                print("Cloudflare protection detected!")
            else:
                print(f"Response length: {len(res_b.text)}")
                # check if there are products in HTML
                soup = BeautifulSoup(res_b.text, 'html.parser')
                print(f"Title: {soup.title.string if soup.title else 'No Title'}")
        except Exception as e:
            print(f"Error: {e}")

        # Instamart
        print("\n--- Testing Instamart ---")
        try:
            res_i = await client.get(f"https://www.swiggy.com/instamart/search?custom_back=true&query={query}")
            print(f"Status: {res_i.status_code}")
            if "Access Denied" in res_i.text or "Cloudflare" in res_i.text:
                print("Protection detected!")
            else:
                print(f"Response length: {len(res_i.text)}")
                soup = BeautifulSoup(res_i.text, 'html.parser')
                print(f"Title: {soup.title.string if soup.title else 'No Title'}")
        except Exception as e:
            print(f"Error: {e}")

        # BigBasket
        print("\n--- Testing BigBasket ---")
        try:
            res_bb = await client.get(f"https://www.bigbasket.com/ps/?q={query}")
            print(f"Status: {res_bb.status_code}")
            if "Access Denied" in res_bb.text or "Cloudflare" in res_bb.text:
                print("Protection detected!")
            else:
                print(f"Response length: {len(res_bb.text)}")
                soup = BeautifulSoup(res_bb.text, 'html.parser')
                print(f"Title: {soup.title.string if soup.title else 'No Title'}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_platforms("milk"))
