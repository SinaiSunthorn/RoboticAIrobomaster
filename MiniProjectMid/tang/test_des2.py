 from robomaster import robot
import time, math
import matplotlib.pyplot as plt

# ----------------- เก็บข้อมูล -----------------
# สิ่งกีดขวางในพิกัด "ตามเส้นทาง": (s_on_path, lateral_offset)
path_obstacles = []

current_x = 0.0
current_y = 0.0
prev_x = None
prev_y = None
path_s = 0.0            # ระยะทางจริงที่วิ่งตามเส้นทาง (m)

base_yaw_rad = 0.0      # มุมฐาน (rad)
gimbal_yaw_deg = 0.0    # มุมกิมบอลแกน yaw (deg)
tof_distance = None     # m

# ----------------- พารามิเตอร์ -----------------
SCAN_MIN = -60
SCAN_MAX = 60
SCAN_STEP = 15
SCAN_SPEED = 120        # deg/s
TOF_TH = 0.30           # m
AVOID_TURN = 45         # deg
FORWARD_AFTER_AVOID = 0.35  # m
COOLDOWN_S = 1.0

MERGE_S = 0.25          # m (รวมจุดที่ s ใกล้กัน)
MERGE_Y = 0.25          # m (รวมจุดที่เยื้องข้างใกล้กัน)

# ----------------- Callbacks -----------------
def pos_handler(position_info):
    global current_x, current_y, prev_x, prev_y, path_s
    x, y = position_info[0], position_info[1]
    if prev_x is not None:
        path_s += math.hypot(x - prev_x, y - prev_y)  # ระยะตามเส้นทาง
    prev_x, prev_y = x, y
    current_x, current_y = x, y

def att_handler(attitude_info):
    global base_yaw_rad
    base_yaw_rad = math.radians(attitude_info[0])

def tof_handler(tof_info):
    global tof_distance
    tof_distance = tof_info[0] / 1000.0  # mm → m

def gimbal_angle_handler(angle_info):
    global gimbal_yaw_deg
    gimbal_yaw_deg = angle_info[1]       # [pitch, yaw, pitch_ground, yaw_ground]

def add_path_obstacle(s_on_path, lat_off):
    # รวมจุดที่อยู่ใกล้กันในพิกัดตามเส้นทาง
    for i, (s0, y0) in enumerate(path_obstacles):
        if abs(s_on_path - s0) <= MERGE_S and abs(lat_off - y0) <= MERGE_Y:
            # เลือกเก็บจุดที่อยู่ไกลกว่าตามทาง (s มากกว่า)
            if s_on_path > s0:
                path_obstacles[i] = (s_on_path, lat_off)
            return
    path_obstacles.append((s_on_path, lat_off))

# ----------------- Main -----------------
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_chassis = ep_robot.chassis
    ep_sensor  = ep_robot.sensor
    ep_gimbal  = ep_robot.gimbal

    # สมัคร callback
    ep_chassis.sub_position(freq=10, callback=pos_handler)
    ep_chassis.sub_attitude(freq=10, callback=att_handler)
    ep_sensor.sub_distance(freq=10, callback=tof_handler)
    ep_gimbal.sub_angle(freq=10, callback=gimbal_angle_handler)

    # กิมบอลกลางก่อนเริ่ม
    ep_gimbal.moveto(pitch=0, yaw=0, pitch_speed=100, yaw_speed=100).wait_for_completed()

    try:
        print("== Start moving with GIMBAL-SCAN avoidance (points only) ==")
        start_time = time.time()
        last_action_time = 0.0

        sweep = list(range(SCAN_MIN, SCAN_MAX + 1, SCAN_STEP))
        sweep += list(range(SCAN_MAX, SCAN_MIN - 1, -SCAN_STEP))

        while time.time() - start_time < 15:
            ep_chassis.drive_speed(x=0.25, y=0, z=0)

            for yaw_target in sweep:
                ep_gimbal.moveto(pitch=0, yaw=yaw_target, yaw_speed=SCAN_SPEED).wait_for_completed()
                time.sleep(0.08)  # รอ TOF อัปเดต

                if tof_distance is not None and tof_distance < TOF_TH:
                    if time.time() - last_action_time < COOLDOWN_S:
                        continue
                    last_action_time = time.time()

                    d = tof_distance
                    phi_rel = math.radians(gimbal_yaw_deg)   # มุมเทียบแกนเส้นทาง
                    s_hit = path_s + max(0.0, d * math.cos(phi_rel))
                    y_off = d * math.sin(phi_rel)

                    add_path_obstacle(s_hit, y_off)
                    print(f"Hit @ s={s_hit:.2f} m, offset={y_off:+.2f} m (d={d:.2f} m, yaw={gimbal_yaw_deg:+.0f}°) → avoid")

                    # หลบ
                    ep_chassis.drive_speed(x=0, y=0, z=0); time.sleep(0.1)
                    turn_cmd = AVOID_TURN if gimbal_yaw_deg > 0 else -AVOID_TURN
                    ep_chassis.move(x=0, y=0, z=turn_cmd, z_speed=80).wait_for_completed()
                    ep_chassis.move(x=FORWARD_AFTER_AVOID, y=0, z=0, xy_speed=0.35).wait_for_completed()
                    ep_chassis.drive_speed(x=0.25, y=0, z=0)

                if time.time() - start_time >= 15:
                    break

        ep_chassis.drive_speed(x=0, y=0, z=0)

    finally:
        ep_chassis.unsub_position()
        ep_chassis.unsub_attitude()
        ep_sensor.unsub_distance()
        ep_gimbal.unsub_angle()
        ep_robot.close()
        print("Robot closed.")

        # ---------- แสดงเป็น "จุด" เท่านั้น ----------
        if path_obstacles:
            s_vals = [s for s, _y in path_obstacles]
            y_vals = [_y for s, _y in path_obstacles]
            plt.scatter(s_vals, y_vals, marker='x', s=60, label='Obstacle')

        plt.xlabel("Along-path distance s (m)")
        plt.ylabel("Lateral offset from path (m)")
        plt.title("Detected obstacle points (referenced to path)")
        plt.grid(True)
        plt.legend()
        plt.show()
