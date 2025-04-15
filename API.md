# 猫検出録画システム API仕様書

## 📌 概要

このドキュメントでは、猫検出録画システムのWeb APIインターフェースについて説明します。
APIはRESTfulな設計に基づいており、JSONフォーマットでデータをやり取りします。

## 🔄 API エンドポイント

### 1. ダッシュボード表示

```http
GET /
```

メインダッシュボードのHTMLページを返します。

**レスポンス**:
- Content-Type: text/html
- ダッシュボードのHTMLコンテンツ

### 2. システム設定の取得・更新

#### 設定の取得
```http
GET /api/settings
```

**レスポンス**:
```json
{
  "camera": {
    "device_id": 0,
    "fps": 30,
    "resolution": {
      "width": 1280,
      "height": 720
    },
    "recording_duration": 60
  },
  "storage": {
    "recordings_dir": "recordings",
    "cat_videos_dir": "cat_videos",
    "models_dir": "models",
    "cat_images_dir": "cat_images",
    "max_storage_size": 1073741824
  },
  // ... 他の設定項目
}
```

#### 設定の更新
```http
POST /api/settings
```

**リクエストボディ**:
```json
{
  "camera": {
    "fps": 15,
    "resolution": {
      "width": 640,
      "height": 480
    }
  },
  // ... 更新したい設定項目
}
```

**レスポンス**:
```json
{
  "status": "success",
  "message": "Settings updated. Restarting modules: camera"
}
```

### 3. モデルファイルのアップロード

```http
POST /api/model
```

**リクエスト**:
- Content-Type: multipart/form-data
- フォームパラメータ: `model`（ファイル）

**レスポンス**:
```json
{
  "status": "success",
  "path": "models/new_model.pt",
  "message": "Model uploaded and processor restarted."
}
```

### 4. 動画ストリーミング

```http
GET /api/video/<folder>/<filename>
```

**パラメータ**:
- folder: "recordings" または "cat_videos"
- filename: 動画ファイル名

**レスポンス**:
- Content-Type: video/mp4
- 動画ファイルのストリーム

### 5. 最新の猫検出画像取得

```http
GET /api/latest_cat_image
```

**レスポンス**:
- Content-Type: image/jpeg
- 最新の猫検出画像

### 6. システム状態の取得

```http
GET /api/status
```

**レスポンス**:
```json
{
  "recording": true,
  "last_processed": "2025-04-14T10:30:00",
  "last_cat_detection": "2025-04-14T10:25:00",
  "storage_usage": {
    "recordings": 524288000,
    "cat_videos": 262144000
  },
  "restart_in_progress": false
}
```

### 7. モジュールの再起動

```http
POST /api/restart
```

**リクエストボディ**:
```json
{
  "modules": ["camera", "processor", "storage"]
}
```

**レスポンス**:
```json
{
  "status": "success",
  "message": "Restarting modules: camera, processor, storage"
}
```

## 🚨 エラーレスポンス

APIは以下の形式でエラーを返します：

```json
{
  "error": "エラーメッセージ"
}
```

### 主なHTTPステータスコード

- 200 OK: リクエスト成功
- 400 Bad Request: リクエストパラメータが不正
- 404 Not Found: リソースが見つからない
- 409 Conflict: 再起動中の重複リクエストなど
- 500 Internal Server Error: サーバー内部エラー

## 📝 注意事項

1. 設定変更時の注意
   - 一部の設定変更は関連モジュールの再起動を伴います
   - 再起動中は一時的にサービスが中断する可能性があります

2. ファイルアップロード
   - モデルファイルは.pt形式のみ対応
   - ファイルサイズの上限は100MB

3. レート制限
   - APIコールは1分間に60回まで
   - ストリーミングは同時に5接続まで