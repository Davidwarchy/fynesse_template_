from controller import Robot, Accelerometer, Keyboard, Compass, Lidar, GPS, Gyro, InertialUnit, LightSensor, TouchSensor
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
    camera = robot.getDevice("Astra rgb")
    keyboard = robot.getKeyboard()
    accelerometer = robot.getDevice("accelerometer")
    compass = robot.getDevice("compass")
    lidar = robot.getDevice("lidar")
    gps = robot.getDevice("gps")
    gyro = robot.getDevice("gyro")
    imu = robot.getDevice("imu")
    light_sensor = robot.getDevice("light sensor")
    touch_sensor = robot.getDevice("touch sensor")
    
    # Set motor initial configurations
    motor_l.setPosition(float('inf'))
    motor_l.setVelocity(0.0) 
    motor_r.setPosition(float('inf'))
    motor_r.setVelocity(0.0) 
    
    # Enable devices
    camera.enable(timestep)
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
    
    # Data collection setup
    accel_queue = queue.Queue()
    compass_queue = queue.Queue()
    lidar_queue = queue.Queue()
    gps_queue = queue.Queue()
    gyro_queue = queue.Queue()
    imu_queue = queue.Queue()
    light_queue = queue.Queue()
    touch_queue = queue.Queue()
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
    actuator_file = os.path.join(data_dir, "actuator.pkl")
    
    # Background thread function for saving sensor/actuator data
    def save_sensor_data(sensor_queue, output_file):
        data = []
        while not stop_thread.is_set():
            try:
                # Get data from queue with a timeout to check stop condition
                sensor_data, sim_time = sensor_queue.get(timeout=1.0)
                data.append((sim_time, sensor_data))
                # Save periodically to avoid data loss
                if len(data) >= 100:  # Save every 100 samples
                    with open(output_file, 'wb') as f:
                        pickle.dump(data, f)
                    data = []  # Reset data list after saving
            except queue.Empty:
                continue
        # Save any remaining data when stopping
        if data:
            with open(output_file, 'wb') as f:
                pickle.dump(data, f)
    
    # Start background threads for data saving
    accel_thread = threading.Thread(target=save_sensor_data, args=(accel_queue, accel_file))
    compass_thread = threading.Thread(target=save_sensor_data, args=(compass_queue, compass_file))
    lidar_thread = threading.Thread(target=save_sensor_data, args=(lidar_queue, lidar_file))
    gps_thread = threading.Thread(target=save_sensor_data, args=(gps_queue, gps_file))
    gyro_thread = threading.Thread(target=save_sensor_data, args=(gyro_queue, gyro_file))
    imu_thread = threading.Thread(target=save_sensor_data, args=(imu_queue, imu_file))
    light_thread = threading.Thread(target=save_sensor_data, args=(light_queue, light_file))
    touch_thread = threading.Thread(target=save_sensor_data, args=(touch_queue, touch_file))
    actuator_thread = threading.Thread(target=save_sensor_data, args=(actuator_queue, actuator_file))
    
    accel_thread.daemon = True
    compass_thread.daemon = True
    lidar_thread.daemon = True
    gps_thread.daemon = True
    gyro_thread.daemon = True
    imu_thread.daemon = True
    light_thread.daemon = True
    touch_thread.daemon = True
    actuator_thread.daemon = True
    
    accel_thread.start()
    compass_thread.start()
    lidar_thread.start()
    gps_thread.start()
    gyro_thread.start()
    imu_thread.start()
    light_thread.start()
    touch_thread.start()
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
            # Move forward
            speed_l = 1.0 * speed_max
            speed_r = 1.0 * speed_max
        elif key == ord('S') or key == keyboard.DOWN:
            # Move backward
            speed_l = -1.0 * speed_max
            speed_r = -1.0 * speed_max
        elif key == ord('A') or key == keyboard.LEFT:
            # Turn left
            speed_l = -1.0 * speed_max
            speed_r = 1.0 * speed_max
        elif key == ord('D') or key == keyboard.RIGHT:
            # Turn right
            speed_l = 1.0 * speed_max
            speed_r = -1.0 * speed_max
        
        # Set motor speeds
        motor_l.setVelocity(speed_l)
        motor_r.setVelocity(speed_r)
        
        # Collect sensor and actuator data with simulation time
        sim_time = robot.getTime()
        accel_data = np.array(accelerometer.getValues(), dtype=np.float32)  # Convert to NumPy array
        compass_data = np.array(compass.getValues(), dtype=np.float32)  # Convert to NumPy array
        lidar_points = lidar.getPointCloud()
        lidar_data = np.array([(p.x, p.y, p.z) for p in lidar_points], dtype=np.float32) if lidar_points else np.array([], dtype=np.float32)
        gps_data = np.array(gps.getValues(), dtype=np.float32)  # [x, y, z]
        gyro_data = np.array(gyro.getValues(), dtype=np.float32)  # [angular velocity x, y, z]
        imu_data = np.array(imu.getRollPitchYaw(), dtype=np.float32)  # [roll, pitch, yaw]
        light_data = np.array([light_sensor.getValue()], dtype=np.float32)  # Single value

        # Handle TouchSensor data
        sensor_type = touch_sensor.getType()  # Get sensor type
        if sensor_type == TouchSensor.BUMPER:
            # Bumper sensor returns a single value (0.0 or 1.0)
            touch_data = np.array([touch_sensor.getValue()], dtype=np.float32)
        elif sensor_type == TouchSensor.FORCE:
            # Force sensor returns a single scalar force value
            touch_data = np.array([touch_sensor.getValue()], dtype=np.float32)
        elif sensor_type == TouchSensor.FORCE3D:
            # Force-3d sensor returns a 3D vector [x, y, z]
            touch_values = touch_sensor.getValues()  # Returns LP_c_double
            # Convert LP_c_double to list
            touch_data = np.array([touch_values[i] for i in range(3)], dtype=np.float32)
        else:
            # Fallback for unknown type
            touch_data = np.array([], dtype=np.float32)
            print(f"Warning: Unknown touch sensor type {sensor_type}")

        print(f'Touch Sensor Data: {touch_data}')
        
        actuator_data = np.array([speed_l, speed_r], dtype=np.float32)  # Left and right motor speeds
        
        accel_queue.put((accel_data, sim_time))
        compass_queue.put((compass_data, sim_time))
        lidar_queue.put((lidar_data, sim_time))
        gps_queue.put((gps_data, sim_time))
        gyro_queue.put((gyro_data, sim_time))
        imu_queue.put((imu_data, sim_time))
        light_queue.put((light_data, sim_time))
        touch_queue.put((touch_data, sim_time))
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
    actuator_thread.join()