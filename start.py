#!/usr/bin/env python3
"""
简化启动脚本 - 直接运行此文件启动应用
"""

import subprocess
import sys
import os

def main():
    # 改变到项目目录
    project_dir = os.path.expanduser("~/video-ai-workflow")
    os.chdir(project_dir)

    print("🎬 正在启动视频AI自动配音工作流...")
    print()
    print("安装依赖中...")

    # 安装依赖
    dependencies = [
        "streamlit==1.40.0",
        "opencv-python==4.10.0.84",
        "anthropic==0.34.0",
        "pydantic==2.6.0",
        "python-dotenv==1.0.1",
        "pillow==10.2.0",
        "requests==2.31.0",
    ]

    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", dep])
        except:
            print(f"⚠️  安装 {dep} 失败，尝试继续...")

    print("✅ 依赖安装完成")
    print()
    print("🚀 启动 Streamlit 应用...")
    print()
    print("📍 应用地址: http://localhost:8501")
    print()

    # 启动 streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])

if __name__ == "__main__":
    main()
