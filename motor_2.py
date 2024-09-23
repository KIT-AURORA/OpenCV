import time
import cv2
import numpy as np
from picamera2 import Picamera2
import RPi.GPIO as GPIO
from time import sleep

# カメラの初期設定
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
camera.configure(camera_config)
camera.start()

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Result", 1280, 960)

# GPIOの初期設定
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

p1 = GPIO.PWM(17, 50)
p2 = GPIO.PWM(18, 50)
p3 = GPIO.PWM(24, 50)
p4 = GPIO.PWM(25, 50)

p1.start(0)
p2.start(0)
p3.start(0)
p4.start(0)

# モーターの動作関数
def move_forward():
    p1.ChangeDutyCycle(100)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(100)
    p4.ChangeDutyCycle(0)

def move_backward():
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(100)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(100)

def stop():
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)

while True:
    try:
        hue_value = int(input("Hue value between 10 and 245: "))
        if (hue_value < 10) or (hue_value > 245):
            raise ValueError
    except ValueError:
        print("That isn't an integer between 10 and 245, try again")
    else:
        break

lower_red = np.array([hue_value - 10, 100, 50])
upper_red = np.array([hue_value + 10, 255, 150])

while True:
    image = camera.capture_array()
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    color_mask = cv2.inRange(hsv, lower_red, upper_red)

    # グレースケール画像の白い部分の面積を計算
    white_area = cv2.countNonZero(color_mask)

    # 全体のピクセル数を計算
    total_area = color_mask.shape[0] * color_mask.shape[1]

    # 白い部分の面積が全体の何%を占めているかを計算
    percentage = (white_area / total_area) * 100

    # 面積とパーセンテージを表示するためのテキストを設定
    text_area = f'White Area: {white_area} pixels'
    text_percentage = f'Percentage: {percentage:.2f}%'

    # テキストをグレースケールの画像に描画
    cv2.putText(color_mask, text_area, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(color_mask, text_percentage, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # グレースケール画像を表示
    cv2.imshow("Result", color_mask)

    # パーセンテージに基づいてモーターを制御
    if percentage > 20:  # 例えば、色の割合が20%以上で前進
        move_forward()
    elif percentage < 5:  # 色の割合が5%以下で後退
        move_backward()
    else:
        stop()

    k = cv2.waitKey(1) & 0xFF
    if k == 27:  # 'ESC'キーで終了
        break

cv2.destroyAllWindows()
camera.stop()

# GPIOのクリーンアップ
p1.stop()
p2.stop()
p3.stop()
p4.stop()
GPIO.cleanup()