#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir(r"C:\Users\nicho.chen\video-ai-workflow")

print("=" * 60)
print("🎬 视频AI自动配音工作流")
print("=" * 60)
print()

# 安装依赖
print("📦 安装依赖（如果需要）...")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "streamlit", "anthropic", "pillow", "requests"], check=True)
    print("✅ 依赖准备完成")
except Exception as e:
    print(f"❌ 依赖安装失败: {e}")
    print()
    input("按 Enter 退出...")
    sys.exit(1)

print()
print("🚀 启动应用...")
print("📍 访问地址: http://localhost:8501")
print()
print("=" * 60)
print()

try:
    # 启动 streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"], check=True)
except KeyboardInterrupt:
    print()
    print("应用已关闭")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    print()
    input("按 Enter 退出...")
    sys.exit(1)

