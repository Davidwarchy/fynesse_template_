from typing import Any, Union
import pandas as pd
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
        if missing_counts.sum() > 0:
            logger.info(f"Found missing values: {missing_counts.to_dict()}")
            print(f"Missing values found: {missing_counts[missing_counts > 0]}")

        # Validate sim_time for gaps (16ms time step)
        df['sim_time'] = pd.to_numeric(df['sim_time'], errors='coerce')
        time_diffs = df['sim_time'].diff()
        expected_step = 0.016  # 16ms in seconds
        missing_timesteps = time_diffs[time_diffs > expected_step * 1.1]  # Allow 10% tolerance
        if not missing_timesteps.empty:
            logger.warning(f"Found {len(missing_timesteps)} potential missing time steps in sim_time")
            print(f"Warning: Detected {len(missing_timesteps)} gaps in sim_time larger than 16ms")

        # Ensure sim_time is in correct format (convert to seconds if needed)
        if df['sim_time'].dtype != np.float64:
            logger.info("Converting sim_time to float64")
            df['sim_time'] = df['sim_time'].astype(np.float64)

        # Validate data types for other columns
        expected_types = {'sensor': 'object'}  # sensor is string
        for col in df.columns:
            if col not in ['sim_time', 'sensor'] and df[col].dtype not in [np.float64, np.int64]:
                logger.warning(f"Column {col} has unexpected type {df[col].dtype}, converting to float64")
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Ensure informative column names (already handled by access.py, but verify)
        if not all(col in df.columns for col in ['sim_time', 'sensor']):
            logger.error("Required columns (sim_time, sensor) missing")
            print("Error: DataFrame missing required columns")
            return None

        # Handle missing values (e.g., forward fill for numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(method='ffill')
        remaining_missing = df[numeric_cols].isnull().sum().sum()
        if remaining_missing > 0:
            logger.info(f"After forward fill, {remaining_missing} missing values remain in numeric columns")
            df[numeric_cols] = df[numeric_cols].fillna(0)  # Final fallback to 0

        # Set index to sim_time for time-series analysis
        df = df.set_index('sim_time', drop=False)
        logger.info("Set sim_time as index for time-series analysis")

        # Log final data summary
        logger.info(f"Data assessment completed. Final shape: {df.shape}")
        print(f"Data assessment completed: {len(df)} rows, {len(df.columns)} columns")
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
        source = ColumnDataSource(data)
        p = figure(title="Sensor Data Time Series", x_axis_label="Time (s)", y_axis_label="Value",
                   x_axis_type="linear", width=800, height=400)

        colors = Category10[10]
        sensors = data['sensor'].unique()
        for i, sensor in enumerate(sensors):
            sensor_data = data[data['sensor'] == sensor]
            source = ColumnDataSource(sensor_data)
            for col in sensor_data.columns:
                if col not in ['sim_time', 'sensor']:
                    p.line(x='sim_time', y=col, source=source, legend_label=f"{sensor}: {col}",
                           color=colors[i % len(colors)])

        p.legend.click_policy = "hide"
        logger.info("Generating Bokeh time series plot")
        show(p)

        # Also display a missing value heatmap using seaborn
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
    Assumes labels could be based on a threshold or derived column (e.g., anomaly detection).

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
        # Example labeling: Label as 1 if any value column exceeds a threshold (e.g., 3 std devs)
        value_cols = [col for col in df_labeled.columns if col not in ['sim_time', 'sensor']]
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