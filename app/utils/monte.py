import random
import math
import time

RISK_FREE_INTEREST = 0.02  # Example value, adjust as needed
TIME = 1  # Total time in years
STEPS_N = 252  # Number of time steps (e.g., trading days)

class MonteCarloSimulation:
    def __init__(self, stock_value, strike, volatility, steps, T):
        self.stock_value = stock_value
        self.risk_free_interest = RISK_FREE_INTEREST 
        self.strike = strike 
        self.sigma = volatility 
        self.delta_time = T / steps 
        self.T = T
        self.steps = steps

    
    def Geometric_Brownian_Motion(self, simulation_id, option_type="call"):
        """
        Simulates one path of stock price movements.

        Args:
            simulation_id (int): Unique identifier for the simulation.
            option_type (str): Type of option ('call' or 'put').

        Returns:
            dict: Contains simulation_id, final_price, payoff, and timestamp.
        """
        ans = []
        st = self.stock_value
        for _ in range(self.steps):
            gaussian = random.gauss(0, 1)
            exponent = ((self.risk_free_interest - 0.5 * self.sigma ** 2) 
                        * self.delta_time + self.sigma * math.sqrt(self.delta_time) * gaussian)
            st *= math.exp(exponent)
            timestamp = time.time()
            ans.append({
                "simulation_id": simulation_id,
                "current_price": st,
                "timestamp": _
            })     
        if option_type.lower() == "call":
            payoff = max(st - self.strike, 0)
        elif option_type.lower() == "put":
            payoff = max(self.strike - st, 0)
        else:
            raise ValueError("Invalid option type. Choose 'call' or 'put'.")
        ans.append({"simulation": simulation_id, "payoff": payoff})
        return ans