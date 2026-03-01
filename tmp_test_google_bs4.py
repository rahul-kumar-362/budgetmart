import urllib.request
from bs4 import BeautifulSoup
import re

def search_free_google_shopping(query):
    url = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # We need to find elements that contain prices (₹) and product names
    text = soup.get_text()
    
    # Simple regex to find names nearby prices, or let's try to find elements with ₹ symbol
    price_elements = soup.find_all(string=re.compile(r'₹[0-9,]+'))
    
    print(f"Found {len(price_elements)} price elements")
    
    results = []
    for pe in price_elements:
        parent = pe.parent
        while parent and parent.name not in ['div', 'span']:
            parent = parent.parent
            
        if parent:
            # try to get some context text
            # it usually has the merchant name and product title nearby
            # we'll grab the parent's parent text
            pp = parent.parent.parent
            if pp:
                print("---")
                t = pp.get_text(separator=' | ', strip=True)
                print(t)
                
if __name__ == "__main__":
    search_free_google_shopping("Amul Milk 500ml")
