import cv2
from picamera2 import Picamera2
import numpy as np

# Picamera2を初期化
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)})
camera.configure(camera_config)
camera.start()

while True:
    # カメラから画像をキャプチャ
    image = camera.capture_array()

    # 画像をHSVカラースペースに変換 
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # 赤色の範囲を定義。S,Vは環境によって変わるので、範囲を大きくとっておいたほうが良い。
    lower_red = np.array([160, 100, 50])
    upper_red = np.array([180, 255, 150])
    
    # 赤い領域だけを抽出するマスクを作成 
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # マスク内の輪郭を検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 赤い領域にバウンディングボックスを描画
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    
    # 画像を表示
    cv2.imshow('Camera', image)
    
    # キー入力の待機
    key = cv2.waitKey(1)
    if key == 27:  # Escキーでループを終了
        break

# クリーンアップ
cv2.destroyAllWindows()
camera.stop()
