from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from analysis import analyze_video_with_claude, generate_music_and_sfx_prompts
from db import init_db, save_analysis, get_analysis_history, get_analysis_by_id, delete_analysis

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# 初始化数据库
init_db()

# 确保上传目录存在
os.makedirs('data/videos', exist_ok=True)
os.makedirs('data/uploads', exist_ok=True)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析视频"""
    try:
        # 获取参数
        api_key = request.form.get('api_key')
        base_url = request.form.get('base_url', 'https://aiapi.uu.cc/v1')

        if not api_key:
            return jsonify({'error': '请提供 API Key'}), 400

        # 检查是否有文件上传
        if 'video' not in request.files:
            return jsonify({'error': '没有上传视频'}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        # 保存视频
        video_path = os.path.join('data/videos', file.filename)
        file.save(video_path)

        # 检查文件大小
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        if file_size > 500:
            os.remove(video_path)
            return jsonify({'error': '视频文件过大（>500MB）'}), 400

        # 分析视频
        analysis_result = analyze_video_with_claude(video_path, api_key, base_url)
        music_prompt, sfx_prompts = generate_music_and_sfx_prompts(analysis_result)

        # 保存到数据库
        save_analysis(file.filename, analysis_result, music_prompt, sfx_prompts, video_path)

        return jsonify({
            'success': True,
            'video_name': file.filename,
            'analysis': analysis_result,
            'music_prompt': music_prompt,
            'sfx_prompts': sfx_prompts
        })

    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.route('/api/history')
def history():
    """获取分析历史"""
    try:
        hist = get_analysis_history()
        return jsonify({'history': hist})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/<int:record_id>')
def get_history(record_id):
    """获取单条历史"""
    try:
        item = get_analysis_by_id(record_id)
        if item:
            return jsonify({'item': item})
        return jsonify({'error': '记录不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_history(record_id):
    """删除历史记录"""
    try:
        delete_analysis(record_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/<int:record_id>')
def export_report(record_id):
    """导出分析报告"""
    try:
        item = get_analysis_by_id(record_id)
        if not item:
            return jsonify({'error': '记录不存在'}), 404

        # 生成 JSON
        json_data = json.dumps(item['analysis_result'], ensure_ascii=False, indent=2)

        # 返回文件
        return jsonify({
            'success': True,
            'filename': f"{item['video_name']}_analysis.json",
            'data': json_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
