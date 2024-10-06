from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import random

web_router = APIRouter()

@web_router.websocket("/ws/simulate")
async def websocket_simulation(websocket: WebSocket):
    await websocket.accept()
    try:
        for time_interval in range(100):  
            # Get price prediction
            data_point = get_price_prediction(time_interval)
            # Send data to the client
            await websocket.send_json(data_point)
            # Simulate delay between data points
            await asyncio.sleep(0)  
        # After sending all data, close the connection
        await websocket.close()
        print("WebSocket connection closed after sending all data.")
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

def get_price_prediction(time_interval: int):
    # Simulate a price prediction
    return {
        "time": time_interval,
        "price": random.uniform(100, 200)
    }