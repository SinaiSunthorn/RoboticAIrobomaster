import pandas as pd

# อ่านไฟล์ .csv ที่ได้จาก IMU
df = pd.read_csv("log_imu.csv")  # เปลี่ยนชื่อไฟล์เป็นชื่อไฟล์จริงของคุณ

# แยกข้อมูล Accelerometer และ Gyroscope
acc_df = df[['timestamp', 'acc_x', 'acc_y', 'acc_z']]
gyro_df = df[['timestamp', 'gyro_x', 'gyro_y', 'gyro_z']]

# บันทึกเป็นไฟล์ .csv แยกต่างหาก
acc_df.to_csv("acc_data.csv", index=False)
gyro_df.to_csv("gyro_data.csv", index=False)

print("แยกไฟล์เสร็จสิ้น: imu_acc_data.csv และ imu_gyro_data.csv")
