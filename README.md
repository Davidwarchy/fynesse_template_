# Access, Assess & Address Pipeline for Robot Sensor/Actuator Data 
* Inspired by https://mlatcl.github.io/
* Template from https://github.com/lawrennd/fynesse_template/

## Access
* Collect a variety of sensor readings:
- IMU (gyroscope, accelerometer) 
- GPS 
- Depth camera 
- Camera 
- Lidar 
- Compass 
- Distance 
- Light sensor 
- Position sensor
- Radar 
- Touch sensor 

* We can use a background thread to collect data (to sort of queue data for storage) so that there's isn't latency between driving the robot. 
* Simulation to be done on Webots with robots with a variety of sensors 
* We want to consider sim to real gap 

We are going to collect data in the following form: 
data/YYYY-MM-DD-HHMMSS/sensor-name.pkl 

Let's first try with accelerometer, I think that we are going to need a driver for each sensor that collects the specific sensor. 

We can use the simulation time as an index for each reading

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

We can have a system capable of automatically collating data and sort of automatically knowing which data links well with which data, which data gives us information on other data. 

## Address 
> Which sensors give redundant information 
> Which sensors predict other sensors well 
> 

## Stuff to Look at 
PCA components for localization.