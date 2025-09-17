from controller import Robot, Accelerometer, Keyboard, Compass, Lidar, GPS, Gyro, InertialUnit, LightSensor, TouchSensor, DistanceSensor, PositionSensor, Camera
import threading
import pickle
import os
from datetime import datetime
import queue
import numpy as np

if __name__ == "__main__":
    # Create the Robot instance.
    robot = Robot()
    
    # Get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())
    speed_max = 6.28  # Maximum speed
    
    # Initialize devices
    motor_l = robot.getDevice("motor_1")
    motor_r = robot.getDevice("motor_2")
    rgb_camera = robot.getDevice("Astra rgb")
    depth_camera = robot.getDevice("Astra depth")
    keyboard = robot.getKeyboard()
    accelerometer = robot.getDevice("accelerometer")
    compass = robot.getDevice("compass")
    lidar = robot.getDevice("lidar")
    gps = robot.getDevice("gps")
    gyro = robot.getDevice("gyro")
    imu = robot.getDevice("imu")
    light_sensor = robot.getDevice("light sensor")
    touch_sensor = robot.getDevice("touch sensor")
    distance_sensor = robot.getDevice("distance sensor")
    position_sensor_1 = robot.getDevice("position_sensor_1")
    position_sensor_2 = robot.getDevice("position_sensor_2")
    
    # Set motor initial configurations
    motor_l.setPosition(float('inf'))
    motor_l.setVelocity(0.0) 
    motor_r.setPosition(float('inf'))
    motor_r.setVelocity(0.0) 
    
    # Enable devices
    rgb_camera.enable(timestep)
    depth_camera.enable(timestep * 10)
    keyboard.enable(timestep)
    accelerometer.enable(timestep)
    compass.enable(timestep)
    lidar.enable(timestep)
    lidar.enablePointCloud()
    gps.enable(timestep)
    gyro.enable(timestep)
    imu.enable(timestep)
    light_sensor.enable(timestep)
    touch_sensor.enable(timestep)
    distance_sensor.enable(timestep)
    position_sensor_1.enable(timestep)
    position_sensor_2.enable(timestep)
    
    # Data collection setup
    accel_queue = queue.Queue()
    compass_queue = queue.Queue()
    lidar_queue = queue.Queue()
    gps_queue = queue.Queue()
    gyro_queue = queue.Queue()
    imu_queue = queue.Queue()
    light_queue = queue.Queue()
    touch_queue = queue.Queue()
    distance_queue = queue.Queue()
    position_1_queue = queue.Queue()
    position_2_queue = queue.Queue()
    depth_queue = queue.Queue()
    actuator_queue = queue.Queue()
    stop_thread = threading.Event()
    
    # Create data directory with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    data_dir = f"data/{timestamp}"
    os.makedirs(data_dir, exist_ok=True)
    accel_file = os.path.join(data_dir, "accelerometer.pkl")
    compass_file = os.path.join(data_dir, "compass.pkl")
    lidar_file = os.path.join(data_dir, "lidar.pkl")
    gps_file = os.path.join(data_dir, "gps.pkl")
    gyro_file = os.path.join(data_dir, "gyro.pkl")
    imu_file = os.path.join(data_dir, "imu.pkl")
    light_file = os.path.join(data_dir, "light.pkl")
    touch_file = os.path.join(data_dir, "touch.pkl")
    distance_file = os.path.join(data_dir, "distance.pkl")
    position_1_file = os.path.join(data_dir, "position_1.pkl")
    position_2_file = os.path.join(data_dir, "position_2.pkl")
    depth_file = os.path.join(data_dir, "depth.pkl")
    actuator_file = os.path.join(data_dir, "actuator.pkl")
    
    # Background thread function for saving sensor/actuator data
    def save_sensor_data(sensor_queue, output_file, sensor_type):
        data = []
        while not stop_thread.is_set():
            try:
                raw_data, sim_time = sensor_queue.get(timeout=1.0)
                # Convert raw data to NumPy array based on sensor type
                if sensor_type == "accelerometer":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                elif sensor_type == "compass":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                elif sensor_type == "lidar":
                    sensor_data = np.array([(p.x, p.y, p.z) for p in raw_data], dtype=np.float32) if raw_data else np.array([], dtype=np.float32)
                elif sensor_type == "gps":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                elif sensor_type == "gyro":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                elif sensor_type == "imu":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                elif sensor_type == "light":
                    sensor_data = np.array([raw_data], dtype=np.float32)
                elif sensor_type == "touch":
                    if isinstance(raw_data, float):  # Bumper or Force sensor
                        sensor_data = np.array([raw_data], dtype=np.float32)
                    else:  # Force3D sensor
                        sensor_data = np.array([raw_data[i] for i in range(3)], dtype=np.float32)
                elif sensor_type == "distance":
                    sensor_data = np.array([raw_data], dtype=np.float32)
                elif sensor_type == "position_1" or sensor_type == "position_2":
                    sensor_data = np.array([raw_data], dtype=np.float32)
                elif sensor_type == "depth":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                elif sensor_type == "actuator":
                    sensor_data = np.array(raw_data, dtype=np.float32)
                else:
                    sensor_data = np.array([], dtype=np.float32)
                    print(f"Warning: Unknown sensor type {sensor_type}")
                
                data.append((sim_time, sensor_data))
                if len(data) >= 500:  # Save every 500 samples
                    with open(output_file, 'wb') as f:
                        pickle.dump(data, f)
                    data = []
            except queue.Empty:
                continue
        if data:
            with open(output_file, 'wb') as f:
                pickle.dump(data, f)
    
    # Start background threads for data saving
    accel_thread = threading.Thread(target=save_sensor_data, args=(accel_queue, accel_file, "accelerometer"))
    compass_thread = threading.Thread(target=save_sensor_data, args=(compass_queue, compass_file, "compass"))
    lidar_thread = threading.Thread(target=save_sensor_data, args=(lidar_queue, lidar_file, "lidar"))
    gps_thread = threading.Thread(target=save_sensor_data, args=(gps_queue, gps_file, "gps"))
    gyro_thread = threading.Thread(target=save_sensor_data, args=(gyro_queue, gyro_file, "gyro"))
    imu_thread = threading.Thread(target=save_sensor_data, args=(imu_queue, imu_file, "imu"))
    light_thread = threading.Thread(target=save_sensor_data, args=(light_queue, light_file, "light"))
    touch_thread = threading.Thread(target=save_sensor_data, args=(touch_queue, touch_file, "touch"))
    distance_thread = threading.Thread(target=save_sensor_data, args=(distance_queue, distance_file, "distance"))
    position_1_thread = threading.Thread(target=save_sensor_data, args=(position_1_queue, position_1_file, "position_1"))
    position_2_thread = threading.Thread(target=save_sensor_data, args=(position_2_queue, position_2_file, "position_2"))
    depth_thread = threading.Thread(target=save_sensor_data, args=(depth_queue, depth_file, "depth"))
    actuator_thread = threading.Thread(target=save_sensor_data, args=(actuator_queue, actuator_file, "actuator"))
    
    accel_thread.daemon = True
    compass_thread.daemon = True
    lidar_thread.daemon = True
    gps_thread.daemon = True
    gyro_thread.daemon = True
    imu_thread.daemon = True
    light_thread.daemon = True
    touch_thread.daemon = True
    distance_thread.daemon = True
    position_1_thread.daemon = True
    position_2_thread.daemon = True
    depth_thread.daemon = True
    actuator_thread.daemon = True
    
    accel_thread.start()
    compass_thread.start()
    lidar_thread.start()
    gps_thread.start()
    gyro_thread.start()
    imu_thread.start()
    light_thread.start()
    touch_thread.start()
    distance_thread.start()
    position_1_thread.start()
    position_2_thread.start()
    depth_thread.start()
    actuator_thread.start()
    
    # Main loop: perform simulation steps until Webots is stopping the controller or 'Q' is pressed
    while robot.step(timestep) != -1:
        # Initialize motor speeds
        speed_l = 0.0
        speed_r = 0.0
        
        # Get keyboard input
        key = keyboard.getKey()
        
        # Check for 'Q' to quit the simulation
        if key == ord('Q'):
            break
        
        # Define movement based on key pressed
        if key == ord('W') or key == keyboard.UP:
            speed_l = 1.0 * speed_max
            speed_r = 1.0 * speed_max
        elif key == ord('S') or key == keyboard.DOWN:
            speed_l = -1.0 * speed_max
            speed_r = -1.0 * speed_max
        elif key == ord('A') or key == keyboard.LEFT:
            speed_l = -1.0 * speed_max
            speed_r = 1.0 * speed_max
        elif key == ord('D') or key == keyboard.RIGHT:
            speed_l = 1.0 * speed_max
            speed_r = -1.0 * speed_max
        
        # Set motor speeds
        motor_l.setVelocity(speed_l)
        motor_r.setVelocity(speed_r)
        
        # Collect raw sensor and actuator data with simulation time
        sim_time = robot.getTime()
        accel_data = accelerometer.getValues()  # Raw list [x, y, z]
        compass_data = compass.getValues()  # Raw list [x, y, z]
        lidar_data = lidar.getPointCloud()  # Raw point cloud
        gps_data = gps.getValues()  # Raw list [x, y, z]
        gyro_data = gyro.getValues()  # Raw list [x, y, z]
        imu_data = imu.getRollPitchYaw()  # Raw list [roll, pitch, yaw]
        light_data = light_sensor.getValue()  # Raw float
        touch_data = touch_sensor.getValue() if touch_sensor.getType() in [TouchSensor.BUMPER, TouchSensor.FORCE] else touch_sensor.getValues()  # Raw float or list
        distance_data = distance_sensor.getValue()  # Raw float
        position_1_data = position_sensor_1.getValue()  # Raw float
        position_2_data = position_sensor_2.getValue()  # Raw float
        depth_data = depth_camera.getRangeImage()  # Raw depth image list
        actuator_data = [speed_l, speed_r]  # Raw list
        
        accel_queue.put((accel_data, sim_time))
        compass_queue.put((compass_data, sim_time))
        lidar_queue.put((lidar_data, sim_time))
        gps_queue.put((gps_data, sim_time))
        gyro_queue.put((gyro_data, sim_time))
        imu_queue.put((imu_data, sim_time))
        light_queue.put((light_data, sim_time))
        touch_queue.put((touch_data, sim_time))
        distance_queue.put((distance_data, sim_time))
        position_1_queue.put((position_1_data, sim_time))
        position_2_queue.put((position_2_data, sim_time))
        depth_queue.put((depth_data, sim_time))
        actuator_queue.put((actuator_data, sim_time))
    
    # Cleanup: stop the background threads and ensure final data save
    stop_thread.set()
    accel_thread.join()
    compass_thread.join()
    lidar_thread.join()
    gps_thread.join()
    gyro_thread.join()
    imu_thread.join()
    light_thread.join()
    touch_thread.join()
    distance_thread.join()
    position_1_thread.join()
    position_2_thread.join()
    depth_thread.join()
    actuator_thread.join()