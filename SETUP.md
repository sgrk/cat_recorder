# 猫検出録画システム セットアップガイド

## 📋 環境要件

### システム要件
- Python 3.8以上
- USBカメラまたはWebカメラ
- ストレージ空き容量: 2GB以上推奨
- 対応OS: Windows 10/11, Linux (Ubuntu 20.04以上), macOS

### 必要なパッケージ
- opencv-python >= 4.8.0: カメラ操作、画像処理
- ultralytics >= 8.0.0: YOLOモデルによる物体検出
- flask >= 2.0.0: Web UI
- pyyaml >= 6.0.0: 設定ファイル管理
- numpy >= 1.24.0: 数値計算、画像処理

## 🚀 インストール手順

1. リポジトリのクローン
```bash
git clone [repository-url]
cd cat_recorder
```

2. Python仮想環境の作成と有効化
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 必要なディレクトリの作成
```bash
mkdir -p recordings cat_videos models cat_images
```

## ⚙️ 設定

### 設定ファイル (config.yaml)

```yaml
# カメラ設定
camera:
  device_id: 0          # カメラデバイスID（通常、内蔵カメラは0、外付けは1以降）
  fps: 30               # フレームレート（推奨: 15-30）
  resolution:
    width: 1280         # 横解像度（推奨: 640-1920）
    height: 720         # 縦解像度（推奨: 480-1080）
  recording_duration: 60 # 1ファイルの録画時間（秒）

# ストレージ設定
storage:
  recordings_dir: "recordings"      # 録画ファイル保存先
  cat_videos_dir: "cat_videos"     # 猫動画保存先
  models_dir: "models"             # モデルファイル保存先
  cat_images_dir: "cat_images"     # 猫検出画像保存先
  max_storage_size: 1073741824     # 最大容量（バイト、デフォルト1GB）

# 動画処理設定
processing:
  frame_interval: 30    # フレーム抽出間隔（値が大きいほど処理が軽くなる）
  cat_detection_threshold: 0.5  # 猫検出の閾値（0.0-1.0）
  confidence_threshold: 0.5     # 検出信頼度の閾値（0.0-1.0）

# モデル設定
model:
  path: "models/detect_kinako_best.pt"  # 使用するモデルファイル
  cat_class_id: 0      # 猫のクラスID

# Web UI設定
webui:
  host: "0.0.0.0"      # ホスト（全てのインターフェースで受付）
  port: 54044          # ポート番号
```

### 設定のカスタマイズ
1. `config.yaml`をテキストエディタで開く
2. 必要に応じて各設定値を変更
3. 設定変更後はシステムの再起動が必要

## 🎮 起動方法

### 通常起動
```bash
python main_controller.py
```

### デバッグモードでの起動
```bash
# 詳細なログを表示
FLASK_ENV=development python main_controller.py
```

### バックグラウンド実行（Linux/macOS）
```bash
nohup python main_controller.py > cat_recorder.log 2>&1 &
```

## ✅ 動作確認

1. システム起動後、Webブラウザで以下のURLにアクセス:
```
http://localhost:54044
```

2. ダッシュボードが表示され、以下の項目を確認:
- カメラの録画状態
- ストレージ使用量
- 最新の猫検出画像
- 録画/保存済み動画一覧

## 🔍 トラブルシューティング

### カメラが認識されない場合
- デバイスIDが正しいか確認
- 他のアプリケーションがカメラを使用していないか確認
- USBカメラの場合、接続を確認

### Web UIにアクセスできない場合
- ポート番号が他のアプリケーションと競合していないか確認
- ファイアウォールの設定を確認
- `config.yaml`のホストとポート設定を確認

### メモリ使用量が高い場合
- `frame_interval`の値を大きくする
- 録画解像度を下げる
- 録画時間を短くする