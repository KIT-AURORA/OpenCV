import cv2
import numpy as np
from picamera2 import Picamera2
import time

# HSV抽出関数
def hsvExtraction(image, hsvLower, hsvUpper):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # 画像をHSV色空間に変換
    hsv_mask = cv2.inRange(hsv, hsvLower, hsvUpper)  # 指定した範囲のマスクを作成
    result = cv2.bitwise_and(image, image, mask=hsv_mask)  # マスクを適用して結果を生成
    return result

# 赤色マスク取得関数
def red_masks_get(image):
    hsvLower_0 = np.array([0, 80, 100])
    hsvLower_1 = np.array([170, 80, 100])
    hsvUpper_0 = np.array([10, 255, 255])
    hsvUpper_1 = np.array([179, 255, 255])
    hsvResult_0 = hsvExtraction(image, hsvLower_0, hsvUpper_0)
    hsvResult_1 = hsvExtraction(image, hsvLower_1, hsvUpper_1)
    hsvResult = cv2.bitwise_or(hsvResult_0, hsvResult_1)  # 2つのマスクを結合
    return hsvResult

# グレースケール画像取得関数
def gray_get(image):
    img = red_masks_get(image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # グレースケールに変換
    return img_gray

# 二値画像取得関数
def binary_get(image):
    ret, img_binary = cv2.threshold(
        gray_get(image), 10, 255, cv2.THRESH_BINARY)  # 二値化処理
    return img_binary

# 占有率取得関数
def occ_get(image):
    pixel_number = np.size(binary_get(image))  # 総ピクセル数
    pixel_sum = np.sum(binary_get(image))  # 白ピクセルの合計値
    white_pixel_number = pixel_sum / 255  # 白ピクセルの数
    return white_pixel_number / pixel_number  # 占有率計算

# 重心取得関数
def center_get(image):
    mu = cv2.moments(binary_get(image), False)  # モーメント計算
    if mu["m00"] != 0:
        x, y = int(mu["m10"] / mu["m00"]), int(mu["m01"] / mu["m00"])  # 重心座標計算
        return [x, y]
    else:
        return [-20000, -20000]  # 重心がない場合のエラー値

# 画像サイズ取得関数（修正）
def size_get(image):
    height, width = image.shape[:2]
    return [width // 2, height // 2]  # 1/4サイズを返す

# 回転角取得関数
def rot_get(center, size, f_mm, diagonal_mm):
    if center != [-20000, -20000]:
        width_mm = diagonal_mm * size[0] / np.sqrt(size[0]**2 + size[1]**2)  # 画像の幅をミリメートルに変換
        sita_rad = np.arctan((width_mm * (size[0] / 2 - center[0]) / size[0]) / f_mm)  # 角度を計算
        sita = 180 * sita_rad / np.pi  # ラジアンを度に変換
        return sita
    else:
        return 404000  # エラー値

# メインプログラム
try:
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (1280, 720)})
    picam2.configure(preview_config)

    # 露出とISO感度を設定
    picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})

    picam2.start()
    time.sleep(0.1)
    
    while True:
        image = picam2.capture_array()
        
        # 画像を1/4サイズに縮小
        image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
        
        # 元の画像を表示
        cv2.imshow("Original", image)
        
        # HSV変換した画像を表示
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        cv2.imshow("HSV", hsv)
        
        # 赤色マスクを表示
        red_mask = red_masks_get(image)
        cv2.imshow("Red Mask", red_mask)
        
        # グレースケール画像を表示
        gray_image = gray_get(image)
        cv2.imshow("Grayscale", gray_image)
        
        # 二値化画像を表示
        binary_image = binary_get(image)
        cv2.imshow("Binary", binary_image)
        
        # 占有率を表示
        occ_rate = occ_get(image)
        print(f"占有率: {occ_rate:.2%}")
        
        # 重心を表示
        center = center_get(image)
        print(f"重心座標: {center}")
        
        # 回転角を表示
        size = size_get(image)
        f_mm = 5  # フォーカス距離を設定（mm）
        diagonal_mm = 7.2  # 撮像素子の対角線を設定（mm）
        rotation_angle = rot_get(center, size, f_mm, diagonal_mm)
        print(f"回転角: {rotation_angle:.2f} degrees")
        
        # 'esc'キーが押されたらループを抜ける
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    cv2.destroyAllWindows()
    picam2.stop()