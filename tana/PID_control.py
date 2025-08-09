from robomaster import robot
import time
import csv
import os

# พารามิเตอร์ PID-Control
Kp = 2.0
Ki = 0.1
Kd = 0.3
target_distance = 1.2  # ระยะทางที่ต้องการเดิน (เมตร)

# เก็บข้อมูลตำแหน่ง
log_data_pos = []
current_x = 0.0
current_y = 0.0
current_speed = 0.0

# ตัวแปรสำหรับคำนวณความเร็ว
prev_x = None
prev_y = None
prev_time = None

# Path ไฟล์ CSV
csv_file_path = os.path.join(os.getcwd(), "log_slide_square.csv")

# เขียน log ลง CSV
def write_csv_once(file_path, fieldnames, entry):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists or os.path.getsize(file_path) == 0:
            writer.writeheader()
        writer.writerow(entry)

# callback สำหรับรับตำแหน่ง
def pos_info_handler(position_info):
    global current_x, current_y, prev_x, prev_y, prev_time

    try:
        timestamp = time.time()
        current_x = position_info[0]
        current_y = position_info[1]

        # คำนวณความเร็ว (m/s)
        if prev_time is not None:
            dt = timestamp - prev_time
            dx = current_x - prev_x
            dy = current_y - prev_y
            speed = ((dx**2 + dy**2) ** 0.5) / dt
        else:
            speed = 0.0

        prev_x, prev_y, prev_time = current_x, current_y, timestamp

        entry = {
            "timestamp": timestamp,
            "x": current_x,
            "y": current_y,
            "z": position_info[2],
            "speed": speed
        }
        log_data_pos.append(entry)
        write_csv_once(csv_file_path, ["timestamp", "x", "y", "z", "speed"], entry)
    except Exception as e:
        print(f"[ERROR in pos_info_handler] {e}")

# ฟังก์ชันเดินตรงตามแกนด้วย PID-Control
def move_straight(ep_chassis, axis='x', distance=1.2):
    global current_x, current_y
    print(f"Moving {distance} meters on {axis.upper()} axis using PID-Control...")

    dt = 0.1  # sampling time (100ms)
    prev_error = 0.0
    integral_error = 0.0

    # ตั้งค่าจุดเริ่มต้น
    if axis == 'x':
        start_pos = current_x
        get_error = lambda: distance - (current_x - start_pos)
    elif axis == 'y':
        start_pos = current_y
        get_error = lambda: distance - (current_y - start_pos)
    else:
        raise ValueError("Axis must be 'x' or 'y'")

    while True:
        error = get_error()
        integral_error += error * dt
        d_error = (error - prev_error) / dt
        speed = (Kp * error) + (Ki * integral_error) + (Kd * d_error)

        prev_error = error

        # เงื่อนไขหยุด
        if abs(error) <= 0.01:
            ep_chassis.drive_speed(x=0, y=0, z=0)
            print(f"Reached target on {axis.upper()} axis.")
            break

        if axis == 'x':
            ep_chassis.drive_speed(x=speed, y=0, z=0)
        else:
            ep_chassis.drive_speed(x=0, y=speed, z=0)

        print(f"Err: {error:.3f}, Int: {integral_error:.3f}, Der: {d_error:.3f}, Speed: {speed:.3f}")
        time.sleep(dt)

# Main program
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=pos_info_handler)
    
    try:
        print("== Start Square Movement (PID-Control) ==")
        move_straight(ep_chassis, axis='x', distance=target_distance)     # ด้านที่ 1
        move_straight(ep_chassis, axis='y', distance=target_distance)     # ด้านที่ 2
        move_straight(ep_chassis, axis='x', distance=-target_distance)    # ด้านที่ 3
        move_straight(ep_chassis, axis='y', distance=-target_distance)    # ด้านที่ 4

    finally:
        ep_chassis.unsub_position()
        ep_robot.close()
        print("Robot closed.")
