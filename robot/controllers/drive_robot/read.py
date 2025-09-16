import pickle
import os
import argparse
from datetime import datetime

def read_pickle_data(pickle_file, n):
    """
    Read the first n elements from a pickle file and print them.
    
    Args:
        pickle_file (str): Path to the pickle file
        n (int): Number of elements to print
    """
    if not os.path.exists(pickle_file):
        print(f"Error: Pickle file '{pickle_file}' does not exist.")
        return
    
    try:
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        
        # Ensure n does not exceed the length of data
        n = min(n, len(data))
        
        if n == 0:
            print("No data available in the pickle file.")
            return
        
        print(f"Printing first {n} accelerometer readings:")
        print("Simulation Time | X | Y | Z")
        print("-" * 35)
        for i in range(n):
            sim_time, accel_values = data[i]
            print(f"{sim_time:.3f} s | {accel_values[0]:.3f} | {accel_values[1]:.3f} | {accel_values[2]:.3f}")
    
    except Exception as e:
        print(f"Error reading pickle file: {e}")

if __name__ == "__main__":
    # Construct the pickle file path
    pickle_file = "robot/controllers/drive_robot/data/2025-09-16-102202/accelerometer.pkl"
    n_readings = 10 
    
    # Read and print the first n elements
    read_pickle_data(pickle_file, n_readings)