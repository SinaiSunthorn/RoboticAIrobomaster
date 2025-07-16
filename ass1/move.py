from robomaster import robot
import time
import csv
import os

# Lists to store logs for each sensor type
log_data_att = []
log_data_pos = []
log_data_imu = []
log_data_sta = []
log_data_esc = []

# Function to append a new row to a CSV file, with headers written once
def write_csv_once(file_path, fieldnames, entry):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists or os.path.getsize(file_path) == 0:
            writer.writeheader()
        writer.writerow(entry)

# Handler for attitude sensor (yaw, pitch, roll)
def att_info_handler(attitude_info):
    timestamp = time.time()
    entry = {"timestamp": timestamp, "yaw": attitude_info[0], "pitch": attitude_info[1], "roll": attitude_info[2]}
    log_data_att.append(entry)
    print(attitude_info[0], attitude_info[1], attitude_info[2])
    write_csv_once("log_att.csv", ["timestamp", "yaw", "pitch", "roll"], entry)

# Handler for position sensor (x, y, z)
def pos_info_handler(position_info):
    timestamp = time.time()
    entry = {"timestamp": timestamp, "x": position_info[0], "y": position_info[1], "z": position_info[2]}
    log_data_pos.append(entry)
    print(position_info[0], position_info[1], position_info[2])
    write_csv_once("log_pos.csv", ["timestamp", "x", "y", "z"], entry)

# Handler for IMU sensor (acceleration and gyroscope)
def imu_info_handler(imu_info):
    timestamp = time.time()
    entry = {
        "timestamp": timestamp,
        "acc_x": imu_info[0], "acc_y": imu_info[1], "acc_z": imu_info[2],
        "gyro_x": imu_info[3], "gyro_y": imu_info[4], "gyro_z": imu_info[5]
    }
    log_data_imu.append(entry)
    print(imu_info[0], imu_info[1], imu_info[2], imu_info[3], imu_info[4], imu_info[5])
    write_csv_once("log_imu.csv", ["timestamp", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"], entry)

# Handler for status sensor (flags and impact detection)
def status_info_handler(status_info):
    timestamp = time.time()
    entry = {
        "timestamp": timestamp,
        "static_flag": status_info[0], "up_hill": status_info[1], "down_hill": status_info[2], "on_slope": status_info[3],
        "pick_up": status_info[4], "slip_flag": status_info[5],
        "impact_x": status_info[6], "impact_y": status_info[7], "impact_z": status_info[8],
        "roll_over": status_info[9], "hill_static": status_info[10]
    }
    log_data_sta.append(entry)
    print(*status_info)
    write_csv_once(
        "log_status.csv",
        ["timestamp", "static_flag", "up_hill", "down_hill", "on_slope", "pick_up", "slip_flag",
         "impact_x", "impact_y", "impact_z", "roll_over", "hill_static"],
        entry
    )

# Handler for ESC (Electronic Speed Controller) sensor
def esc_info_handler(esc_info):
    timestamp = time.time()
    speed, angle, esc_timestamp, state = esc_info  # Unpack values
    entry = {
        "timestamp": timestamp, "speed": speed, "angle": angle,
        "esc_timestamp": esc_timestamp, "state": state
    }
    log_data_esc.append(entry)
    print(speed, angle, esc_timestamp, state)
    write_csv_once("log_esc.csv", ["timestamp", "speed", "angle", "esc_timestamp", "state"], entry)

# Main script
if __name__ == '__main__':
    # Create and initialize the robot in AP (Wi-Fi direct) mode
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    # Access the robot's chassis module
    ep_chassis = ep_robot.chassis

    # Subscribe to chassis sensor data (10 Hz update rate)
    ep_chassis.sub_position(freq=10, callback=pos_info_handler)
    ep_chassis.sub_attitude(freq=10, callback=att_info_handler)
    ep_chassis.sub_imu(freq=10, callback=imu_info_handler)
    ep_chassis.sub_esc(freq=10, callback=esc_info_handler)
    ep_chassis.sub_status(freq=10, callback=status_info_handler)

    # Define movement parameters for square path
    side_length = 0.6      # Length of each side (meters)
    forward_speed = 1      # Forward speed (m/s)
    turn_angle = -90        # Turn angle (degrees)

    try:
        # Move the robot in a square (4 sides)
        for i in range(4):
            print(f"Side {i+1}: move forward")
            ep_chassis.move(x=side_length, y=0, z=0, xy_speed=forward_speed).wait_for_completed()

            print(f"Side {i+1}: turn left 90 degrees")
            ep_chassis.move(x=0, y=0, z=turn_angle, z_speed=60).wait_for_completed()

        print("Square path completed.")

    finally:
        # Unsubscribe all sensor data before shutting down
        ep_chassis.unsub_status()
        ep_chassis.unsub_esc()
        ep_chassis.unsub_imu()
        ep_chassis.unsub_attitude()
        ep_chassis.unsub_position()

        # Safely close the robot connection
        ep_robot.close()
