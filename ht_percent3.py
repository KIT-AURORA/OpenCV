import time
import cv2
import numpy as np
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# GPIOのセットアップ
LED_PIN = 22  # 使用するGPIOピン
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def blink_led(times):
    """LEDを指定した回数点滅させる"""
    for _ in range(times):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.5)

def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

# カメラの初期設定
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
camera.configure(camera_config)
camera.start()

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Result", 1280, 960)

# 前回の白い部分の面積
previous_white_area = 0

while True:
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
        result = cv2.bitwise_and(image, image, mask=color_mask)

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
        
        # 画像を結合して表示
        stacked_images = stackImages(0.8, ([image, hsv], [color_mask, result]))
        cv2.imshow("Result", stacked_images)

        # 白い部分の面積が前回よりも増加していればLEDを2回点滅、減少していれば1回点滅
        if white_area > previous_white_area:
            blink_led(2)
        elif white_area < previous_white_area:
            blink_led(1)

        # 現在の白い面積を次回の比較用に保存
        previous_white_area = white_area

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    if k == 27:
        break

cv2.destroyAllWindows()
camera.stop()
GPIO.cleanup()  # GPIOを解放