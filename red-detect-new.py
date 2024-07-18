import cv2
from picamera2 import Picamera2
import numpy as np

# Picamera2を初期化
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (400, 400)})
picam2.configure(preview_config)
picam2.start()

while True:
    # カメラから画像をキャプチャ
    im = picam2.capture_array()

    # 画像をHSVカラースペースに変換 
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    
    # 赤色の範囲を定義 (修正点2)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # 赤い領域だけを抽出するマスクを作成 
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # マスク内の輪郭を検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 赤い領域にバウンディングボックスを描画
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # ここに画像処理コードを追加する場合はこのコメント内に追加
    
    # 画像を表示
    cv2.imshow('Camera', im)
    
    # キー入力の待機
    key = cv2.waitKey(1)
    if key == 27:  # Escキーでループを終了
        break

# クリーンアップ
cv2.destroyAllWindows()
picam2.stop()