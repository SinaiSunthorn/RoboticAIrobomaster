import pandas as pd
import matplotlib.pyplot as plt
import ast

# โหลดไฟล์ CSV
file_path = "log_data.csv"  # เปลี่ยน path ได้ตามต้องการ
df = pd.read_csv(file_path)

# แปลง data จาก string → tuple หรือ list
df["data"] = df["data"].apply(ast.literal_eval)

# ฟังก์ชันพล็อตข้อมูลทั่วไป
def plot_flat_data(sensor_df, sensor_type):
    sensor_df = sensor_df.sort_values(by="timestamp")
    max_len = max(len(d) for d in sensor_df["data"])
    labels = [f"{sensor_type}_{i}" for i in range(max_len)]
    sensor_df[labels] = pd.DataFrame(sensor_df["data"].tolist(), index=sensor_df.index)

    plt.figure(figsize=(12, 6))
    for col in labels:
        plt.plot(sensor_df["timestamp"], sensor_df[col], label=col)
    plt.title(f"{sensor_type.upper()} Sensor Data")
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.show()

    
def plot_nested_data(sensor_df, sensor_type):
    sensor_df = sensor_df.sort_values(by="timestamp")
    max_len = max(len(d) for d in sensor_df["data"])
    group_cols = [f"group_{i}" for i in range(max_len)]
    sensor_df[group_cols] = pd.DataFrame(sensor_df["data"].tolist(), index=sensor_df.index)

    plt.figure(figsize=(14, 7))
    for group in group_cols:
        group_values = sensor_df[group].tolist()
        try:
            exploded_df = pd.DataFrame(group_values)
        except ValueError:
            continue  # ข้ามถ้าไม่สามารถแปลงได้ (ข้อมูลไม่สม่ำเสมอ)
        if exploded_df.shape[1] == 0:
            continue

        exploded_df.columns = [f"{group}_{i}" for i in range(exploded_df.shape[1])]
        exploded_df["timestamp"] = sensor_df["timestamp"].values

        for col in exploded_df.columns[:-1]:
            plt.plot(exploded_df["timestamp"], exploded_df[col], label=col)

    plt.title(f"{sensor_type.upper()} - Combined Values")
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.show()


# วิเคราะห์ข้อมูลแยกตาม type
sensor_types = df["type"].unique()
for sensor in sensor_types:
    sensor_df = df[df["type"] == sensor].copy()
    first_data = sensor_df["data"].iloc[0]

    if isinstance(first_data, (tuple, list)):
        if all(isinstance(i, (int, float)) for i in first_data):
            plot_flat_data(sensor_df, sensor)
        elif all(isinstance(i, (list, tuple)) for i in first_data):
            plot_nested_data(sensor_df, sensor)
        else:
            print(f"[SKIPPED] Cannot interpret structure for sensor: {sensor}")
    else:
        print(f"[SKIPPED] Unrecognized data format in sensor: {sensor}")
