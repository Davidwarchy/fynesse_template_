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
   - Use print() statements for basic logging
   - Log when operations start and complete
   - Log errors with context information
   - Log data summary information

Attribution:
This TUM RGB-D dataset download script is adapted from:
https://github.com/rmurai0610/MASt3R-SLAM
"""

####################################################################
# Access module for the fynesse framework
# Handles dataset access functionality for TUM RGB-D sequences
# Incorporates legal and ethical considerations, error handling, and logging
####################################################################

import os
import logging
import subprocess
from typing import Optional

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TUM_DATASETS = [
    "rgbd_dataset_freiburg1_360.tgz",
    "rgbd_dataset_freiburg1_floor.tgz",
    "rgbd_dataset_freiburg1_desk.tgz",
    "rgbd_dataset_freiburg1_desk2.tgz",
    "rgbd_dataset_freiburg1_room.tgz",
    "rgbd_dataset_freiburg1_plant.tgz",
    "rgbd_dataset_freiburg1_teddy.tgz",
    "rgbd_dataset_freiburg1_xyz.tgz",
    "rgbd_dataset_freiburg1_rpy.tgz",
]

BASE_URL = "https://cvg.cit.tum.de/rgbd/dataset/freiburg1"

def download_and_extract_tum_dataset(
        dataset_dir: str = "datasets/tum"
    ) -> Optional[str]:
    """
    Download and extract the TUM RGB-D dataset sequences.

    Args:
        dataset_dir (str): Directory to store datasets (default: datasets/tum).

    Returns:
        Optional[str]: Path to dataset directory if successful, None otherwise.

    Notes:
        - Downloads multiple TUM RGB-D sequences (freiburg1 family).
        - Uses wget + tar for reliability.
        - Logs progress and errors.
        - Ensure compliance with dataset license:
          https://vision.in.tum.de/data/datasets/rgbd-dataset
    """
    logger.info(f"Preparing dataset directory: {dataset_dir}")
    os.makedirs(dataset_dir, exist_ok=True)

    try:
        for fname in TUM_DATASETS:
            url = f"{BASE_URL}/{fname}"
            local_path = os.path.join(dataset_dir, fname)

            if not os.path.exists(local_path):
                logger.info(f"Downloading {fname}...")
                cmd = ["wget", "-O", local_path, url]
                subprocess.run(cmd, check=True)
            else:
                logger.info(f"Already downloaded: {fname}")

            # Extract
            logger.info(f"Extracting {fname}...")
            cmd = ["tar", "-xvzf", local_path, "-C", dataset_dir]
            subprocess.run(cmd, check=True)

        logger.info("All datasets downloaded and extracted successfully.")
        return dataset_dir

    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        print(f"Error: Failed during download/extract: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        return None


# Example usage
if __name__ == "__main__":
    download_and_extract_tum_dataset()
