import time
import cv2
import numpy as np
from picamera2 import Picamera2

# カメラの初期設定
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
camera.configure(camera_config)
camera.start()

cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Result", 1280, 960)

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
    
    lower_red = np.array([hue_value-10, 100, 50])
    upper_red = np.array([hue_value+10, 255, 150])

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

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    if k == 27:
        break

cv2.destroyAllWindows()
camera.stop()