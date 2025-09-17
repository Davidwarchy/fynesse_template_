import pickle
import os
import argparse
from datetime import datetime
import numpy as np

def read_pickle_data(pickle_file, n):
    """
    Read the first n elements from a pickle file and print them, handling variable number of columns.
    
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
        
        # Determine the number of columns dynamically
        first_data = data[0][1]  # Access the sensor data part of the first tuple
        num_columns = len(first_data) if isinstance(first_data, (list, tuple, np.ndarray)) else 1
        
        # Create header based on number of columns
        if num_columns == 1:
            header = "Simulation Time | Value"
            column_names = ["Value"]
        else:
            header = "Simulation Time | " + " | ".join(f"Col_{i+1}" for i in range(num_columns))
            column_names = [f"Col_{i+1}" for i in range(num_columns)]
        
        print(f"Printing first {n} readings from {os.path.basename(pickle_file)}:")
        print(header)
        print("-" * (len(header) + 10))
        
        for i in range(n):
            sim_time, sensor_values = data[i]
            if num_columns == 1:
                print(f"{sim_time:.3f} s | {sensor_values:.3f}")
            else:
                values = [f"{val:.3f}" for val in sensor_values]
                print(f"{sim_time:.3f} s | {' | '.join(values)}")
    
    except Exception as e:
        print(f"Error reading pickle file: {e}")

if __name__ == "__main__":
    # Construct the pickle file path
    pickle_file = "robot/controllers/drive_robot/data/2025-09-17-095442/actuator.pkl"
    n_readings = 10 
    
    # Read and print the first n elements
    read_pickle_data(pickle_file, n_readings)