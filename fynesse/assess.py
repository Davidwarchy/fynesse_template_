from typing import Any, Union
import pandas as pd
pd.set_option("future.no_silent_downcasting", True)
import numpy as np
import logging
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category10
import seaborn as sns
import matplotlib.pyplot as plt

import access

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

"""These are the types of import we might expect in this file
import pandas
import bokeh
import seaborn
import matplotlib.pyplot as plt
import sklearn.decomposition as decomposition
import sklearn.feature_extraction"""

"""Place commands in this file to assess the data you have downloaded.
How are missing values encoded, how are outliers encoded? What do columns represent,
makes rure they are correctly labeled. How is the data indexed. Crete visualisation
routines to assess the data (e.g. in bokeh). Ensure that date formats are correct
and correctly timezoned."""
def fill_missing_per_sensor(df: pd.DataFrame, interval: float = 0.016) -> pd.DataFrame:
    """
    Restore missing sim_time values per sensor at fixed intervals,
    forward filling other values.
    """
    filled_dfs = []

    for sensor, group in df.groupby("sensor"):
        logger.info(f"Processing sensor '{sensor}' with {len(group)} rows")

        group = group.sort_values("sim_time").set_index("sim_time")
        sim_time_min = group.index.min()
        sim_time_max = group.index.max()

        # Generate expected timeline with interval spacing
        expected_times = np.arange(sim_time_min, sim_time_max + interval/2, interval)
        logger.info(
            f"  Sensor '{sensor}': expected {len(expected_times)} intervals "
            f"(from {sim_time_min:.3f}s to {sim_time_max:.3f}s)"
        )

        # Reindex to full timeline
        group_filled = group.reindex(expected_times)

        # Count how many were newly inserted
        inserted = group_filled.isnull().all(axis=1).sum()
        logger.info(f"  Sensor '{sensor}': inserted {inserted} missing rows")

        # Forward fill values
        group_filled = group_filled.ffill().infer_objects(copy=False)

        # Restore sensor column
        group_filled["sensor"] = sensor

        # Reset index so sim_time is a column again
        group_filled = group_filled.reset_index().rename(columns={"index": "sim_time"})
        logger.info(f"  Sensor '{sensor}': final rows = {len(group_filled)}")

        filled_dfs.append(group_filled)

    combined = pd.concat(filled_dfs, ignore_index=True)
    try:
        combined.to_csv("xffilled_data.csv", index=False)
    except Exception as e:
        logger.error(f"Error saving filled data: {e}")
    logger.info(f"All sensors combined: {len(combined)} rows total")
    return combined


def data(folder: str = "data") -> Union[pd.DataFrame, Any]:
    """
    Load the data from access and ensure missing values are correctly encoded, indices are correct,
    column names are informative, and date/times are correctly formatted.

    Returns:
        pd.DataFrame or None: Cleaned DataFrame or None on error.
    """
    """
    Load the data from access and ensure missing values are correctly encoded as well as
    indices correct, column names informative, date and times correctly formatted.
    Return a structured data structure such as a data frame.

    IMPLEMENTATION GUIDE FOR STUDENTS:
    ==================================

    1. REPLACE THIS FUNCTION WITH YOUR DATA ASSESSMENT CODE:
       - Load data using the access module
       - Check for missing values and handle them appropriately
       - Validate data types and formats
       - Clean and prepare data for analysis

    2. ADD ERROR HANDLING:
       - Handle cases where access.data() returns None
       - Check for data quality issues
       - Validate data structure and content

    3. ADD BASIC LOGGING:
       - Log data quality issues found
       - Log cleaning operations performed
       - Log final data summary

    4. EXAMPLE IMPLEMENTATION:
       df = access.data()
       if df is None:
           print("Error: No data available from access module")
           return None

       print(f"Assessing data quality for {len(df)} rows...")
       # Your data assessment code here
       return df
    """
    logger.info("Starting data assessment")

    # Load data from access module
    df = access.data(folder)
    if df is None:
        logger.error("No data available from access module")
        print("Error: Could not load data from access module")
        return None

    logger.info(f"Assessing data quality for {len(df)} rows, {len(df.columns)} columns")

    try:
        # Check for missing values
        missing_counts = df.isnull().sum()
        total_missing = missing_counts.sum()
        if total_missing > 0:
            logger.info(f"Found {total_missing} missing values: {missing_counts[missing_counts > 0].to_dict()}")
            print(f"Missing values found: {total_missing} total\n{missing_counts[missing_counts > 0]}")

        # Ensure sim_time is numeric
        df["sim_time"] = pd.to_numeric(df["sim_time"], errors="coerce")
        if df["sim_time"].isnull().any():
            logger.warning(f"Found {df['sim_time'].isnull().sum()} missing sim_time values")
            print(f"Warning: Found {df['sim_time'].isnull().sum()} missing sim_time values")

        # Fill missing values per sensor
        logger.info("Restoring missing values per sensor with 16ms intervals + forward fill")
        df = fill_missing_per_sensor(df)

        # Fill non-numeric columns (e.g., sensor already handled, others get placeholder)
        if "sensor" in df.columns:
            df["sensor"] = df["sensor"].fillna("unknown")
            logger.info("Filled missing sensor values with 'unknown'")

        # Validate data types
        for col in df.columns:
            if col not in ["sim_time", "sensor"] and df[col].dtype not in [np.float64, np.int64]:
                logger.warning(f"Column {col} has unexpected type {df[col].dtype}, converting to float64")
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Set sim_time as index for time-series analysis
        df = df.set_index("sim_time", drop=False)
        logger.info("Set sim_time as index for time-series analysis")

        # Log final data summary
        logger.info(f"Data assessment completed. Final shape: {df.shape}")
        print(f"Data assessment completed: {len(df)} rows, {len(df.columns)} columns")

        print("Data assessment test completed.")

        print("="*180)

        return df

    except Exception as e:
        logger.error(f"Error during data assessment: {e}")
        print(f"Error assessing data: {e}")
        return None

def query(data: Union[pd.DataFrame, Any]) -> str:
    """
    Request user input to explore specific aspects of the data.

    Args:
        data: Input DataFrame from data() function.

    Returns:
        str: String describing the query result or error message.
    """
    if data is None or not isinstance(data, pd.DataFrame):
        logger.error("Invalid or no data provided for query")
        return "Error: No valid data provided for query"

    try:
        print("\nAvailable sensors:", data['sensor'].unique())
        sensor = input("Enter sensor name to query (or 'all' for all sensors): ").strip()
        time_start = float(input("Enter start time (seconds, or 0 for no limit): "))
        time_end = float(input("Enter end time (seconds, or -1 for no limit): "))

        # Filter data based on user input
        query_df = data
        if sensor.lower() != 'all':
            query_df = query_df[query_df['sensor'] == sensor]
        if time_start > 0:
            query_df = query_df[query_df.index >= time_start]
        if time_end >= 0:
            query_df = query_df[query_df.index <= time_end]

        if query_df.empty:
            logger.warning("Query returned no data")
            return "No data matches the query criteria"

        result = f"Query result: {len(query_df)} rows for sensor '{sensor}' from {time_start} to {time_end} seconds"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f"Error processing query: {e}"

def view(data: Union[pd.DataFrame, Any]) -> None:
    """
    Provide a Bokeh visualization to verify data quality (e.g., time series plot).

    Args:
        data: Input DataFrame from data() function.
    """
    if data is None or not isinstance(data, pd.DataFrame):
        logger.error("Invalid or no data provided for visualization")
        print("Error: No valid data provided for visualization")
        return

    try:
        # Create a Bokeh time series plot for each sensor
        p = figure(title="Sensor Data Time Series", x_axis_label="Time (s)", y_axis_label="Value",
                   x_axis_type="linear", width=800, height=400)

        colors = Category10[10]
        sensors = data['sensor'].unique()
        for i, sensor in enumerate(sensors):
            sensor_data = data[data['sensor'] == sensor].copy()
            # source = ColumnDataSource(sensor_data)
            source = ColumnDataSource(sensor_data.reset_index().rename(columns={'sim_time': 'sim_time_index'}))


            for col in sensor_data.columns:
                if col not in ['sim_time', 'sensor']:
                    p.line(x='sim_time', y=col, source=source, legend_label=f"{sensor}: {col}",
                           color=colors[i % len(colors)])

        p.legend.click_policy = "hide"
        logger.info("Generating Bokeh time series plot")
        show(p)

        # Display a missing value heatmap using seaborn
        plt.figure(figsize=(10, 6))
        sns.heatmap(data.drop(columns=['sensor']).isnull(), cbar=False, cmap='viridis')
        plt.title("Missing Values Heatmap")
        plt.xlabel("Columns")
        plt.ylabel("Rows")
        plt.show()
        logger.info("Generated missing values heatmap")

    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        print(f"Error generating visualization: {e}")

def labelled(data: Union[pd.DataFrame, Any]) -> Union[pd.DataFrame, Any]:
    """
    Provide a labelled set of data ready for supervised learning.
    Labels based on threshold (3 std devs) for anomaly detection.

    Args:
        data: Input DataFrame from data() function.

    Returns:
        pd.DataFrame or None: DataFrame with a 'label' column or None on error.
    """
    if data is None or not isinstance(data, pd.DataFrame):
        logger.error("Invalid or no data provided for labeling")
        print("Error: No valid data provided for labeling")
        return None

    try:
        df_labeled = data.copy()
        value_cols = [col for col in df_labeled.columns if col not in ['sim_time', 'sensor', 'label']]
        if not value_cols:
            logger.error("No value columns available for labeling")
            print("Error: No value columns available for labeling")
            return None

        # Compute threshold based on standard deviation
        thresholds = df_labeled[value_cols].mean() + 3 * df_labeled[value_cols].std()
        df_labeled['label'] = 0
        for col in value_cols:
            df_labeled.loc[df_labeled[col] > thresholds[col], 'label'] = 1

        logger.info(f"Generated labels: {df_labeled['label'].value_counts().to_dict()}")
        print(f"Label distribution:\n{df_labeled['label'].value_counts()}")

        return df_labeled

    except Exception as e:
        logger.error(f"Error generating labeled data: {e}")
        print(f"Error generating labeled data: {e}")
        return None

if __name__ == "__main__":
    folder = "data/noiseless/2025-09-17-095442"
    df = data(folder)
    if df is not None:
        print("\nData Head:\n", df.head())
        print(query(df))
        view(df)
        df_labeled = labelled(df)
        if df_labeled is not None:
            print("\nLabeled Data Head:\n", df_labeled.head())