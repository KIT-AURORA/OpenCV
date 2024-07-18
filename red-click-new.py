import cv2
from picamera2 import Picamera2
import numpy as np

def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel_value = frame[y, x]
        print("Clicked at (x={}, y={}) - RGB: {}".format(x, y, pixel_value[::-1]))

# Picamera2を初期化
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})  # 解像度を800x600に変更
picam2.configure(preview_config)
picam2.start()

# ウィンドウを作成し、位置と大きさを設定
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Camera", 1024, 768)  # ウィンドウサイズを1024x768に設定
cv2.moveWindow("Camera", 100, 50)  # ウィンドウ位置を(100, 50)に設定

cv2.setMouseCallback("Camera", on_mouse_click)

while True:
    frame = picam2.capture_array()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    cv2.imshow("Camera", frame_rgb)
    
    key = cv2.waitKey(1)
    if key == 27:  # Escキーでループを終了
        break

cv2.destroyAllWindows()
picam2.stop()