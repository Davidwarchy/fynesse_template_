"""
Access module for the fynesse framework.

This module handles data access functionality including:
- Data loading from various sources (web, local files, databases)
- Legal compliance (intellectual property, privacy rights)
- Ethical considerations for data usage
- Error handling for access issues

Legal and ethical considerations are paramount in data access.
Ensure compliance with e.g. GDPR, intellectual property laws, and ethical guidelines.

Best Practice on Implementation
===============================

1. BASIC ERROR HANDLING:
   - Use try/except blocks to catch common errors
   - Provide helpful error messages for debugging
   - Log important events for troubleshooting

2. WHERE TO ADD ERROR HANDLING:
   - File not found errors when loading data
   - Network errors when downloading from web
   - Permission errors when accessing files
   - Data format errors when parsing files

3. SIMPLE LOGGING:
   - Use logging for structured logs
   - Log when operations start and complete
   - Log errors with context information
   - Log data summary information

4. EXAMPLE PATTERNS:
   
   Basic error handling:
   try:
       df = pd.read_csv('data.csv')
   except FileNotFoundError:
       print("Error: Could not find data.csv file")
       return None
   
   With logging:
   logger.info("Loading data from data.csv...")
   try:
       df = pd.read_csv('data.csv')
       logger.info(f"Successfully loaded {len(df)} rows of data")
       return df
   except FileNotFoundError:
       logger.error("Error: Could not find data.csv file")
       return None
"""

from typing import Union
import pandas as pd
import logging
import os

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def data(folder: str = "data") -> Union[pd.DataFrame, None]:
    """
    Read the data from a folder (default = "data"), returning a structured format such as a DataFrame.

    IMPLEMENTATION GUIDE
    ====================

    1. LOAD DATA:
       - Attempts to load `data.csv` from the given folder.
       - Folder defaults to "data".

    2. ERROR HANDLING:
       - Missing folder → log + return None
       - Missing file → log + return None
       - Other unexpected errors → log + return None

    3. LOGGING:
       - Logs when data loading starts
       - Logs success with row/column summary
       - Logs detailed error messages

    Args:
        folder (str, optional): Path to folder containing `data.csv`. Defaults to "data".

    Returns:
        pd.DataFrame or None
    """
    logger.info(f"Starting data access operation in folder: {folder}")

    # Ensure folder exists
    if not os.path.exists(folder):
        logger.error(f"Folder not found: {folder}")
        print(f"Error: Folder not found -> {folder}")
        return None

    file_path = os.path.join(folder, "gyro.csv")

    try:
        # Try to load the CSV
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)

        # Validate content
        if df.empty:
            logger.warning(f"Loaded file is empty: {file_path}")
            print(f"Warning: The file {file_path} is empty.")
            return None

        logger.info(
            f"Successfully loaded data: {len(df)} rows, {len(df.columns)} columns"
        )
        return df

    except FileNotFoundError:
        logger.error(f"Data file not found: {file_path}")
        print(f"Error: Could not find file -> {file_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied when accessing: {file_path}")
        print(f"Error: Permission denied -> {file_path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        print(f"Error loading data from {file_path}: {e}")
        return None


if __name__ == "__main__":
    # Test the data access function
    df = data("data/noiseless/2025-09-17-095442")
    print(df.head())