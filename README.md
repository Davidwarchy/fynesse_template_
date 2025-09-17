# Access, Assess & Address Pipeline for Robot Sensor/Actuator Data 

We’re building a dataset of sensor and actuator readings from a cylindrical two-wheeled robot as it moves around. The aim is to set up an **access → assess → address** pipeline to process this data and explore what the robot (and we) can learn from it.

![alt text](media/web.gif)

* Inspired by https://mlatcl.github.io/
* Template from https://github.com/lawrennd/fynesse_template/

## Access
### Sensors 
* Collect a variety of sensor readings:
- [x] IMU (gyroscope, accelerometer) 
- [x] GPS 
- Depth camera 
- Camera 
- [x] Lidar 
- [x] Compass 
- [x] Distance sensor
- [x] Light sensor 
- [x] Position sensor (position encoder)
- Radar 
- [x] Touch sensor 

### Actuators 
* Actuator commands 

### How to create the dataset 
* We can use a background thread to collect data (to sort of queue data for storage) so that there's isn't latency between driving the robot. 
* Simulation to be done on Webots with robots with a variety of sensors 
* We want to consider sim to real gap 

We are going to collect data in the following form: 
data/YYYY-MM-DD-HHMMSS/sensor-name.pkl 

Let's first try with accelerometer, I think that we are going to need a driver for each sensor that collects the specific sensor. 

We can use the simulation time as an index for each reading

I think that we need to specify the structure of each sensor reading because they are quite very different. 

#### Accelerometer
Shape: (3,)

#### Compass 
Shape: (3,)

#### Lidar 
Shape: (2048, 3)

### Real to Sim Gap 
* [List of some gaps](https://chatgpt.com/share/68c81135-1118-8002-975e-974bc2d90bb0)
> Instead of the usual real to sim gap, we'll sort of reverse collections from simulation to integrate weaknesses in the real world...
- wear out 
- noise 
- missing data

After collecting the perfect data, we might want to do the following to introduce imperfections in the real world 
- Remove some data 
- Add  noise to the data 
- Time & Latency Effects - sensors have different rates 
- Jitter - Mechanical vibration (say from wheels on rough ground, or drone propellers) causes high-frequency oscillations in the readings.

## Assess 
> Get means, standard devs, correlations

* We can have a system capable of automatically collating data and sort of automatically knowing which data links well with which data, which data gives us information on other data. 

* A major question is when we have data of different dimensions. How do we assess relationships between data of different shapes? An example would be lidar data and compass data. Lidar has shape (2048, 3). 

## Address 
> Which sensors give redundant information 
> Which sensors predict other sensors well 

## Stuff to Look at 
PCA components for localization.