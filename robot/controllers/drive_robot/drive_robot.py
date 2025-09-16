from controller import Robot, Accelerometer, Keyboard
import threading
import pickle
import os
from datetime import datetime
import queue

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
    
    # Set motor initial configurations
    motor_l.setPosition(float('inf'))
    motor_l.setVelocity(0.0) 
    motor_r.setPosition(float('inf'))
    motor_r.setVelocity(0.0) 
    
    # Enable devices
    camera.enable(timestep)
    keyboard.enable(timestep)
    accelerometer.enable(timestep)
    
    # Data collection setup
    data_queue = queue.Queue()
    stop_thread = threading.Event()
    
    # Create data directory with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    data_dir = f"data/{timestamp}"
    os.makedirs(data_dir, exist_ok=True)
    accel_file = os.path.join(data_dir, "accelerometer.pkl")
    
    # Background thread function for saving accelerometer data
    def save_accelerometer_data():
        data = []
        while not stop_thread.is_set():
            try:
                # Get data from queue with a timeout to check stop condition
                accel_data, sim_time = data_queue.get(timeout=1.0)
                data.append((sim_time, accel_data))
                # Save periodically to avoid data loss
                if len(data) >= 100:  # Save every 100 samples
                    with open(accel_file, 'wb') as f:
                        pickle.dump(data, f)
                    data = []  # Reset data list after saving
            except queue.Empty:
                continue
        # Save any remaining data when stopping
        if data:
            with open(accel_file, 'wb') as f:
                pickle.dump(data, f)
    
    # Start background thread for data saving
    data_thread = threading.Thread(target=save_accelerometer_data)
    data_thread.daemon = True  # Ensure thread exits when main program exits
    data_thread.start()
    
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
        
        # Collect accelerometer data with simulation time
        sim_time = robot.getTime()
        accel_data = accelerometer.getValues()  # Returns [x, y, z]
        data_queue.put((accel_data, sim_time))
    
    # Cleanup: stop the background thread and ensure final data save
    stop_thread.set()
    data_thread.join()