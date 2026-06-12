#!/bin/bash

# 视频AI配音工作流启动脚本

echo "🎬 启动视频AI自动配音工作流..."
echo ""
echo "确保已安装依赖: pip install -r requirements.txt"
echo ""

# 检查是否有 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并配置 API Key"
    echo ""
    echo "cp .env.example .env"
    echo "然后编辑 .env 文件，输入你的 API 密钥"
    exit 1
fi

# 启动 Streamlit
echo "🚀 启动 Streamlit 服务..."
echo "🌐 打开浏览器访问: http://localhost:8501"
echo ""

streamlit run app.py
