"""
Access module for the fynesse framework.

This module handles data access functionality including:
- Data loading from various sources (web, local files, databases)
- Legal compliance (intellectual property, privacy rights)
- Ethical considerations for data usage
- Error handling for access issues

Legal and ethical considerations are paramount in data access.
Ensure compliance with e.g. .GDPR, intellectual property laws, and ethical guidelines.

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

4. EXAMPLE PATTERNS:
   
   Basic error handling:
   try:
       df = pd.read_csv('data.csv')
   except FileNotFoundError:
       print("Error: Could not find data.csv file")
       return None
   
   With logging:
   print("Loading data from data.csv...")
   try:
       df = pd.read_csv('data.csv')
       print(f"Successfully loaded {len(df)} rows of data")
       return df
   except FileNotFoundError:
       print("Error: Could not find data.csv file")
       return None
"""

####################################################################
# Access module for the fynesse framework
# Handles data access functionality including geospatial data retrieval and visualization
# Incorporates legal and ethical considerations, error handling, and logging
####################################################################

from typing import Union, Optional
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt
import logging
import warnings

# Suppress specific OSMnx FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning, module='osmnx')

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class access:
    @staticmethod
    def plot_city_map(
        place_name: str, 
        latitude: float, 
        longitude: float, 
        box_size_km: float = 2
    ) -> Optional[plt.Figure]:
        """
        Plot a city map using OpenStreetMap data for a given place and coordinates.

        Args:
            place_name (str): Name of the place (e.g., 'Nyeri, Kenya').
            latitude (float): Latitude of the center point.
            longitude (float): Longitude of the center point.
            box_size_km (float): Size of the bounding box in kilometers (default: 2).

        Returns:
            Optional[plt.Figure]: Matplotlib figure object if successful, None otherwise.

        Notes:
            - Uses OSMnx to retrieve and visualize geospatial data.
            - Includes points of interest, street network, and buildings.
            - Bounding box size is approximate, based on 1 degree ≈ 111 km.
            - Logs operations and errors for debugging.
            - Ensures compliance with OpenStreetMap's terms of use.
        """
        logger.info(f"Starting plot_city_map for {place_name}")

        try:
            # Validate inputs
            if not isinstance(place_name, str) or not place_name.strip():
                logger.error("Invalid place name provided")
                print("Error: Place name must be a non-empty string")
                return None
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                logger.error("Invalid coordinates provided")
                print("Error: Latitude must be [-90, 90] and longitude [-180, 180]")
                return None
            if box_size_km <= 0:
                logger.error("Invalid box size provided")
                print("Error: Box size must be positive")
                return None

            # Convert box size from kilometers to degrees (approximate: 1 degree ≈ 111 km)
            box_size_deg = 0.1
            box_width = box_size_deg
            box_height = box_size_deg

            # Create bounding box
            north = latitude + box_height / 2
            south = latitude - box_height / 2
            west = longitude - box_width / 2
            east = longitude + box_width / 2
            bbox = (west, south, east, north)
            logger.info(f"Bounding box created: {bbox}")

            # Define points of interest tags
            poi_tags = {
                "amenity": True,
                "buildings": True,
                "historic": True,
                "leisure": True,
                "shop": True,
                "tourism": True,
                "religion": True,
                "memorial": True
            }

            # Download geospatial data
            logger.info(f"Downloading points of interest for {place_name}")
            pois = ox.features_from_bbox(bbox, tags=poi_tags)
            logger.info(f"Downloaded {len(pois)} points of interest")

            logger.info(f"Downloading street network for {place_name}")
            graph = ox.graph_from_bbox(bbox)
            nodes, edges = ox.graph_to_gdfs(graph)
            logger.info("Street network downloaded")

            logger.info(f"Downloading area and buildings for {place_name}")
            area = ox.geocode_to_gdf(place_name)
            buildings = ox.features_from_bbox(bbox, tags={"building": True})
            logger.info(f"Downloaded {len(buildings)} buildings")

            # Create plot
            fig, ax = plt.subplots(figsize=(6, 6))
            area.plot(ax=ax, color="tan", alpha=0.5)
            buildings.plot(ax=ax, facecolor="gray", edgecolor="gray")
            edges.plot(ax=ax, linewidth=1, edgecolor="black", alpha=0.3)
            nodes.plot(ax=ax, color="black", markersize=1, alpha=0.3)
            pois.plot(ax=ax, color="green", markersize=5, alpha=1)
            ax.set_xlim(west, east)
            ax.set_ylim(south, north)
            ax.set_title(place_name, fontsize=14)

            logger.info(f"Map plot created successfully for {place_name}")
            plt.show()
            return fig

        except ox._errors.InsufficientResponseError as e:
            logger.error(f"OSM API returned insufficient data: {e}")
            print(f"Error: Insufficient data from OpenStreetMap API for {place_name}")
            return None
        except ValueError as e:
            logger.error(f"Invalid input or geocoding error: {e}")
            print(f"Error: Invalid input or unable to geocode {place_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while plotting map: {e}")
            print(f"Error: Failed to plot map for {place_name}: {e}")
            return None

# Example usage
if __name__ == "__main__":
    access.plot_city_map('Nyeri, Kenya', -0.4371, 36.9580, 2)