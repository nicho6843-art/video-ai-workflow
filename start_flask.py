#!/usr/bin/env python3
import subprocess
import sys
import os
import webbrowser
import time

os.chdir(r"C:\Users\nicho.chen\video-ai-workflow")

print("=" * 60)
print("🎬 视频AI自动配音工作流 - Flask 版本")
print("=" * 60)
print()

print("📦 安装依赖...")
try:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        "flask", "anthropic", "pillow", "requests"
    ])
    print("✅ 依赖安装完成")
except:
    print("⚠️ 依赖安装遇到问题，尝试继续...")

print()
print("=" * 60)
print("🚀 启动应用...")
print("=" * 60)
print()
print("📍 应用地址: http://localhost:5000")
print()

time.sleep(2)
try:
    webbrowser.open("http://localhost:5000")
    print("🌐 浏览器已打开")
except:
    print("💡 请手动打开浏览器访问: http://localhost:5000")

print()
print("应用运行中... (按 Ctrl+C 停止)")
print()

# 启动 Flask
subprocess.run([sys.executable, "flask_app.py"])
