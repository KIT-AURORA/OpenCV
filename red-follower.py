from picamera2 import Picamera2
import cv2
import numpy as np
import gpiozero
import time

camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
camera.configure(camera_config)
camera.start()

image_width = 640
image_height = 480
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 4000     #実験などで細かい値を設定
maximum_area = 300000  # 実験などで細かい値を設定

robot = gpiozero.Robot(left=(24, 23), right=(20, 21)) #ピン配置の設定
forward_speed = 1 # 実験などで細かい値を0~1に設定。
turn_speed = 0.7  # 実験などで細かい値を0~1に設定

HUE_VAL = 120# 実験などで細かい値を設定

#環境に合わせて変わるため、範囲は大きくとっておくのが良い。


lower_color = np.array([HUE_VAL-10, 100, 55])# 実験などで細かい値を設定
upper_color = np.array([HUE_VAL+10, 255, 255])# 実験などで細かい値を設定

while True:
    
    image = camera.capture_array()

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    color_mask = cv2.inRange(hsv, lower_color, upper_color)

    contours, _ = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    object_area = 0
    object_x = 0
    object_y = 0

    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        found_area = width * height
        center_x = x + (width / 2)
        center_y = y + (height / 2)
        if object_area < found_area:
            object_area = found_area
            object_x = center_x
            object_y = center_y

    if object_area > 0:
        ball_location = [object_area, object_x, object_y]
    else:
        ball_location = None

    if ball_location:
        if (ball_location[0] > minimum_area) and (ball_location[0] < maximum_area):
            if ball_location[1] > (center_image_x + (image_width / 6)):
                robot.right(turn_speed)
                print("右折")
            elif ball_location[1] < (center_image_x - (image_width / 6)):
                robot.left(turn_speed)
                print("左折")
            else:
                robot.forward(forward_speed)
                print("前進")
        elif ball_location[0] < minimum_area:
            robot.left(turn_speed)
            print("ターゲット未検知, 捜索します")
        else:
            robot.stop()
            print("ターゲット到着, 停止します")
    else:
        robot.left(turn_speed)
        print("ターゲットが見つかりません")

