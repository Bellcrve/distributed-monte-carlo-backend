from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import random
import os
import sys
import math
import time
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from dask.distributed import Client, as_completed

web_router = APIRouter()

dask_client = Client('147.182.254.237:8786') 



def Geometric_Brownian_Motion(stock_value, strike, volatility, steps, T, simulation_id, option_type="call"):
    """
    Simulates one path of stock price movements.

    Args:
        simulation_id (int): Unique identifier for the simulation.
        option_type (str): Type of option ('call' or 'put').

    Returns:
        dict: Contains simulation_id, final_price, payoff, and timestamp.
    """
    delta_time = T / steps 
    risk_free_interest = 0.02
    sigma = volatility
    ans = []
    st = stock_value
    for _ in range(steps):
        gaussian = random.gauss(0, 1)
        exponent = ((risk_free_interest - 0.5 * sigma ** 2) 
                    * delta_time + sigma * math.sqrt(delta_time) * gaussian)
        st *= math.exp(exponent)
        timestamp = time.time()
        ans.append({
            "simulation_id": simulation_id,
            "current_price": st,
            "timestamp": _
        })     
    if option_type.lower() == "call":
        payoff = max(st - strike, 0)
    elif option_type.lower() == "put":
        payoff = max(strike - st, 0)
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'.")
    ans.append({"simulation": simulation_id, "payoff": payoff})
    return ans




@web_router.websocket("/ws/simulate")
async def websocket_simulation(websocket: WebSocket):
    await websocket.accept()
    try:
        # data = await websocket.receive_json()
        # stock_value = data.get("stock_value")
        # strike = data.get("strike")
        # volatility = data.get("volatility")
        # steps = data.get("steps")
        # simulations = data.get("simulations")
        simulations = 10000
        # option_type = data.get("option_type", "call")  # Default to 'call'
        option_type = "call"
        # T = data.get("T", 1) 
        
        # monte = MonteCarloSimulation(100, 100, 0.2 ,200, 1)

        # Submit simulation tasks to Dask
        payoffs = []
        futures = []
        for sim_id in range(1, simulations + 1):
            future = dask_client.submit(Geometric_Brownian_Motion, 100, 105, 0.2, 350, 1, sim_id, option_type)
            futures.append(future)

        # Process completed futures as they finish
        async for completed_future in as_completed(futures):
            try:
                result = await completed_future  # Await the future result
                payoff = result[-1]['payoff']  # Get the payoff from the last element
                payoffs.append(payoff)
                
                # Send intermediate results to frontend (without payoff)
                await websocket.send_json(result[:-1])
            except Exception as e:
                print(f"Error in simulation {completed_future}: {e}")

        average_payoff = sum(payoffs) / len(payoffs) if payoffs else 0

        # Send the summary to the frontend
        await websocket.send_json({
            "message": "All simulations completed.",
            "average_payoff": average_payoff
        })
        # After sending all data, close the connection
        await websocket.close()
        print("WebSocket connection closed after sending all data.")
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

