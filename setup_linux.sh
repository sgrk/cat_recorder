#!/bin/bash

# エラーが発生したら停止
set -e

# 色付きの出力用の関数
print_info() {
    echo -e "\e[1;34m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[1;32m[SUCCESS]\e[0m $1"
}

print_error() {
    echo -e "\e[1;31m[ERROR]\e[0m $1"
}

# root権限チェック
if [ "$EUID" -ne 0 ]; then
    print_error "このスクリプトはroot権限で実行してください。"
    print_info "実行方法: sudo $0"
    exit 1
fi

# ユーザー名の取得
SUDO_USER_NAME=${SUDO_USER:-${USER}}
if [ "$SUDO_USER_NAME" = "root" ]; then
    print_error "rootユーザーではなく、sudo権限を持つ通常ユーザーで実行してください。"
    exit 1
fi

# インストールディレクトリの設定
INSTALL_DIR="/opt/cat_recorder"
USER_HOME=$(eval echo ~$SUDO_USER_NAME)
CONFIG_DIR="$USER_HOME/.config/cat_recorder"

print_info "猫検出録画システムのセットアップを開始します..."

# 必要なシステムパッケージのインストール
print_info "システムパッケージをインストールしています..."
apt-get update
apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    v4l-utils \
    ffmpeg \
    git

# インストールディレクトリの作成
print_info "インストールディレクトリを作成しています..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# 現在のディレクトリのファイルをインストールディレクトリにコピー
print_info "ファイルをコピーしています..."
cp -r ./* "$INSTALL_DIR/"

# Python仮想環境の作成
print_info "Python仮想環境を作成しています..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# 必要なPythonパッケージのインストール
print_info "Pythonパッケージをインストールしています..."
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"

# 必要なディレクトリの作成
print_info "データディレクトリを作成しています..."
mkdir -p "$CONFIG_DIR/"{recordings,cat_videos,models,cat_images}

# 設定ファイルの初期化
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    print_info "設定ファイルを初期化しています..."
    cp "$INSTALL_DIR/config.yaml" "$CONFIG_DIR/config.yaml"
    # 設定ファイルのパスを更新
    sed -i "s|recordings_dir: \"recordings\"|recordings_dir: \"$CONFIG_DIR/recordings\"|" "$CONFIG_DIR/config.yaml"
    sed -i "s|cat_videos_dir: \"cat_videos\"|cat_videos_dir: \"$CONFIG_DIR/cat_videos\"|" "$CONFIG_DIR/config.yaml"
    sed -i "s|models_dir: \"models\"|models_dir: \"$CONFIG_DIR/models\"|" "$CONFIG_DIR/config.yaml"
    sed -i "s|cat_images_dir: \"cat_images\"|cat_images_dir: \"$CONFIG_DIR/cat_images\"|" "$CONFIG_DIR/config.yaml"
fi

# カメラデバイスの権限設定
print_info "カメラデバイスの権限を設定しています..."
if ! groups "$SUDO_USER_NAME" | grep -q "video"; then
    usermod -a -G video "$SUDO_USER_NAME"
fi

# 所有者とパーミッションの設定
print_info "ファイルの権限を設定しています..."
chown -R "$SUDO_USER_NAME:$SUDO_USER_NAME" "$INSTALL_DIR"
chown -R "$SUDO_USER_NAME:$SUDO_USER_NAME" "$CONFIG_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod -R 755 "$CONFIG_DIR"

# systemdサービスの設定
print_info "systemdサービスを設定しています..."
cat > /etc/systemd/system/cat-recorder.service << EOL
[Unit]
Description=Cat Detection Recording System
After=network.target

[Service]
Type=simple
User=$SUDO_USER_NAME
Group=$SUDO_USER_NAME
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main_controller.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# サービスの有効化
systemctl daemon-reload
systemctl enable cat-recorder.service

# 起動スクリプトの作成
print_info "起動スクリプトを作成しています..."
cat > "$INSTALL_DIR/start.sh" << EOL
#!/bin/bash
source "$INSTALL_DIR/venv/bin/activate"
python "$INSTALL_DIR/main_controller.py"
EOL

chmod +x "$INSTALL_DIR/start.sh"

# 完了メッセージ
print_success "セットアップが完了しました！"
echo
print_info "システムの使用方法:"
echo "1. サービスとして起動する場合:"
echo "   sudo systemctl start cat-recorder"
echo
echo "2. 手動で起動する場合:"
echo "   $INSTALL_DIR/start.sh"
echo
echo "3. 設定ファイルの場所:"
echo "   $CONFIG_DIR/config.yaml"
echo
echo "4. ログの確認:"
echo "   sudo journalctl -u cat-recorder -f"
echo
print_info "Webインターフェース:"
echo "ブラウザで以下のURLにアクセスしてください:"
echo "http://localhost:54044"
echo
print_info "トラブルシューティング:"
echo "詳細は $INSTALL_DIR/TROUBLESHOOTING.md を参照してください"