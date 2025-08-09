from robomaster import robot
import time
import csv
import os
import math

# PD controller parameters
Kp = 5.0
Kd = 2.0
tolerance = 0.01

current_x = 0.0
current_y = 0.0
prev_error = 0.0
prev_time = None

def write_csv_once(file_path, fieldnames, entry):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists or os.path.getsize(file_path) == 0:
            writer.writeheader()
        writer.writerow(entry)

def pos_info_handler(position_info):
    global current_x, current_y
    current_x = position_info[0]
    current_y = position_info[1]

def pd_move_to(ep_chassis, axis, target_value):
    global prev_error, prev_time
    prev_error = 0.0
    prev_time = None

    print(f"Moving on axis: {axis} to {target_value:.2f}m")
    while True:
        current_time = time.time()
        dt = 0.1 if prev_time is None else current_time - prev_time

        pos = current_x if axis == "x" else current_y
        error = target_value - pos
        derivative = (error - prev_error) / dt if dt > 0 else 0.0

        speed = Kp * error + Kd * derivative
        speed = max(min(speed, 0.5), -0.5)

        if abs(error) <= tolerance:
            ep_chassis.drive_speed(x=0, y=0, z=0)
            print(f"{axis}-axis target reached.")
            break

        if axis == "x":
            ep_chassis.drive_speed(x=speed, y=0, z=0)
        else:
            ep_chassis.drive_speed(x=0, y=speed, z=0)

        prev_error = error
        prev_time = current_time
        time.sleep(0.05)

def rotate_to_heading(ep_chassis, target_angle_deg):
    print(f"Rotating to heading: {target_angle_deg}°")
    ep_chassis.move_to(x=0, y=0, z=target_angle_deg, z_unit='deg').wait_for_completed()
    time.sleep(1)

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=pos_info_handler)

    try:
        square_path = [
            ("x", 1.2, 0),
            ("y", 1.2, 90),
            ("x", 0.0, 180),
            ("y", 0.0, 270)
        ]

        for axis, target, heading in square_path:
            rotate_to_heading(ep_chassis, heading)
            pd_move_to(ep_chassis, axis, target)

        print("✅ Square path complete.")

    finally:
        ep_chassis.unsub_position()
        ep_robot.close()
        print("Robot closed.")