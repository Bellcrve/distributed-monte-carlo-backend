from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from app.utils.data_fetcher import fetch_stock_metadata

api_router = APIRouter()

@api_router.get("/stocks/search")
async def search_stock(stock_symbol):
    stock_data = await fetch_stock_metadata(stock_symbol)
    if stock_data:
        return stock_data
    else:
        raise HTTPException(status_code=404, detail="Stock not found")