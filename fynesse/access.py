from typing import Union
import pandas as pd
import logging
import os
import json
import numpy as np

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def data(folder: str = "data", sample_fraction: float = 0.8) -> Union[pd.DataFrame, None]:
    """
    Read the data from a folder (default = "data"), returning a structured format such as a DataFrame.
    If sensor is specified, loads data for that sensor only. If sensor is None or empty, combines data
    from all CSV-convertible sensors listed in sensors.json in a sparse wide format with a sensor column.
    Randomly drops rows for each sensor type before combining, based on the sample_fraction.

    IMPLEMENTATION GUIDE
    ====================

    1. LOAD DATA:
       - Loads sensors.json from robot/controllers/drive_robot/sensors.json.
       - If sensor is specified, loads only that sensor's data.csv.
       - If sensor is None or empty, loads and combines data from all CSV-convertible sensors.
       - Folder defaults to "data".
       - Dynamically creates a unified column set from csv_columns in sensors.json.
       - Randomly samples rows for each sensor's data based on sample_fraction.

    2. ERROR HANDLING:
       - Missing folder → log + return None
       - Missing file → log + return None
       - Other unexpected errors → log + return None

    3. LOGGING:
       - Logs when data loading starts
       - Logs success with row/column summary
       - Logs detailed error messages

    Args:
        folder (str, optional): Path to folder containing sensor data CSVs. Defaults to "data".
        sample_fraction (float, optional): Fraction of rows to keep for each sensor (0.0 to 1.0). Defaults to 0.8.

    Returns:
        pd.DataFrame or None: DataFrame in sparse wide format with sensor column or None on error.
    """
    logger.info(f"Starting data access operation in folder: {folder}")

    # Validate sample_fraction
    if not 0.0 <= sample_fraction <= 1.0:
        logger.error(f"Invalid sample_fraction: {sample_fraction}. Must be between 0.0 and 1.0.")
        print(f"Error: Invalid sample_fraction -> {sample_fraction}. Must be between 0.0 and 1.0.")
        return None

    # Ensure folder exists
    if not os.path.exists(folder):
        logger.error(f"Folder not found: {folder}")
        print(f"Error: Folder not found -> {folder}")
        return None

    # Load sensors.json
    sensors_file = os.path.join("robot", "controllers", "drive_robot", "sensors.json")
    try:
        with open(sensors_file, 'r') as f:
            sensors_config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Sensors configuration file not found: {sensors_file}")
        print(f"Error: Could not find sensors.json -> {sensors_file}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing sensors.json: {e}")
        print(f"Error parsing sensors.json: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading sensors.json: {e}")
        print(f"Error loading sensors.json: {e}")
        return None

    # Filter sensors that can be converted to CSV
    csv_sensors = [s for s in sensors_config if s.get("can_csv", False)]

    # Dynamically create unified column set from csv_columns
    all_columns = set()
    for sensor in csv_sensors:
        all_columns.update(sensor["csv_columns"])
    all_columns = list(all_columns) + ["sensor"]

    # If no sensor specified, combine data from all CSV-convertible sensors
    dataframes = []
    for s in csv_sensors:
        sensor_name = s["name"]
        file_path = os.path.join(folder, f"{sensor_name}.csv")
        try:
            logger.info(f"Loading data from {file_path}")
            df = pd.read_csv(file_path)

            if df.empty:
                logger.warning(f"Loaded file is empty: {file_path}")
                print(f"Warning: The file {file_path} is empty.")
                continue

            # Randomly sample rows
            if sample_fraction < 1.0:
                original_rows = len(df)
                df = df.sample(frac=sample_fraction, random_state=np.random.randint(0, 10000))
                logger.info(f"Sampled {len(df)} rows from {original_rows} for {sensor_name} (fraction: {sample_fraction})")

            # Map sensor-specific columns to unified columns
            column_mapping = {
                f"value_{i}": name for i, name in enumerate(s["csv_columns"])
            }
            column_mapping["sim_time"] = "sim_time"  # keep time as is

            df = df.rename(columns=column_mapping)

            # Add sensor column
            df["sensor"] = sensor_name

            # Ensure all unified columns are present, fill with NaN where needed
            for col in all_columns:
                if col not in df.columns:
                    df[col] = pd.NA

            dataframes.append(df)
            logger.info(
                f"Successfully loaded data for {sensor_name}: {len(df)} rows, {len(df.columns)} columns"
            )

        except FileNotFoundError:
            logger.error(f"Data file not found: {file_path}")
            print(f"Error: Could not find file -> {file_path}")
            continue
        except PermissionError:
            logger.error(f"Permission denied when accessing: {file_path}")
            print(f"Error: Permission denied -> {file_path}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            print(f"Error loading data from {file_path}: {e}")
            continue

    if not dataframes:
        logger.error("No valid data loaded from any sensor")
        print("Error: No valid data loaded from any sensor")
        return None

    # Combine all DataFrames
    try:
        combined_df = pd.concat(dataframes, ignore_index=True)
        logger.info(
            f"Successfully combined data: {len(combined_df)} rows, {len(combined_df.columns)} columns"
        )

        # Try save to csv for inspection
        try:
            combined_df.to_csv('x.csv')
        except Exception as e:
            logger.error(f"Error saving combined DataFrame to CSV: {e}")
            print(f"Error saving combined DataFrame to CSV: {e}")

        return combined_df

    except Exception as e:
        logger.error(f"Error combining DataFrames: {e}")
        print(f"Error combining DataFrames: {e}")
        return None


if __name__ == "__main__":
    # Test the data access function
    dir = "data/noiseless/2025-09-17-095442"

    # Test with all sensors and default sampling fraction (80%)
    df_all = data(dir, sample_fraction=0.8)
    if df_all is not None:
        print("\nCombined DataFrame for all sensors (after random sampling):")
        print(df_all.head())