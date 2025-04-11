# 猫検出録画システム クラス設計書

## 🧱 クラス設計概要

### 1. `CameraRecorder`
- **責務**: 外部カメラから映像を取得し、指定された時間ごとに動画ファイルとして保存する
- **主なメソッド**:
  - `start_recording()`: 録画を開始する
  - `stop_recording()`: 録画を停止する
  - `check_storage_limit()`: 保存先フォルダの容量をチェックし、制限を超えている場合は古いファイルを削除する
- **備考**: OpenCVの`cv2.VideoCapture`と`cv2.VideoWriter`を使用します

### 2. `VideoProcessor`
- **責務**: 保存された動画ファイルからフレームを抽出し、物体検出を行う
- **主なメソッド**:
  - `extract_frames(video_path)`: 動画から指定間隔でフレームを抽出する
  - `detect_objects(frames)`: 抽出したフレームに対して物体検出を行う
  - `classify_video(detection_results)`: 検出結果に基づき、動画を分類する
- **備考**: Ultralytics YOLOモデルを使用します

### 3. `StorageManager`
- **責務**: 動画ファイルの保存先フォルダの容量管理を行う
- **主なメソッド**:
  - `get_total_size()`: フォルダの合計容量を取得する
  - `delete_oldest_files()`: 容量制限を超えている場合、古いファイルを削除する
- **備考**: ファイルの作成日時を基に、削除対象を決定します

### 4. `WebUI`
- **責務**: ユーザーが設定を変更したり、モデルを更新したりするためのWebインターフェースを提供する
- **主なメソッド**:
  - `render_dashboard()`: 現在の設定やシステムの状態を表示する
  - `update_settings(new_settings)`: ユーザーからの設定変更を反映する
  - `upload_model(model_file)`: 新しいモデルファイルをアップロードする
- **備考**: FlaskまたはFastAPIを使用して構築します

### 5. `ConfigManager`
- **責務**: システム全体の設定を管理する
- **主なメソッド**:
  - `load_config()`: 設定ファイルから設定を読み込む
  - `save_config()`: 現在の設定をファイルに保存する
  - `get_setting(key)`: 特定の設定値を取得する
  - `set_setting(key, value)`: 特定の設定値を更新する
- **備考**: 設定ファイルはYAML形式で管理します

### 6. `MainController`
- **責務**: 各コンポーネントを統括し、システム全体のフローを管理する
- **主なメソッド**:
  - `run()`: システムを起動し、各コンポーネントを初期化して連携させる
  - `shutdown()`: システムを安全に停止する
- **備考**: このクラスはシステムのエントリーポイントとなります

## 🔄 クラス間の関係図（簡略化）

```plaintext
MainController
├── CameraRecorder
├── VideoProcessor
├── StorageManager
├── WebUI
└── ConfigManager
```

## 🧩 デザインパターンの適用

- **シングルトンパターン**: `ConfigManager`はシステム全体で一つの設定を共有するため、シングルトンパターンを適用します。

- **ファクトリーパターン**: `VideoProcessor`で使用するYOLOモデルのインスタンス化にファクトリーパターンを適用し、モデルの切り替えを容易にします。

- **ストラテジーパターン**: `StorageManager`の容量管理戦略を切り替え可能にするため、ストラテジーパターンを適用します。

## 📁 推奨ディレクトリ構成

```plaintext
project_root/
├── camera/
│   └── recorder.py
├── processor/
│   └── video_processor.py
├── storage/
│   └── manager.py
├── webui/
│   ├── app.py
│   └── templates/
├── config/
│   └── config_manager.py
├── main_controller.py
├── config.yaml
└── requirements.txt
```