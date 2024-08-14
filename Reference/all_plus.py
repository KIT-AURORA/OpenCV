import time
#カメラ関係
import cv2
import numpy as np
#モーター関係
from gpiozero import Motor
from gpiozero.pins.pigpio import PiGPIOFactory
#距離センサ関係
import RPi.GPIO as GPIO

# DCモータの下準備============================*========
PIN_AIN1 = 18
PIN_AIN2 = 23
PIN_BIN1 = 24
PIN_BIN2 = 13

dcm_pins = {
    "left_forward": PIN_AIN2,
    "left_backward": PIN_AIN1,
    "right_forward": PIN_BIN2,
    "right_backward": PIN_BIN1,
}
# 初期化
factory = PiGPIOFactory()
motor_left = Motor( forward=dcm_pins["left_forward"],
                    backward=dcm_pins["left_backward"],
                    pin_factory=factory)
motor_right = Motor( forward=dcm_pins["right_forward"],
                     backward=dcm_pins["right_backward"],
                     pin_factory=factory)

def straight(speed):
    motor_left.value = speed
    motor_right.value = speed

def turn(speed):
    motor_left.value = speed
    motor_right.value = -speed

#距離センサ準備===========================================================
Trig = 27                           #変数"Trig"に27を代入
Echo = 19                           #変数"Echo"に19を代入

#GPIOの設定
GPIO.setmode(GPIO.BCM)              #GPIOのモードを"GPIO.BCM"に設定
GPIO.setup(Trig, GPIO.OUT)          #GPIO27を出力モードに設定
GPIO.setup(Echo, GPIO.IN)           #GPIO19を入力モードに設定

#HC-SR04で距離を測定する関数
def read_distance():
    GPIO.output(Trig, GPIO.HIGH)            #GPIO27の出力をHigh(3.3V)にする
    time.sleep(0.00001)                     #10μ秒間待つ
    GPIO.output(Trig, GPIO.LOW)             #GPIO27の出力をLow(0V)にする

    while GPIO.input(Echo) == GPIO.LOW:     #GPIO18がLowの時間
        sig_off = time.time()
    while GPIO.input(Echo) == GPIO.HIGH:    #GPIO18がHighの時間
        sig_on = time.time()

    duration = sig_on - sig_off             #GPIO18がHighしている時間を算術
    distance = duration * 34000 / 2         #距離を求める(cm)
    return distance

#カメラ準備===============================================================
#画像を縦に五分割して左から何番目の部分が一番赤色の部分が多いか判定する関数
def find_red_quadrant(image):
    #画像の高さと幅をタプルで返す
    height, width = image.shape[:2]
    quarter_width = width // 5

    # 画像をHSV形式に変換
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # HSV形式での赤色範囲を定義
    lower_red, upper_red = np.array([0, 50, 50]), np.array([10, 255, 255])

    # HSV画像から赤色のみを抽出するための閾値設定
    red_mask = cv2.inRange(hsv, lower_red, upper_red)

    # 赤のマスクを縦に4分割
    red_mask_1 = red_mask[ :, 0: quarter_width]
    red_mask_2 = red_mask[ :, quarter_width: 2 * quarter_width]
    red_mask_3 = red_mask[ :, 2 * quarter_width: 3 * quarter_width]
    red_mask_4 = red_mask[ :, 3 * quarter_width: 4 * quarter_width]
    red_mask_5 = red_mask[ :, 4 * quarter_width:]

    # 画像の各部に含まれる赤の割合
    red_percentage = np.sum(red_mask) 
    red_percentage_1 = np.sum(red_mask_1) 
    red_percentage_2 = np.sum(red_mask_2) 
    red_percentage_3 = np.sum(red_mask_3) 
    red_percentage_4 = np.sum(red_mask_4) 
    red_percentage_5 = np.sum(red_mask_5) 

    # 最も赤い部分を探す、赤い部分が十分多ければ0を返す、赤い部分が無ければ5を返す
    if red_percentage_1 == red_percentage_2 == red_percentage_3 == red_percentage_4:
        quadrant = 6
    else:
        red_pers = [red_percentage_1, red_percentage_2, red_percentage_3, red_percentage_4]
        quadrant = red_pers.index(max(red_pers)) + 1
    print(quadrant)
    return quadrant

if __name__ == '__main__':
    #連続して値を超音波センサの状態を読み取る
    while True:
        cm = read_distance()                   #HC-SR04で距離を測定する
        if cm > 2 and cm < 300:                #距離が2~400cmの場合
            print("distance=", int(cm), "cm")  #距離をint型で表示
            if cm < 10:
                print("Full Success Clear!!!")
            else:
                straight(0.5)
                time.sleep(t)#なんかいい感じにする
        time.sleep(1)                          #1秒間待つ

	
	
	
	
    camera = cv2.VideoCapture(0)
    while True:
        # Get the current frame
        ret, image = camera.read()
        # Break if the image is not obtained
        if not ret:
            break
        # Get the current timestamp
        timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        cv2.imwrite(timestamp + ".jpg", image)
        print("photo ok")
        
        image_num = find_red_quadrant(image)
        if image_num ==1:
            #左に強く旋回、具体的値を実験で決定
            time.sleep(2)
        elif image_num ==2:
            #左に弱く旋回、具体的値を実験で決定
            time.sleep(2)
        elif image_num ==3:
            #右に弱く旋回、具体的値を実験で決定
            time.sleep(2)
        elif image_num ==4:
            #右に強く旋回、具体的値を実験で決定
            time.sleep(2)
        else:
            time.sleep(2)

    camera.release()
    cv2.destroyAllWindows()