import pandas as pd
import matplotlib.pyplot as plt

# Helper function: load csv and normalize timestamp
def load_and_normalize(csv_file):
    df = pd.read_csv(csv_file)
    df["timestamp"] -= df["timestamp"].iloc[0]  # start timestamp at 0
    return df

# ---------- Plot log_att.csv ----------
try:
    df_att = load_and_normalize("log_att.csv")
    plt.figure(figsize=(10, 6))
    plt.plot(df_att["timestamp"], df_att["yaw"], label="Yaw")
    plt.plot(df_att["timestamp"], df_att["pitch"], label="Pitch")
    plt.plot(df_att["timestamp"], df_att["roll"], label="Roll")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (degrees)")
    plt.title("Attitude (Yaw, Pitch, Roll) vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except FileNotFoundError:
    print("File log_att.csv not found, skipping...")

# ---------- Plot log_pos.csv ----------
try:
    df_pos = load_and_normalize("log_pos.csv")
    plt.figure(figsize=(10, 6))
    plt.plot(df_pos["timestamp"], df_pos["x"], label="X")
    plt.plot(df_pos["timestamp"], df_pos["y"], label="Y")
    plt.plot(df_pos["timestamp"], df_pos["z"], label="Z")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (meters)")
    plt.title("Position (X, Y, Z) vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except FileNotFoundError:
    print("File log_pos.csv not found, skipping...")

# ---------- Plot log_imu.csv ----------
try:
    df_imu = load_and_normalize("log_imu.csv")
    # Acceleration
    plt.figure(figsize=(10, 6))
    plt.plot(df_imu["timestamp"], df_imu["acc_x"], label="Acc X")
    plt.plot(df_imu["timestamp"], df_imu["acc_y"], label="Acc Y")
    plt.plot(df_imu["timestamp"], df_imu["acc_z"], label="Acc Z")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.title("IMU Acceleration vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    # Gyroscope
    plt.figure(figsize=(10, 6))
    plt.plot(df_imu["timestamp"], df_imu["gyro_x"], label="Gyro X")
    plt.plot(df_imu["timestamp"], df_imu["gyro_y"], label="Gyro Y")
    plt.plot(df_imu["timestamp"], df_imu["gyro_z"], label="Gyro Z")
    plt.xlabel("Time (s)")
    plt.ylabel("Angular Velocity (°/s)")
    plt.title("IMU Gyroscope vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except FileNotFoundError:
    print("File log_imu.csv not found, skipping...")

# ---------- Plot log_status.csv ----------
try:
    df_sta = load_and_normalize("log_status.csv")
    plt.figure(figsize=(10, 6))
    plt.step(df_sta["timestamp"], df_sta["static_flag"], label="Static Flag")
    plt.step(df_sta["timestamp"], df_sta["up_hill"], label="Up Hill")
    plt.step(df_sta["timestamp"], df_sta["down_hill"], label="Down Hill")
    plt.xlabel("Time (s)")
    plt.ylabel("Status (0 or 1)")
    plt.title("Robot Status Flags vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except FileNotFoundError:
    print("File log_status.csv not found, skipping...")

# ---------- Plot log_esc.csv ----------
try:
    df_esc = load_and_normalize("log_esc.csv")
    plt.figure(figsize=(10, 6))
    plt.plot(df_esc["timestamp"], df_esc["speed"], label="Speed")
    plt.plot(df_esc["timestamp"], df_esc["angle"], label="Angle")
    plt.xlabel("Time (s)")
    plt.ylabel("ESC Values")
    plt.title("ESC Speed and Angle vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except FileNotFoundError:
    print("File log_esc.csv not found, skipping...")
