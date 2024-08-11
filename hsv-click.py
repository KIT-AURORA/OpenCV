import cv2
from picamera2 import Picamera2
import numpy as np

#クリックした箇所のHSVを取得して表示する関数
def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        
        pixel_value = frame_hsv[y, x]
        print("Clicked at (x={}, y={}) - HSV: {}".format(x, y, pixel_value))

# Picamera2を初期化。RGBフォーマット
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
camera.configure(camera_config)
camera.start()

# ウィンドウを作成し、位置と大きさを設定
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Camera", 1024, 768)  # ウィンドウサイズを1024x768に設定
cv2.moveWindow("Camera", 100, 50)  # ウィンドウ位置を(100, 50)に設定

#クリックしたときに関数の呼び出し
cv2.setMouseCallback("Camera", on_mouse_click)

while True:
    frame = camera.capture_array()
    
    # RGBからHSVに変換
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    
    cv2.imshow("Camera", frame)  # RGBで表示
    
    key = cv2.waitKey(1)
    if key == 27:  # Escキーでループを終了
        break

cv2.destroyAllWindows()
camera.stop()

