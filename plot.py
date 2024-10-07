import os
import sys
import math
import time
import json
from datetime import datetime
import random
from dask.distributed import Client, as_completed

# Initialize Dask client
# Replace '147.182.254.237:8786' with your actual Dask scheduler address
dask_client = Client('147.182.254.237:8786') 

def Geometric_Brownian_Motion(stock_value, strike, volatility, steps, T, simulation_id, option_type="call"):
    """
    Simulates one path of stock price movements.

    Args:
        stock_value (float): Initial stock price.
        strike (float): Strike price of the option.
        volatility (float): Volatility of the stock.
        steps (int): Number of time steps.
        T (float): Time to expiration in years.
        simulation_id (int): Unique identifier for the simulation.
        option_type (str): Type of option ('call' or 'put').

    Returns:
        list of dict: Contains simulation_id, current_price, timestamp, and payoff.
    """
    delta_time = T / steps 
    risk_free_interest = 0.02
    sigma = volatility
    ans = []
    st = stock_value
    for step in range(steps):
        gaussian = random.gauss(0, 1)
        exponent = ((risk_free_interest - 0.5 * sigma ** 2) 
                    * delta_time + sigma * math.sqrt(delta_time) * gaussian)
        st *= math.exp(exponent)
        timestamp = step  # Using step number as timestamp for clarity
        ans.append({
            "simulation_id": simulation_id,
            "current_price": st,
            "timestamp": step
        })     
    if option_type.lower() == "call":
        payoff = max(st - strike, 0)
    elif option_type.lower() == "put":
        payoff = max(strike - st, 0)
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'.")
    ans.append({
        "simulation_id": simulation_id,
        "payoff": payoff,
        "final_price": st,
        "timestamp": time.time()
    })
    return ans

def Geometric_Brownian_Motion_Batch(stock_value, strike, volatility, steps, T, batch_size, start_sim_id, option_type="call"):
    """
    Runs a batch of simulations in a single task.

    Args:
        stock_value (float): Initial stock price.
        strike (float): Strike price of the option.
        volatility (float): Volatility of the stock.
        steps (int): Number of time steps.
        T (float): Time to expiration in years.
        batch_size (int): Number of simulations in this batch.
        start_sim_id (int): Starting simulation ID for this batch.
        option_type (str): Type of option ('call' or 'put').

    Returns:
        list of dict: Contains results for all simulations in the batch.
    """
    all_simulations = []
    for sim_id in range(start_sim_id, start_sim_id + batch_size):
        simulation_result = Geometric_Brownian_Motion(stock_value, strike, volatility, steps, T, sim_id, option_type)
        all_simulations.extend(simulation_result)
    return all_simulations

def run_simulations(stock_value=100, strike=103, volatility=0.3, steps=144, T=1, simulations=1000, batch_size=100, option_type="call", workers=4):
    """
    Runs Monte Carlo simulations using Dask with batched tasks.

    Args:
        stock_value (float): Initial stock price.
        strike (float): Strike price of the option.
        volatility (float): Volatility of the stock.
        steps (int): Number of time steps.
        T (float): Time to expiration in years.
        simulations (int): Total number of simulations to run.
        batch_size (int): Number of simulations per task.
        option_type (str): Type of option ('call' or 'put').
        workers (int): Number of workers to utilize.
    """
    print(f"Starting simulations with {workers} workers, batch size {batch_size}...")
    payoffs = []
    all_simulations = []
    futures = []
    
    start_time = time.time()
    
    # Submit batched tasks instead of individual tasks
    for batch_start in range(0, simulations, batch_size):
        future = dask_client.submit(
            Geometric_Brownian_Motion_Batch,
            stock_value,
            strike,
            volatility,
            steps,
            T,
            batch_size,
            batch_start + 1,
            option_type
        )
        futures.append(future)
    
    # Process completed futures as they finish using `as_completed`
    for completed_future in as_completed(futures):
        try:
            result = completed_future.result()  # Get the result from the completed future
            for entry in result:
                if 'payoff' in entry:
                    payoffs.append(entry['payoff'])
            all_simulations.extend(result)
            print(f"Batch completed with {len(result)} results.")
        except Exception as e:
            print(f"Error in batch {completed_future}: {e}")
    
    average_payoff = sum(payoffs) / len(payoffs) if payoffs else 0
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Prepare summary
    summary = {
        "message": "All simulations completed.",
        "average_payoff": average_payoff,
        "total_simulations": simulations,
        "execution_time_seconds": execution_time,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(summary)
    
    # Store simulation results
    store_results(all_simulations, summary, workers)
    
def store_results(simulation_data, summary_data, workers):
    """
    Stores simulation results and summary to JSON files.

    Args:
        simulation_data (list of dict): The simulation data to store.
        summary_data (dict): The summary data to store.
        workers (int): Number of workers used.
    """
    # Create a directory to store results if it doesn't exist
    os.makedirs('simulation_results', exist_ok=True)
    
    # Define file paths
    results_file = f"simulation_results/results_workers_{workers}.json"
    summary_file = f"simulation_results/summary_workers_{workers}.json"
    
    # Write simulation data
    with open(results_file, 'w') as f:
        json.dump(simulation_data, f, indent=4)
    print(f"Simulation data stored in {results_file}")
    
    # Write summary data
    with open(summary_file, 'w') as f:
        json.dump([summary_data], f, indent=4)
    print(f"Summary data stored in {summary_file}")

if __name__ == "__main__":
    # Run simulations with 4 workers and 100 simulations per task
    run_simulations(
        stock_value=100, 
        strike=103, 
        volatility=0.3, 
        steps=72, 
        T=1, 
        simulations=6400, 
        batch_size=400,  # Batch size determines the number of simulations per task
        option_type="call", 
        workers=8
    )
