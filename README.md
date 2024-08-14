# OpenCV
大幅にコード書き換え、不要なものは削除しました（8/11）。色の反転も解決したはず。
カラーコーンのHueは120付近。ネットや本に書いている値と大きくずれるが、理由は不明。もしかしたら色々間違っているかも。
パラメーターも調整が必要。修正あったらブランチ切ってアップロードお願いします。

# ファイル説明

| ファイル名 | 説明 |
| --- | --- |
| hsv-click.py | 画像を表示し、クリックした場所の色を表示。テキスト欄にHSVの値を表示 |
| red_box.py | 赤色を検出してボックスで囲むファイル。HSVの値は調整する必要あり|
| hsv-tester.py | ・元画像・HSVの変換画像・指定したHSVのマスキング・切り抜き画像、の4つを表示。HSVをメインコードに使うなら、hsv-click.pyで数値の見当を付け、このコードでテスト|
| ht_area.py | 'hsv_tester.py'で行ったグレースケールの面積をピクセル数で画面に表示するもの |
| ht_percent.py | 'hsv_tester.py'で行ったグレースケールの面積が全体の何パーセントを占めるかを表示するもの |
| ht_color.py | 'hsv_percent.py'で表示されたパーセントの値を50％以上であれば緑、未満であれば赤色に表示するコードにしたかった |
| ht_color2.py | 'ht_color.py'をグレースケールのみ表示 |
