@echo off
chcp 65001 >nul
echo 视频AI自动配音工作流启动脚本
echo.

REM 检查 Python
echo 正在检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到 python 命令
    echo.
    echo 尝试用 python3...
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ 找不到 python3 命令
        echo.
        echo 请确保 Python 已安装并添加到系统 PATH
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

echo ✅ 找到 Python
echo.

cd /d C:\Users\nicho.chen\video-ai-workflow

echo 安装依赖...
%PYTHON% -m pip install -q streamlit anthropic pillow requests

if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成
echo.
echo 🚀 启动应用...
echo.
echo 📍 应用地址: http://localhost:8501
echo.
echo 请等待浏览器打开...
echo.

%PYTHON% -m streamlit run app.py --server.port 8501

pause
