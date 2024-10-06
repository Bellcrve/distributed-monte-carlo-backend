import os
import httpx
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from constants import POLYGON_API_KEY
from datetime import datetime,timedelta



async def fetch_stock_metadata(symbol: str):
    if not POLYGON_API_KEY:
        raise ValueError("No API key found")

    # Get yesterday's date and format it to yyyy-mm-dd 
    # TODO: FIX the date
    yesterday_date = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    api_url = f'https://api.polygon.io/v3/reference/tickers/{symbol}'
    ticker_price_url = f'https://api.polygon.io/v1/open-close/{symbol}/{yesterday_date}'
    
    params = {
        'apiKey': POLYGON_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        price_response = await client.get(ticker_price_url, params=params)
        if response.status_code == 200 and price_response.status_code == 200:
            filter_data = ['ticker', 'name', 'currency_name', 'market_cap', 'currency_name', 'homepage_url'] 
            data = response.json()
            price_data = price_response.json()

            metadata = {key: data["results"][key] for key in filter_data}
            metadata['price'] = price_data['close']
            return metadata
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
