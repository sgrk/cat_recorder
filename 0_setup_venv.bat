@echo off
chcp 65001

echo Ultrarytics環境整備 - 仮想環境セットアップ
echo ===============================================

REM 仮想環境のディレクトリ名
set VENV_DIR=.venv

REM 仮想環境が既に存在するか確認
if exist %VENV_DIR%\ (
    echo 仮想環境は既に存在します。
    exit /b 1
) else (
    echo 仮想環境を作成しています...
    py -3.12 -m venv %VENV_DIR%
    if errorlevel 1 (
        echo エラー: 仮想環境の作成に失敗しました。
        echo Python3.12がインストールされていることを確認してください。
        exit /b 1
    )
    echo 仮想環境を作成しました。
)

REM 仮想環境をアクティベート
echo 仮想環境をアクティベートしています...
call %VENV_DIR%\Scripts\activate

REM 必要なパッケージをインストール
echo 必要なパッケージをインストールしています...
python.exe -m pip install --upgrade pip
pip install pillow
pip install labelImg
pip install opencv-python
pip install ultralytics
pip uninstall torch torchvision
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo ===============================================
echo セットアップが完了しました。
echo 仮想環境を使用するには、以下のコマンドを実行してください:
echo   call %VENV_DIR%\Scripts\activate
echo .
echo 仮想環境を終了するには、以下のコマンドを実行してください:
echo   deactivate
echo ===============================================
pause
