import os
import httpx
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from constants import POLYGON_API_KEY


async def fetch_stock_metadata(symbol: str):
    if not POLYGON_API_KEY:
        raise ValueError("No API key found")
    
    api_url = f'https://api.polygon.io/v3/reference/tickers/{symbol}'
    
    params = {
        'apiKey': POLYGON_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        if response.status_code == 200:
            filter_data = ['ticker', 'name', 'currency_name', 'market_cap', 'currency_name', 'homepage_url'] 
            data = response.json()
            return {key: data["results"][key] for key in filter_data}
        else:
            print(f'Error fetching data: {response.text}')
            return None
        
# Example usage
async def main():
    symbol = 'AAPL'
    data = await fetch_stock_metadata(symbol)
    if data:
        print(data)
    else:
        print('Failed to fetch stock metadata.')
