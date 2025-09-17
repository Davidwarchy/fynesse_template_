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

## Assess

The collected dataset gives us:

* **Multimodal sensor time-series** (synchronous but at different rates).
* **Actuator–sensor correlations** (how motor commands affect observed values).
* **Redundancies & relationships**: which sensors provide overlapping information, and which are critical.

This allows us to explore tasks like:

* Predicting one sensor’s readings from another (sensor fusion or compression).
* Identifying minimal sensor sets needed for reliable behavior.
* Mapping the topology of robot-environment interaction (e.g., wheel encoders + compass → odometry drift).

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

## Credits 
* Inspired by https://mlatcl.github.io/
* Template from https://github.com/lawrennd/fynesse_template/

## License 
Licensed under **MIT**.