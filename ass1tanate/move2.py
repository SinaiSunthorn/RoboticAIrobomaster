from robomaster import robot
import time
import csv
import os

# เก็บข้อมูล log
log_data_pos = []

# PD controller parameters
Kp = 5.0
Kd = 2.0
tolerance = 0.01
current_x = 0.0
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
    global current_x
    timestamp = time.time()
    current_x = position_info[0]
    entry = {"timestamp": timestamp, "x": position_info[0], "y": position_info[1], "z": position_info[2]}
    log_data_pos.append(entry)
    print(f"Position X: {position_info[0]:.2f}")
    write_csv_once("log_poshigh1.csv", ["timestamp", "x", "y", "z"], entry)

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=pos_info_handler)

    print("Starting PD-Control square movement...")

    try:
        for i in range(4):
            print(f"🟩 Side {i+1}: Moving forward 1.2 meters...")

            setpoint = current_x + 1.2  # ไม่ใช้ global แล้ว
            prev_error = 0.0
            prev_time = None

            while True:
                current_time = time.time()
                error = setpoint - current_x

                dt = 0.1 if prev_time is None else current_time - prev_time
                derivative = (error - prev_error) / dt if dt > 0 else 0.0
                speed = (Kp * error) + (Kd * derivative)
                speed = max(min(speed, 1.0), -1.0)

                if abs(error) <= tolerance:
                    ep_chassis.drive_speed(x=0, y=0, z=0)
                    print("✅ Target distance reached.")
                    break

                ep_chassis.drive_speed(x=speed, y=0, z=0)
                print(f"Error: {error:.2f}, Speed: {speed:.2f}")

                prev_error = error
                prev_time = current_time
                time.sleep(0.1)

            # Rotate 90 degrees
            print("🔄 Rotating 90 degrees...")
            ep_chassis.drive_speed(x=0, y=0, z=45)
            time.sleep(2)
            ep_chassis.drive_speed(x=0, y=0, z=0)
            time.sleep(1)

        print("✅ Square path complete.")

    finally:
        ep_chassis.unsub_position()
        ep_robot.close()
        print("Robot closed.")
