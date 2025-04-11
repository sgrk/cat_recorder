# Cat Recorder

A Python application that continuously records video from a camera, detects cats using a YOLO model, and saves videos containing cats to a separate folder.

[日本語の説明は下部にあります](#猫レコーダー)

## Features

- Continuous video recording from a camera in 1-minute segments
- Automatic cat detection using a custom YOLO model
- Separate storage for videos containing cats
- Automatic storage management (deletes old videos when storage limit is reached)
- Web UI for monitoring and configuration
- Configurable settings via YAML file

## Requirements

- Python 3.12
- External camera
- Dependencies:
  - opencv-python >= 4.8.0
  - ultralytics >= 8.0.0
  - flask >= 2.0.0
  - pyyaml >= 6.0.0
  - numpy >= 1.24.0

## Setup

1. Clone this repository
2. Run the setup script to create a virtual environment and install dependencies:
   ```
   0_setup_venv.bat
   ```
3. Activate the virtual environment:
   ```
   call .venv\Scripts\activate
   ```

## Usage

There are two ways to run the application:

### 1. Main Controller (Full System)

The main controller starts all system components including the camera recorder, video processor, storage manager, and web UI:

```
python main_controller.py
```

This will:
- Start recording videos from the camera
- Process videos to detect cats
- Move videos containing cats to the cat_videos folder
- Start the web UI for monitoring and configuration

### 2. Continuous Recorder (Simple Recording)

If you only want to record videos without cat detection:

```
python continuous_recorder.py
```

This will:
- Record videos in 1-minute segments
- Manage storage by deleting old videos when the limit is reached
- Save all videos to the recorded_videos folder

## Configuration

The system can be configured using the `config.yaml` file:

### Camera Settings
```yaml
camera:
  device_id: 0  # External camera device ID
  fps: 30
  resolution:
    width: 1280
    height: 720
  recording_duration: 60  # Duration of each video in seconds
```

### Storage Settings
```yaml
storage:
  recordings_dir: "recordings"
  cat_videos_dir: "cat_videos"
  models_dir: "models"
  max_storage_size: 1073741824  # 1GB in bytes
```

### Video Processing Settings
```yaml
processing:
  frame_interval: 30  # Extract every 30th frame
  cat_detection_threshold: 0.5  # 50% of frames must contain cats
  confidence_threshold: 0.5  # YOLO confidence threshold
```

### Model Settings
```yaml
model:
  path: "models/detect_kinako_best.pt"
  cat_class_id: 0
```

### Web UI Settings
```yaml
webui:
  host: "0.0.0.0"
  port: 50548
```

## Project Structure

```
cat_recorder/
├── camera/                # Camera recording module
│   └── recorder.py
├── config/                # Configuration management
│   └── config_manager.py
├── models/                # YOLO model files
│   └── detect_kinako_best.pt
├── processor/             # Video processing module
│   └── video_processor.py
├── storage/               # Storage management module
│   └── manager.py
├── webui/                 # Web UI module
│   ├── app.py
│   └── templates/
│       └── dashboard.html
├── recordings/            # Temporary video storage
├── cat_videos/            # Storage for videos with cats
├── 0_setup_venv.bat       # Setup script
├── cat_detector.py        # Cat detection using YOLO
├── config.yaml            # Configuration file
├── continuous_recorder.py # Simple continuous recording
├── main_controller.py     # Main application controller
└── requirements.txt       # Python dependencies
```

## How It Works

1. The system continuously records 1-minute video segments from the camera
2. Each video is processed to extract frames at regular intervals
3. A YOLO model analyzes the frames to detect cats
4. If more than 50% of the frames contain cats, the video is moved to the cat_videos folder
5. The system automatically manages storage by deleting old videos when the limit is reached
6. The web UI allows monitoring and configuration of the system

---

# 猫レコーダー

カメラから継続的に映像を録画し、YOLOモデルを使用して猫を検出し、猫が含まれる動画を別のフォルダに保存するPythonアプリケーションです。

## 機能

- カメラからの1分間セグメントでの継続的なビデオ録画
- カスタムYOLOモデルを使用した自動猫検出
- 猫が含まれる動画用の専用ストレージ
- 自動ストレージ管理（ストレージ制限に達すると古い動画を削除）
- 監視と設定用のWeb UI
- YAMLファイルによる設定可能なパラメータ

## 要件

- Python 3.12
- 外部カメラ
- 依存関係:
  - opencv-python >= 4.8.0
  - ultralytics >= 8.0.0
  - flask >= 2.0.0
  - pyyaml >= 6.0.0
  - numpy >= 1.24.0

## セットアップ

1. このリポジトリをクローンします
2. セットアップスクリプトを実行して仮想環境を作成し、依存関係をインストールします:
   ```
   0_setup_venv.bat
   ```
3. 仮想環境をアクティベートします:
   ```
   call .venv\Scripts\activate
   ```

## 使用方法

アプリケーションを実行する方法は2つあります:

### 1. メインコントローラー（フルシステム）

メインコントローラーはカメラレコーダー、ビデオプロセッサー、ストレージマネージャー、Web UIを含むすべてのシステムコンポーネントを起動します:

```
python main_controller.py
```

これにより:
- カメラからの動画の録画を開始します
- 猫を検出するために動画を処理します
- 猫が含まれる動画をcat_videosフォルダに移動します
- 監視と設定用のWeb UIを起動します

### 2. 連続レコーダー（シンプル録画）

猫検出なしで動画を録画するだけの場合:

```
python continuous_recorder.py
```

これにより:
- 1分間のセグメントで動画を録画します
- 制限に達すると古い動画を削除してストレージを管理します
- すべての動画をrecorded_videosフォルダに保存します

## 設定

システムは`config.yaml`ファイルを使用して設定できます:

### カメラ設定
```yaml
camera:
  device_id: 0  # 外部カメラデバイスID
  fps: 30
  resolution:
    width: 1280
    height: 720
  recording_duration: 60  # 各動画の秒単位の長さ
```

### ストレージ設定
```yaml
storage:
  recordings_dir: "recordings"
  cat_videos_dir: "cat_videos"
  models_dir: "models"
  max_storage_size: 1073741824  # 1GB（バイト単位）
```

### 動画処理設定
```yaml
processing:
  frame_interval: 30  # 30フレームごとに抽出
  cat_detection_threshold: 0.5  # フレームの50%以上に猫が含まれている必要がある
  confidence_threshold: 0.5  # YOLO信頼度しきい値
```

### モデル設定
```yaml
model:
  path: "models/detect_kinako_best.pt"
  cat_class_id: 0
```

### Web UI設定
```yaml
webui:
  host: "0.0.0.0"
  port: 50548
```

## プロジェクト構造

```
cat_recorder/
├── camera/                # カメラ録画モジュール
│   └── recorder.py
├── config/                # 設定管理
│   └── config_manager.py
├── models/                # YOLOモデルファイル
│   └── detect_kinako_best.pt
├── processor/             # 動画処理モジュール
│   └── video_processor.py
├── storage/               # ストレージ管理モジュール
│   └── manager.py
├── webui/                 # Web UIモジュール
│   ├── app.py
│   └── templates/
│       └── dashboard.html
├── recordings/            # 一時的な動画ストレージ
├── cat_videos/            # 猫が含まれる動画のストレージ
├── 0_setup_venv.bat       # セットアップスクリプト
├── cat_detector.py        # YOLOを使用した猫検出
├── config.yaml            # 設定ファイル
├── continuous_recorder.py # シンプルな連続録画
├── main_controller.py     # メインアプリケーションコントローラー
└── requirements.txt       # Python依存関係
```

## 動作の仕組み

1. システムはカメラから1分間の動画セグメントを継続的に録画します
2. 各動画は一定間隔でフレームを抽出するために処理されます
3. YOLOモデルがフレームを分析して猫を検出します
4. フレームの50%以上に猫が含まれている場合、動画はcat_videosフォルダに移動されます
5. システムは制限に達すると古い動画を削除して自動的にストレージを管理します
6. Web UIはシステムの監視と設定を可能にします
