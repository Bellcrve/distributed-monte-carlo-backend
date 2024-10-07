import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse

def load_simulation_data(workers, num_simulations_to_plot=300):
    """
    Loads simulation data from JSON files for a given number of workers.

    Args:
        workers (int): Number of workers used in simulations.
        num_simulations_to_plot (int): Number of simulation paths to plot.

    Returns:
        list of list of dict: A list containing simulation data for each simulation.
    """
    results_file = f"simulation_results/results_workers_{workers}.json"
    
    if not os.path.exists(results_file):
        print(f"Results file {results_file} not found.")
        return []
    
    with open(results_file, 'r') as f:
        all_data = json.load(f)
    
    # Organize data by simulation_id
    simulations = {}
    for entry in all_data:
        sim_id = entry["simulation_id"]
        if sim_id not in simulations:
            simulations[sim_id] = []
        simulations[sim_id].append(entry)
    
    # Select a subset of simulations to plot
    selected_sim_ids = list(simulations.keys())[:num_simulations_to_plot]
    selected_simulations = [simulations[sim_id] for sim_id in selected_sim_ids]
    
    return selected_simulations

def load_summary_data(workers):
    """
    Loads summary data from JSON files for a given number of workers.

    Args:
        workers (int): Number of workers used in simulations.

    Returns:
        dict: Summary data.
    """
    summary_file = f"simulation_results/summary_workers_{workers}.json"
    
    if not os.path.exists(summary_file):
        print(f"Summary file {summary_file} not found.")
        return {}
    
    with open(summary_file, 'r') as f:
        summaries = json.load(f)
    
    if summaries:
        return summaries[0]  # Assuming one summary per file
    else:
        return {}

def plot_simulations(simulations_by_workers, summary_by_workers):
    """
    Plots Time (X), Stock Price (Y), and Execution Time (Z) for different worker counts in 3D.

    Args:
        simulations_by_workers (dict): A dictionary containing simulation data for different worker counts.
        summary_by_workers (dict): A dictionary containing summary data for different worker counts.
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')  # 3D plot

    colors = {2: 'red', 4: 'green', 8: 'blue'}  # Different colors for different worker counts

    # Plot simulations (X-axis: time step, Y-axis: stock price, Z-axis: execution time)
    for workers, simulations in simulations_by_workers.items():
        execution_time = summary_by_workers[workers]['execution_time_seconds']
        
        for sim_data in simulations:
            timestamps = [entry["timestamp"] for entry in sim_data if "current_price" in entry]
            prices = [entry["current_price"] for entry in sim_data if "current_price" in entry]
            sim_id = sim_data[0]["simulation_id"]
            
            # Z-axis: Set execution time as a constant for all points in this simulation
            z = [execution_time] * len(timestamps)
            
            ax.plot(timestamps, prices, z, color=colors[workers], alpha=0.7)

    # Set axis labels and title
    ax.set_xlabel("Time Step (X)")
    ax.set_ylabel("Stock Price (Y)")
    ax.set_zlabel("Execution Time (Z)")
    ax.set_title(f"Time Steps, Stock Price, and Execution Time for 2, 4, and 8 Workers")

    # Create custom legend for worker counts (using dummy plots)
    worker_labels = [plt.Line2D([0], [0], color=colors[workers], lw=4) for workers in [2, 4, 8]]
    ax.legend(worker_labels, ['2 Workers (Red)', '4 Workers (Green)', '8 Workers (Blue)'], loc='upper left', bbox_to_anchor=(1, 1))

    plt.tight_layout()

    # Save the plot
    plt.savefig(f"simulation_results/comparison_plot_workers_3D.png")
    plt.show()
    print(f"3D comparison plot saved as simulation_results/comparison_plot_workers_3D.png")

def main():
    parser = argparse.ArgumentParser(description="Plot simulation results for 2, 4, and 8 workers in 3D.")
    parser.add_argument('--num_simulations', type=int, default=50, help='Number of simulations to plot for each worker count.')
    args = parser.parse_args()

    num_simulations_to_plot = args.num_simulations

    worker_counts = [2, 4, 8]  # Workers to compare
    simulations_by_workers = {}
    summary_by_workers = {}

    # Load data for each worker count
    for workers in worker_counts:
        simulations = load_simulation_data(workers, num_simulations_to_plot)
        summary = load_summary_data(workers)
        if simulations and summary:
            simulations_by_workers[workers] = simulations
            summary_by_workers[workers] = summary
        else:
            print(f"Insufficient data to plot for {workers} workers.")
    
    # Plot all the data
    if simulations_by_workers and summary_by_workers:
        plot_simulations(simulations_by_workers, summary_by_workers)
    else:
        print("No sufficient data for plotting.")

if __name__ == "__main__":
    main()
