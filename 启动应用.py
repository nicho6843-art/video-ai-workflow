#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("=" * 50)
    print("🎬 视频AI自动配音工作流")
    print("=" * 50)
    print()

    # 进入项目目录
    project_dir = r"C:\Users\nicho.chen\video-ai-workflow"
    os.chdir(project_dir)
    print(f"📁 项目目录: {project_dir}")
    print()

    # 安装依赖
    print("📦 安装依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q",
            "streamlit", "anthropic", "pillow", "requests"
        ])
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

    print()
    print("=" * 50)
    print("🚀 启动 Streamlit 应用...")
    print("=" * 50)
    print()
    print("📍 应用地址: http://localhost:8501")
    print()
    print("⏳ 应用启动中，请稍候...")
    print()

    # 延迟打开浏览器
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:8501")
        print("🌐 浏览器已打开")
    except:
        print("💡 请手动打开浏览器访问: http://localhost:8501")

    print()

    # 启动 Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print()
        print("应用已关闭")

if __name__ == "__main__":
    main()
