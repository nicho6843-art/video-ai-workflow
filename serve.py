#!/usr/bin/env python3
import http.server
import socketserver
import os
import webbrowser
import time

os.chdir(r"C:\Users\nicho.chen\video-ai-workflow")

PORT = 5000
Handler = http.server.SimpleHTTPRequestHandler

print("=" * 60)
print("🎬 视频AI自动配音工作流")
print("=" * 60)
print()
print(f"📍 应用地址: http://localhost:{PORT}")
print()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"✅ 服务器运行中...")
    print()

    # 打开浏览器
    time.sleep(1)
    try:
        webbrowser.open(f"http://localhost:{PORT}/index_complete.html")
    except:
        pass

    print("按 Ctrl+C 停止服务器")
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print("服务器已停止")
