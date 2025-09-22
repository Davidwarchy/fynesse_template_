"""
Author: David Warutumo
Description: Convert pickle sensor data to CSV format. Add realistic noise for real-to-sim gap simulation.
"""
import os
import pickle
import csv
import json
import numpy as np
from scipy import signal

def pickle_to_csv(pickle_file, csv_file, shape, noisy=False, noise_params=None):
    """
    Convert a pickle file containing (sim_time, sensor_values) tuples to CSV.
    If noisy=True, add imperfections to simulate real-world data.
    """
    if not os.path.exists(pickle_file):
        print(f"Warning: {pickle_file} not found.")
        return

    try:
        with open(pickle_file, "rb") as f:
            data = pickle.load(f)

        if not data:
            print(f"Warning: No data in {pickle_file}")
            return

        # Ensure destination folder exists
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)

        # Prepare data for CSV
        processed_data = []
        noise_summary = {"gaussian_std": False, "missing_prob": False, "latency_rate": False, "jitter_amplitude": False}

        for sim_time, sensor_values in data:
            if isinstance(sensor_values, (list, tuple, np.ndarray)):
                values = np.array(sensor_values).flatten()
            else:
                values = np.array([sensor_values])

            if noisy and noise_params:
                # Add Gaussian noise
                if noise_params.get("gaussian_std", 0) > 0:
                    noise = np.random.normal(0, noise_params["gaussian_std"], values.shape)
                    values = values + noise
                    noise_summary["gaussian_std"] = True

                # Simulate missing data
                if noise_params.get("missing_prob", 0) > 0 and np.random.random() < noise_params["missing_prob"]:
                    noise_summary["missing_prob"] = True
                    continue  # Skip this row

                # Simulate latency (subsample data to mimic slower sensor rates)
                if noise_params.get("latency_rate", 1) > 1 and len(processed_data) % noise_params["latency_rate"] != 0:
                    noise_summary["latency_rate"] = True
                    continue  # Skip to simulate lower sampling rate

                # Add jitter (high-frequency oscillation)
                if noise_params.get("jitter_amplitude", 0) > 0:
                    jitter = noise_params["jitter_amplitude"] * np.sin(2 * np.pi * noise_params["jitter_freq"] * sim_time)
                    values = values + jitter
                    noise_summary["jitter_amplitude"] = True
                    noise_summary["jitter_freq"] = noise_params["jitter_freq"]

            row = [sim_time] + list(values)
            processed_data.append(row)

        # Write to CSV
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Build header
            if shape is None or shape == [1]:
                header = ["sim_time", "value"]
            else:
                flat_size = int(np.prod(shape))
                header = ["sim_time"] + [f"value_{i}" for i in range(flat_size)]
            writer.writerow(header)
            writer.writerows(processed_data)

        print(f"Converted {pickle_file} -> {csv_file}")
        if noisy:
            print(f"Noise applied to {csv_file}:")
            for noise_type, applied in noise_summary.items():
                if applied:
                    print(f" - {noise_type}: {noise_params.get(noise_type, 'N/A')}")

    except Exception as e:
        print(f"Error processing {pickle_file}: {e}")

def convert_all(src_base, dst_base, noisy_base, sensors_json):
    """
    Convert all eligible sensor pickle files in src_base to CSV files in dst_base (noiseless)
    and noisy_base (noisy) using sensors.json metadata.
    """
    with open(sensors_json, "r") as f:
        sensors = json.load(f)

    # Noise parameters
    noise_params = {
        "gaussian_std": 0.1,  # Standard deviation for Gaussian noise
        "missing_prob": 0.05,  # Probability of dropping a data point
        "latency_rate": 2,     # Simulate sensor sampling every 2nd point
        "jitter_amplitude": 0.05,  # Amplitude of jitter oscillation
        "jitter_freq": 10.0   # Frequency of jitter in Hz
    }

    for sensor in sensors:
        if not sensor.get("can_csv", False):
            continue

        sensor_name = sensor["name"]
        shape = sensor.get("shape", None)

        pickle_file = os.path.join(src_base, f"{sensor_name}.pkl")
        csv_file_noiseless = os.path.join(dst_base, f"{sensor_name}.csv")
        csv_file_noisy = os.path.join(noisy_base, f"{sensor_name}.csv")

        # Save noiseless data
        pickle_to_csv(pickle_file, csv_file_noiseless, shape, noisy=False)

        # Save noisy data
        pickle_to_csv(pickle_file, csv_file_noisy, shape, noisy=True, noise_params=noise_params)

if __name__ == "__main__":
    # Specify manually
    timestamp = "2025-09-22-151649"
    src_base = f"robot/controllers/drive_robot/data/{timestamp}"
    dst_base = f"data/noiseless/{timestamp}"
    noisy_base = f"data/noisy/{timestamp}"
    sensors_json = "robot/controllers/drive_robot/sensors.json"

    convert_all(src_base, dst_base, noisy_base, sensors_json)