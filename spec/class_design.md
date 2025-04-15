# 猫検出録画システム クラス設計書

## 🧱 クラス設計概要

### 1. `CameraRecorder`
- **責務**: 外部カメラから映像を取得し、指定された時間ごとに動画ファイルとして保存する
- **主なメソッド**:
  - `start_recording()`: 録画を開始する（スレッドで実行）
  - `stop_recording()`: 録画を停止する
  - `is_recording()`: 録画状態を確認する
- **備考**:
  - OpenCVの`cv2.VideoCapture`と`cv2.VideoWriter`を使用
  - 設定可能なパラメータ：デバイスID、解像度、FPS、録画時間
  - WebUIと共有されるインスタンスとして動作

### 2. `VideoProcessor`
- **責務**: 保存された動画ファイルからフレームを抽出し、物体検出を行う
- **主なメソッド**:
  - `process_new_videos()`: 新しい動画ファイルを処理する
  - `extract_frames(video_path)`: 動画から指定間隔でフレームを抽出する
  - `detect_objects(frames)`: 抽出したフレームに対して物体検出を行う
  - `classify_video(detection_results)`: 検出結果に基づき、動画を分類する
  - `get_latest_cat_image()`: 最新の猫検出画像を取得する
- **備考**:
  - Ultralytics YOLOモデルを使用
  - 猫検出画像を保存し、WebUIで表示可能

### 3. `StorageManager`
- **責務**: 各種ファイルの保存と容量管理を行う
- **主なメソッド**:
  - `get_total_size(path)`: 指定フォルダの合計容量を取得する
  - `check_and_cleanup()`: 全フォルダの容量をチェックし、必要に応じて古いファイルを削除する
  - `list_recordings()`: 録画中の動画一覧を取得する
  - `list_cat_videos()`: 保存された猫動画一覧を取得する
  - `save_model(path)`: 新しいモデルファイルを保存する
- **備考**:
  - 複数のフォルダ（recordings, cat_videos, cat_images, models）を管理
  - ファイルの作成日時を基に、削除対象を決定

### 4. `WebUI` (Flask Application)
- **責務**: システムの管理・監視インターフェースを提供する
- **主なエンドポイント**:
  - `/`: メインダッシュボード
  - `/api/settings`: 設定の取得・更新
  - `/api/model`: モデルファイルのアップロード
  - `/api/video/<folder>/<filename>`: 動画ストリーミング
  - `/api/latest_cat_image`: 最新の猫検出画像の取得
  - `/api/status`: システム状態の取得
  - `/api/restart`: モジュールの再起動
- **備考**:
  - Flaskを使用して構築
  - WebSocketを使用したリアルタイム更新
  - 各種コンポーネントと共有インスタンスを使用

### 5. `ConfigManager`
- **責務**: システム全体の設定を管理する
- **主なメソッド**:
  - `load_config()`: 設定ファイルから設定を読み込む
  - `save_config()`: 現在の設定をファイルに保存する
  - `get_setting(key)`: 特定の設定値を取得する
  - `set_setting(value, section, key)`: 特定の設定値を更新する
- **備考**:
  - YAML形式で設定を管理
  - 各種設定をセクション（camera, storage, processing, model, webui）で分類

### 6. `MainController`
- **責務**: 各コンポーネントを統括し、システム全体のフローを管理する
- **主なメソッド**:
  - `run()`: システムを起動し、各コンポーネントを初期化して連携させる
  - `shutdown()`: システムを安全に停止する
  - `_process_videos_loop()`: 動画処理ループを実行する（スレッドで実行）
  - `register_restart_handlers()`: 再起動ハンドラを登録する
- **備考**:
  - システムのエントリーポイント
  - 各コンポーネントのライフサイクルを管理
  - RestartManagerと連携して動的な再起動を実現

### 7. `RestartManager`
- **責務**: システムコンポーネントの動的な再起動を管理する
- **主なメソッド**:
  - `register_module(name, handler)`: 再起動可能なモジュールを登録する
  - `restart_modules(modules)`: 指定されたモジュールを再起動する
- **備考**:
  - シングルトンパターンを使用
  - 設定変更時の動的な再起動を実現
  - WebUIからの再起動要求を処理

## 🔄 クラス間の関係図（簡略化）

```plaintext
MainController
├── CameraRecorder ◄────┐
├── VideoProcessor ◄────┤
├── StorageManager ◄────┤
├── ConfigManager  ◄────┼── WebUI
└── RestartManager ◄────┘
```

## 🧩 デザインパターンの適用

- **シングルトンパターン**:
  - `ConfigManager`: システム全体で一つの設定を共有
  - `RestartManager`: システム全体で一つのインスタンスを使用
  - `CameraRecorder`: WebUIと共有される単一インスタンス

- **オブザーバーパターン**:
  - WebUIのステータス更新: システムの状態変更を監視し、WebUIに反映
  - 設定変更の通知: 設定変更時に関連モジュールに通知

- **ファクトリーパターン**:
  - `VideoProcessor`のYOLOモデルインスタンス化
  - モジュールの再起動時の新しいインスタンス生成

- **ストラテジーパターン**:
  - `StorageManager`の容量管理戦略
  - `VideoProcessor`の物体検出戦略

## 📁 ディレクトリ構成

```plaintext
cat_recorder/
├── camera/
│   └── recorder.py          # カメラ録画機能
├── processor/
│   └── video_processor.py   # 動画処理・物体検出
├── storage/
│   └── manager.py           # ファイル管理
├── webui/
│   ├── app.py              # Web UI実装
│   └── templates/
│       └── dashboard.html   # ダッシュボードテンプレート
├── config/
│   └── config_manager.py    # 設定管理
├── main_controller.py       # メインコントローラー
├── restart_manager.py       # 再起動管理
├── config.yaml             # 設定ファイル
├── requirements.txt        # 依存パッケージ
└── CONTINUOUS_RECORDER_README.md  # ドキュメント
```