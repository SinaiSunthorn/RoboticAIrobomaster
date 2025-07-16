import robomaster
from robomaster import robot

def sub_data_handler(angle_info):
    pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle = angle_info
    print("gimbal angle: pitch_angle:{0}, yaw_angle:{1}, pitch_ground_angle:{2}, yaw_ground_angle:{3}".format(
        pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle))

if __name__ == '_main_':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_gimbal = ep_robot.gimbal

    ep_gimbal.sub_angle(freq=10, callback=sub_data_handler)

    # หมุนจาก -90 ถึง 90 ทีละ 10 องศา
    for yaw in range(-90, 91, 10):  # start, stop, step
        ep_gimbal.moveto(pitch=0, yaw=yaw, pitch_speed=0, yaw_speed=10).wait_for_completed()

    # หมุนกลับไปที่ -90 ด้วยความเร็วสูงขึ้น
    ep_gimbal.moveto(pitch=0, yaw=-90, pitch_speed=0, yaw_speed=50).wait_for_completed()

    ep_gimbal.unsub_angle()
    ep_robot.close()