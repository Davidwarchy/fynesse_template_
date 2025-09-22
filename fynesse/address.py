"""
Address module for the fynesse framework.

This module handles question addressing functionality including:
- Statistical analysis
- Predictive modeling
- Data visualization for decision-making
- Dashboard creation
"""

from assess import data
from typing import Any, Union
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr
from bokeh.plotting import figure, show
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource

# Set up logging
logger = logging.getLogger(__name__)

# Here are some of the imports we might expect
# import sklearn.model_selection  as ms
# import sklearn.linear_model as lm
# import sklearn.svm as svm
# import sklearn.naive_bayes as naive_bayes
# import sklearn.tree as tree

# import GPy
# import torch
# import tensorflow as tf

# Or if it's a statistical analysis
# import scipy.stats

def analyze_data(data: Union[pd.DataFrame, Any]) -> pd.DataFrame:
    """
    Perform statistical analysis, explore relationships between sensor data of different dimensions,
    and return a DataFrame with means, standard deviations, and other statistics.

    Args:
        data: Input DataFrame from assess.data() with sim_time as index and sensor column.

    Returns:
        pd.DataFrame: DataFrame containing statistical metrics (mean, std, min, max, median) for each numeric column.
    """
    """
    Address a particular question that arises from the data.

    IMPLEMENTATION GUIDE FOR STUDENTS:
    ==================================

    1. REPLACE THIS FUNCTION WITH YOUR ANALYSIS CODE:
       - Perform statistical analysis on the data
       - Create visualizations to explore patterns
       - Build models to answer specific questions
       - Generate insights and recommendations

    2. ADD ERROR HANDLING:
       - Check if input data is valid and sufficient
       - Handle analysis failures gracefully
       - Validate analysis results

    3. ADD BASIC LOGGING:
       - Log analysis steps and progress
       - Log key findings and insights
       - Log any issues encountered

    4. EXAMPLE IMPLEMENTATION:
       if data is None or len(data) == 0:
           print("Error: No data available for analysis")
           return {}

       print("Starting data analysis...")
       # Your analysis code here
       results = {"sample_size": len(data), "analysis_complete": True}
       return results
    """
    logger.info("Starting data analysis")

    # Validate input data
    if data is None or not isinstance(data, pd.DataFrame):
        logger.error("No valid data provided for analysis")
        print("Error: No valid data available for analysis")
        return pd.DataFrame()

    if len(data) == 0:
        logger.error("Empty dataset provided for analysis")
        print("Error: Empty dataset provided for analysis")
        return pd.DataFrame()

    logger.info(f"Analyzing data with {len(data)} rows, {len(data.columns)} columns")

    try:
        # Step 1: Compute Basic Statistics
        numeric_columns = data.select_dtypes(include=["number"]).columns
        if len(numeric_columns) == 0:
            logger.error("No numeric columns available for statistical analysis")
            print("Error: No numeric columns available for analysis")
            return pd.DataFrame()

        # Compute statistics
        stats_df = pd.DataFrame({
            "mean": data[numeric_columns].mean(),
            "std": data[numeric_columns].std(),
            "min": data[numeric_columns].min(),
            "max": data[numeric_columns].max(),
            "median": data[numeric_columns].median()
        })
        logger.info("Computed statistics (mean, std, min, max, median) for numeric columns")
        print(f"Statistics:\n{stats_df}")

        # Step 2: Handle Different Data Shapes (e.g., Lidar vs. Compass)
        sensors = data["sensor"].unique()
        pca_results = {}
        reduced_data = pd.DataFrame(index=data.index)

        for sensor in sensors:
            sensor_data = data[data["sensor"] == sensor].copy()
            value_cols = [col for col in sensor_data.columns if col not in ["sim_time", "sensor"]]

            if not value_cols:
                logger.warning(f"No value columns for sensor {sensor}")
                continue

            # Apply PCA for high-dimensional sensors (e.g., lidar)
            if sensor == "lidar" and len(value_cols) > 3:
                logger.info(f"Applying PCA to reduce dimensionality of {sensor} data")
                X = sensor_data[value_cols].dropna()
                if len(X) > 0:
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    n_components = min(3, len(value_cols), len(X))
                    pca = PCA(n_components=n_components)
                    X_reduced = pca.fit_transform(X_scaled)
                    # Use unique column names to avoid overlap
                    pca_cols = [f"{sensor}_pca_{i+1}" for i in range(n_components)]
                    reduced_data = reduced_data.join(
                        pd.DataFrame(X_reduced, index=X.index, columns=pca_cols),
                        rsuffix=f"_{sensor}"  # Add suffix to handle column overlap
                    )
                    explained_variance = pca.explained_variance_ratio_.sum()
                    pca_results[sensor] = {
                        "components": n_components,
                        "explained_variance_ratio": explained_variance,
                    }
                    logger.info(
                        f"PCA for {sensor}: {n_components} components, "
                        f"{explained_variance*100:.2f}% variance explained"
                    )
                else:
                    logger.warning(f"No valid data for PCA on {sensor}")
            else:
                # For low-dimensional sensors, use original columns with sensor prefix
                for col in value_cols:
                    reduced_data = reduced_data.join(
                        sensor_data[[col]].rename(columns={col: f"{sensor}_{col}"}),
                        rsuffix=f"_{sensor}"
                    )

        # Step 3: Correlation Analysis
        correlation_matrix = reduced_data.corr(method="pearson")
        logger.info("Computed correlation matrix for reduced data")
        print("Correlation Matrix (subset):\n", correlation_matrix.iloc[:5, :5])

        # Identify strong correlations (|corr| > 0.7)
        strong_correlations = []
        corr_threshold = 0.7
        for col1 in correlation_matrix.columns:
            for col2 in correlation_matrix.index:
                if col1 < col2:
                    corr = correlation_matrix.loc[col2, col1]
                    if abs(corr) > corr_threshold:
                        strong_correlations.append(
                            {"columns": (col1, col2), "correlation": corr}
                        )
        logger.info(f"Found {len(strong_correlations)} strong correlations (|corr| > {corr_threshold})")
        if strong_correlations:
            print("Strong Correlations (|corr| > 0.7):")
            for sc in strong_correlations:
                print(f"{sc['columns'][0]} vs {sc['columns'][1]}: {sc['correlation']:.3f}")

        # Step 4: Sensor Simplification
        redundant_sensors = []
        for sensor in sensors:
            sensor_cols = [col for col in reduced_data.columns if sensor in col]
            if not sensor_cols:
                continue
            sensor_corrs = correlation_matrix[sensor_cols].drop(sensor_cols, errors="ignore")
            max_corr = sensor_corrs.abs().max().max()
            if max_corr > 0.9:
                redundant_sensors.append({"sensor": sensor, "max_correlation": max_corr})
        if redundant_sensors:
            logger.info(f"Potential redundant sensors: {[rs['sensor'] for rs in redundant_sensors]}")
            print("Potential Redundant Sensors:")
            for rs in redundant_sensors:
                print(f"{rs['sensor']}: max correlation = {rs['max_correlation']:.3f}")

        # Step 5: Predict Actuator Outcomes
        actuator_cols = [col for col in reduced_data.columns if "actuator" in col]
        predictive_sensors = []
        if actuator_cols:
            for col in reduced_data.columns:
                if col not in actuator_cols and col != "sim_time":
                    for actuator_col in actuator_cols:
                        corr, _ = pearsonr(
                            reduced_data[col].dropna(),
                            reduced_data[actuator_col].dropna(),
                        )
                        if abs(corr) > 0.6:
                            predictive_sensors.append(
                                {"sensor_col": col, "actuator_col": actuator_col, "correlation": corr}
                            )
            logger.info(f"Found {len(predictive_sensors)} sensor-actuator correlations")
            if predictive_sensors:
                print("Sensors Predictive of Actuators:")
                for ps in predictive_sensors:
                    print(f"{ps['sensor_col']} predicts {ps['actuator_col']}: corr = {ps['correlation']:.3f}")

        # Step 6: Visualizations
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=False, cmap="coolwarm", center=0)
        plt.title("Correlation Heatmap of Sensor Data")
        plt.tight_layout()
        plt.show()
        logger.info("Generated correlation heatmap")

        p = figure(
            title="Key Sensor and Actuator Time Series",
            x_axis_label="Time (s)",
            y_axis_label="Value",
            x_axis_type="linear",
            width=800,
            height=400,
        )
        colors = Category10[10]
        for i, col in enumerate(reduced_data.columns[:5]):
            if col != "sim_time":
                source = ColumnDataSource(
                    pd.DataFrame({"sim_time": reduced_data.index, col: reduced_data[col]})
                )
                p.line(
                    x="sim_time",
                    y=col,
                    source=source,
                    legend_label=col,
                    color=colors[i % len(colors)],
                )
        p.legend.click_policy = "hide"
        logger.info("Generating Bokeh time series plot for key sensors")
        show(p)

        # Step 7: Insights for Task Grounding
        insights = []
        if redundant_sensors:
            insights.append(
                f"Sensor Simplification: Consider removing {[rs['sensor'] for rs in redundant_sensors]}"
            )
        if predictive_sensors:
            insights.append(
                f"Prediction: {[ps['sensor_col'] for ps in predictive_sensors]} predict actuators"
            )
        insights.append("Task Grounding: Strong sensor-actuator relationships detected")
        stats_df["insights"] = ", ".join(insights)
        logger.info("Generated insights for robotics goals")
        print("Insights:")
        for insight in insights:
            print(f"- {insight}")

        logger.info("Data analysis completed successfully")
        print(f"Analysis completed. Sample size: {len(data)}")
        return stats_df.reset_index().rename(columns={"index": "column"})

    except Exception as e:
        logger.error(f"Error during data analysis: {e}")
        print(f"Error analyzing data: {e}")
        return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    # Example folder path - replace with actual path as needed
    folder = "data/noiseless/2025-09-17-095442"
    df = data(folder)
    if df is not None:
        results = analyze_data(df)
        print("Analysis Results:", results)
    
        print("Data address completed.")

        print("="*180)