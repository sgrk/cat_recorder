# 猫検出録画システム トラブルシューティングガイド

## 📋 目次

1. [一般的な問題](#一般的な問題)
2. [カメラ関連の問題](#カメラ関連の問題)
3. [物体検出の問題](#物体検出の問題)
4. [ストレージの問題](#ストレージの問題)
5. [Web UI関連の問題](#web-ui関連の問題)
6. [パフォーマンスの問題](#パフォーマンスの問題)
7. [ログの見方](#ログの見方)

## 一般的な問題

### システムが起動しない

**症状**:
- `python main_controller.py`を実行しても正常に起動しない
- エラーメッセージが表示される

**確認項目**:
1. Python環境
```bash
python --version  # 3.8以上であることを確認
```

2. 依存パッケージ
```bash
pip list  # 必要なパッケージがインストールされているか確認
```

3. 設定ファイル
```bash
cat config.yaml  # 設定ファイルの構文エラーがないか確認
```

**解決方法**:
1. 仮想環境の再作成
```bash
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 設定ファイルの再設定
```bash
cp config.yaml config.yaml.bak  # バックアップ
cp config.yaml.example config.yaml  # デフォルト設定で上書き
```

## カメラ関連の問題

### カメラが認識されない

**症状**:
- "Failed to open camera"エラー
- 黒い画面のみ表示される

**確認項目**:
1. カメラの接続状態
```bash
ls -l /dev/video*  # Linux
```

2. カメラのデバイスID
```python
import cv2
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i} is available")
    cap.release()
```

**解決方法**:
1. config.yamlのdevice_idを正しい値に設定
2. 他のアプリケーションのカメラ使用を終了
3. USBケーブルの抜き差し
4. OSの再起動

### 録画が途中で停止する

**症状**:
- 録画が不規則に停止する
- エラーログに"Camera disconnected"などが表示される

**解決方法**:
1. USBポートの変更
2. カメラのドライバーアップデート
3. recording_durationを短くする（30秒程度）

## 物体検出の問題

### 猫の検出精度が低い

**症状**:
- 猫が写っているのに検出されない
- 誤検出が多い

**確認項目**:
1. 検出設定
```yaml
processing:
  confidence_threshold: 0.5  # 閾値を下げると検出されやすくなる
  cat_detection_threshold: 0.5
```

2. 画像品質
```yaml
camera:
  resolution:
    width: 1280  # 解像度を上げると精度が向上する可能性
    height: 720
```

**解決方法**:
1. confidence_thresholdの調整（0.3-0.7の範囲で試行）
2. frame_intervalの調整（値を小さくすると検出機会が増える）
3. 照明条件の改善
4. カメラの位置や角度の調整

## ストレージの問題

### ディスク容量の急激な増加

**症状**:
- ストレージ使用量が急速に増加
- "Disk full"エラー

**確認項目**:
1. 現在の使用量
```bash
du -h recordings/ cat_videos/ cat_images/
```

2. 設定値
```yaml
storage:
  max_storage_size: 1073741824  # 1GB
```

**解決方法**:
1. 不要なファイルの手動削除
```bash
find recordings/ -type f -mtime +7 -delete  # 7日以上前のファイルを削除
```

2. max_storage_sizeの調整
3. recording_durationの短縮

## Web UI関連の問題

### Web UIにアクセスできない

**症状**:
- "Connection refused"エラー
- ページが読み込めない

**確認項目**:
1. サーバー状態
```bash
netstat -an | grep 54044  # ポートの使用状況確認
```

2. ファイアウォール設定
```bash
sudo ufw status  # Ubuntu
```

**解決方法**:
1. ポート番号の変更
2. ファイアウォールの設定変更
3. `host: "0.0.0.0"`の確認

### ダッシュボードの表示が更新されない

**症状**:
- ステータス情報が古いまま
- リアルタイム更新が機能しない

**解決方法**:
1. ブラウザのキャッシュクリア
2. ページの強制リロード
3. 別のブラウザでの試行

## パフォーマンスの問題

### CPU使用率が高い

**症状**:
- システムの応答が遅い
- ファンの回転が激しい

**確認項目**:
1. プロセス状態
```bash
top -p $(pgrep -f main_controller)
```

2. 設定値
```yaml
processing:
  frame_interval: 30  # 値を大きくすると負荷が下がる
```

**解決方法**:
1. frame_intervalの増加（30→60）
2. 解像度の低下
3. confidence_thresholdの引き上げ

### メモリ使用量が増加する

**症状**:
- メモリ使用量が時間とともに増加
- システムが遅くなる

**確認項目**:
```bash
ps aux | grep main_controller  # メモリ使用量の確認
```

**解決方法**:
1. 定期的なシステム再起動
2. 古いログファイルの削除
3. 画像キャッシュのクリア

## ログの見方

### ログファイルの場所
- システムログ: `cat_recorder.log`
- エラーログ: `stderr.log`

### 主なログメッセージと意味

```
[INFO] Camera recording started
→ カメラの録画開始

[ERROR] Failed to open camera (device_id: 0)
→ カメラのオープンに失敗

[WARNING] Storage limit exceeded
→ ストレージ制限に到達

[INFO] Cat detected in video: {filename}
→ 猫の検出成功

[ERROR] Model inference failed
→ 物体検出処理の失敗
```

### デバッグモードの有効化

```bash
FLASK_ENV=development python main_controller.py
```

これにより：
- 詳細なログ出力
- エラーのトレースバック
- リアルタイムのログ表示