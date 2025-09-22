# Access → Assess → Address Pipeline for Robot Sensor/Actuator Data

We’re building a dataset of sensor and actuator readings from a **cylindrical two-wheeled robot** as it moves around.

![alt text](media/web.gif)

The robot is equipped with multiple sensors and actuators, and the goal is to:

1. **Access** — systematically collect and store the data.
2. **Assess** — analyze, structure, and inspect it for patterns, reliability, and relationships.
3. **Address** — act on what we learn, e.g., simplifying sensing, predicting one modality from another, or accounting for real-world imperfections.

This pipeline forms the basis for understanding how robots (and we) can learn from multimodal sensorimotor data.

---

## Access

### Sensors

We log readings from a variety of onboard sensors:

* ✅ IMU (gyroscope, accelerometer)
* ✅ GPS
* Depth camera
* Camera
* ✅ Lidar
* ✅ Compass
* ✅ Distance sensor
* ✅ Light sensor
* ✅ Position sensor (encoder)
* Radar
* ✅ Touch sensor

### Actuators

* Wheel actuation commands (motor velocities, torques, etc.)

### Data Collection Strategy

* **Threaded logging**: a background process queues and saves data without slowing down robot control.
* **Simulation**: runs in Webots with the mentioned robot sensor configurations.
* **File structure**:

```
robot/controllers/drive_robot/data/YYYY-MM-DD-HHMMSS/sensor-name.pkl
```

We can then transfer these pickle files to the main data folder:

[data](data)

We do consider [real-to-sim](#sim-to-real-gap-in-reverse) constraints

* **Index**: all readings use simulation time as the reference index.

### Sensor Reading Shapes

To keep things consistent, each sensor has a defined data shape:

* **Accelerometer** → `(3,)`
* **Compass** → `(3,)`
* **Lidar** → `(2048, 3)`
* **Wheel Encoder** → `(1,)`

Example snippet from the encoder:

| Simulation Time | Value   |
| --------------- | ------- |
| 40.016 s        | 159.371 |
| 40.032 s        | 159.472 |
| 40.048 s        | 159.572 |
| 40.064 s        | 159.673 |

All shapes are stored in [`sensors.json`](robot/controllers/drive_robot/sensors.json).

---

### Sim-to-Real Gap (in reverse)

Our simulation starts “perfect.” We deliberately degrade the data to mimic real-world imperfections:

* **Wear-out effects** (e.g., drifting sensors, weaker motors).
* **Noise injection** (Gaussian, salt-and-pepper, systematic bias).
* **Dropped/missing data** (packet loss, sensor faults).
* **Latency** (different update rates across sensors).
* **Jitter** (mechanical vibrations causing oscillations).

--- 

## Assess 

The `assess` module provides a framework for **loading, cleaning, visualizing, and labeling sensor data** for analysis and machine learning. It combines data handling, logging, visualization, and anomaly labeling into a structured workflow.

### Key Features Implemented

1. **Logging Setup**

   * Configured logging with timestamps, levels, and messages.
   * Logs progress and issues during data assessment, filling, visualization, and labeling.

2. **Data Cleaning & Preparation**

   * `fill_missing_per_sensor(df, interval=0.016)`

     * Restores missing `sim_time` values per sensor at fixed 16ms intervals.
     * Reindexes sensor groups, forward-fills missing values, and maintains time alignment.
     * Saves the cleaned data to `xffilled_data.csv`.

   * `data(folder="data")`

     * Loads data via the `access` module.
     * Handles missing values and invalid types.
     * Ensures `sim_time` is numeric and used as index.
     * Normalizes column types (floats/ints).
     * Logs and prints summaries of cleaning results.

3. **Data Exploration**

   * `query(data)`

     * Interactive CLI-based querying of sensor data.
     * Allows filtering by sensor name and time range.
     * Reports how many rows match the criteria.

4. **Visualization**

   * `view(data)`

     * Generates **Bokeh time-series plots** per sensor and value column.
     * Interactive legend (click-to-hide/show).
     * Generates **seaborn heatmap** for missing value visualization.

5. **Labeling for Supervised Learning**

   * `labelled(data)`

     * Labels anomalies using a **3 standard deviation threshold** rule.
     * Adds a `label` column (0 = normal, 1 = anomaly).
     * Prints label distribution and returns labeled dataset.

6. **Main Execution Block**

   * Demonstrates usage with a sample dataset folder:

     * Loads and cleans data (`data`)
     * Prints head of dataset
     * Runs a query (`query`)
     * Generates plots (`view`)
     * Produces labeled dataset (`labelled`)
---

## Address

Once we’ve assessed, we can **address real-world constraints**:

### Robotics Goals

* **Simplification**: Which sensors can be dropped with minimal performance loss?
* **Prediction**: Which sensors best predict actuator outcomes or each other?
* **Task grounding**: Relating sensor relationships to navigation, mapping, and control.

---

👉 In short:

* **Access** gives us the raw data.
* **Assess** turns it into structure, patterns, and insight.
* **Address** adapts that insight to the messiness of the real world and the needs of robotics.

## Assess 
> Get means, standard devs, correlations

* We can have a system capable of automatically collating data and sort of automatically knowing which data links well with which data, which data gives us information on other data. 

* A major question is when we have data of different dimensions. How do we assess relationships between data of different shapes? An example would be lidar data and compass data. Lidar has shape (2048, 3). 

### Limitations of the Current Pipeline 
- Real world data is usually very specific, and important signals are encoded in durations of different perception. There's a lot of frequency details that are ommitted. 
- Comparison of data of different dimensions is a challenge to implement and where it's implemented, we might use averages, which glosses over fine details 

## Credits 
* Inspired by https://mlatcl.github.io/
* Template from https://github.com/lawrennd/fynesse_template/

## License 
Licensed under **MIT**.