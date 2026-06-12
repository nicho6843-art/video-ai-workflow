import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime

from db import init_db, save_analysis, get_analysis_history, get_analysis_by_id, delete_analysis

# 页面配置
st.set_page_config(
    page_title="视频AI配音系统",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎬 视频自动配音效工作流")
st.markdown("分析视频 → 生成音乐/音效提示词")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")

    api_key = st.text_input(
        "API Key",
        value=os.getenv("CLAUDE_API_KEY", ""),
        type="password",
        help="输入你的 Claude API Key"
    )

    base_url = st.text_input(
        "Base URL",
        value=os.getenv("CLAUDE_BASE_URL", "https://aiapi.uu.cc/v1"),
        help="API 网关地址"
    )

    st.divider()

    # 历史记录
    st.subheader("📋 分析历史")
    history = get_analysis_history()

    if history:
        st.write(f"共 {len(history)} 条记录")

        selected_history = st.selectbox(
            "选择历史记录查看",
            options=[h["id"] for h in history],
            format_func=lambda x: f"{[h for h in history if h['id']==x][0]['video_name']} ({[h for h in history if h['id']==x][0]['upload_time'][:19]})",
        )

        if selected_history:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👁️ 查看详情", use_container_width=True):
                    st.session_state.view_history = selected_history
            with col2:
                if st.button("🗑️ 删除记录", use_container_width=True):
                    delete_analysis(selected_history)
                    st.success("记录已删除")
                    st.rerun()
    else:
        st.info("暂无分析历史")

# 主要内容区域
tab1, tab2 = st.tabs(["📤 新建分析", "📚 历史详情"])

with tab1:
    st.subheader("上传视频进行分析")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "选择视频文件",
            type=["mp4", "mov", "avi", "mkv"],
            help="支持 mp4, mov, avi, mkv 格式，时长不超过 5 分钟"
        )

    with col2:
        st.metric("时长限制", "≤ 5 分钟")

    if uploaded_file:
        if st.button("📋 显示示例分析结果", use_container_width=True, type="primary"):
            # 显示示例结果
            st.session_state.current_analysis = {
                "video_name": uploaded_file.name,
                "analysis_result": {
                    "video_summary": {
                        "title": "示例视频分析",
                        "main_theme": "这是一个示例分析",
                        "overall_emotion": "专业、动感",
                        "duration": 120
                    },
                    "music_recommendation": {
                        "style": "现代电影配乐，弦乐和钢琴为主",
                        "tempo": "70-90 BPM，动感稳定",
                        "instrumentation": "弦乐、钢琴、低音提琴",
                        "mood_descriptors": ["专业", "动感", "现代"],
                        "intensity": 7,
                        "key_characteristics": "通过弦乐营造专业感，钢琴提供情感深度",
                        "ai_prompt": "A professional modern cinematic background music featuring lush strings (violins, violas, cellos) with piano melodies. Tempo around 80 BPM. The mood should convey professionalism, energy, and modernity. Suitable for corporate and business settings. The composition should have dynamic sections with building intensity..."
                    },
                    "timeline": [
                        {
                            "timestamp": 0,
                            "duration_estimate": 5,
                            "visual_description": "场景开始，展示主题",
                            "actions": "视觉介绍",
                            "emotion": "期待、吸引",
                            "sfx_needs": ["环境音"],
                            "sfx_prompts": {
                                "环境音": "轻微的背景环境音，营造专业感"
                            }
                        },
                        {
                            "timestamp": 5,
                            "duration_estimate": 10,
                            "visual_description": "核心内容展示",
                            "actions": "信息传递",
                            "emotion": "强调、重要",
                            "sfx_needs": ["转场音效"],
                            "sfx_prompts": {
                                "转场音效": "清晰的转场音效，强调场景切换"
                            }
                        }
                    ]
                },
                "music_prompt": "A professional modern cinematic background music featuring lush strings (violins, violas, cellos) with piano melodies. Tempo around 80 BPM. The mood should convey professionalism, energy, and modernity.",
                "sfx_prompts": [
                    {
                        "timestamp": 0,
                        "name": "环境音",
                        "prompt": "轻微的背景环境音，营造专业感"
                    },
                    {
                        "timestamp": 5,
                        "name": "转场音效",
                        "prompt": "清晰的转场音效，强调场景切换"
                    }
                ]
            }

            st.success("✅ 示例分析已加载")

    # 显示当前分析结果
    if "current_analysis" in st.session_state:
        analysis = st.session_state.current_analysis
        result = analysis["analysis_result"]

        st.divider()
        st.subheader("📊 分析结果")

        # 视频摘要
        summary = result.get("video_summary", {})
        with st.container(border=True):
            st.write("### 📺 视频摘要")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**标题**: {summary.get('title', 'N/A')}")
                st.write(f"**主题**: {summary.get('main_theme', 'N/A')}")
            with col2:
                st.write(f"**时长**: {summary.get('duration', 'N/A')}s")
                st.write(f"**整体情感**: {summary.get('overall_emotion', 'N/A')}")

        # 音乐推荐
        music_rec = result.get("music_recommendation", {})
        with st.container(border=True):
            st.write("### 🎵 音乐推荐")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**风格**: {music_rec.get('style', 'N/A')}")
                st.write(f"**节奏**: {music_rec.get('tempo', 'N/A')}")
                st.write(f"**乐器**: {music_rec.get('instrumentation', 'N/A')}")
            with col2:
                st.write(f"**强度**: {music_rec.get('intensity', 'N/A')}/10")
                st.write(f"**情绪**: {', '.join(music_rec.get('mood_descriptors', []))}")

            st.write("**关键特征**:")
            st.write(music_rec.get("key_characteristics", "N/A"))

        # 音乐生成提示词
        with st.container(border=True):
            st.write("### 🎼 AI 音乐生成提示词")
            music_prompt_text = analysis["music_prompt"]
            st.code(music_prompt_text, language="text")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📋 复制提示词",
                    data=music_prompt_text,
                    file_name="music_prompt.txt",
                    mime="text/plain",
                )
            with col2:
                st.write("💡 *可将此提示词输入到 Suno、爱声音坊或其他音乐生成工具*")

        # 时间轴分析
        st.write("### ⏱️ 时间轴分析")
        timeline = result.get("timeline", [])

        if timeline:
            for idx, segment in enumerate(timeline):
                with st.expander(
                    f"[{segment.get('timestamp', 0):.1f}s] {segment.get('visual_description', 'Scene')}",
                    expanded=False,
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**持续时长**: ~{segment.get('duration_estimate', 'N/A')}s")
                        st.write(f"**情绪**: {segment.get('emotion', 'N/A')}")
                        st.write(f"**发生事件**: {segment.get('actions', 'N/A')}")

                    with col2:
                        st.write(f"**需要音效**: {', '.join(segment.get('sfx_needs', []))}")

                    if segment.get("sfx_prompts"):
                        st.write("**音效生成提示词**:")
                        for sfx_name, sfx_prompt in segment.get(
                            "sfx_prompts", {}
                        ).items():
                            st.code(f"{sfx_name}: {sfx_prompt}", language="text")

        # 导出功能
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            json_data = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 导出分析报告 (JSON)",
                data=json_data,
                file_name=f"{analysis['video_name']}_analysis.json",
                mime="application/json",
            )

        with col2:
            full_prompts = f"""视频: {analysis['video_name']}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【音乐生成提示词】
{analysis["music_prompt"]}

【音效生成提示词】
"""
            for sfx_item in analysis["sfx_prompts"]:
                full_prompts += f"\n时间戳: {sfx_item['timestamp']}s\n名称: {sfx_item['name']}\n{sfx_item['prompt']}\n---\n"

            st.download_button(
                label="📥 导出完整提示词",
                data=full_prompts,
                file_name=f"{analysis['video_name']}_prompts.txt",
                mime="text/plain",
            )

        with col3:
            if st.button("🔄 重新分析", use_container_width=True):
                del st.session_state.current_analysis
                st.rerun()

with tab2:
    st.subheader("📚 查看历史分析")

    if "view_history" in st.session_state:
        history_id = st.session_state.view_history
        history_item = get_analysis_by_id(history_id)

        if history_item:
            st.write(f"**视频**: {history_item['video_name']}")
            st.write(f"**分析时间**: {history_item['upload_time']}")

            result = history_item["analysis_result"]

            # 显示与新建分析相同的内容格式
            summary = result.get("video_summary", {})
            with st.container(border=True):
                st.write("### 📺 视频摘要")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**标题**: {summary.get('title', 'N/A')}")
                    st.write(f"**主题**: {summary.get('main_theme', 'N/A')}")
                with col2:
                    st.write(f"**时长**: {summary.get('duration', 'N/A')}s")
                    st.write(f"**整体情感**: {summary.get('overall_emotion', 'N/A')}")

            music_rec = result.get("music_recommendation", {})
            with st.container(border=True):
                st.write("### 🎵 音乐推荐")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**风格**: {music_rec.get('style', 'N/A')}")
                    st.write(f"**节奏**: {music_rec.get('tempo', 'N/A')}")
                with col2:
                    st.write(f"**强度**: {music_rec.get('intensity', 'N/A')}/10")
                    st.write(f"**情绪**: {', '.join(music_rec.get('mood_descriptors', []))}")

            with st.container(border=True):
                st.write("### 🎼 音乐生成提示词")
                st.code(history_item["music_prompt"], language="text")

            timeline = result.get("timeline", [])
            st.write("### ⏱️ 时间轴分析")

            if timeline:
                for segment in timeline:
                    with st.expander(
                        f"[{segment.get('timestamp', 0):.1f}s] {segment.get('visual_description', 'Scene')}",
                        expanded=False,
                    ):
                        st.write(f"**情绪**: {segment.get('emotion', 'N/A')}")
                        st.write(f"**音效需求**: {', '.join(segment.get('sfx_needs', []))}")
                        if segment.get("sfx_prompts"):
                            for sfx_name, sfx_prompt in segment.get(
                                "sfx_prompts", {}
                            ).items():
                                st.code(f"{sfx_name}: {sfx_prompt}", language="text")

            # 导出按钮
            col1, col2 = st.columns(2)
            with col1:
                json_data = json.dumps(result, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 导出分析报告",
                    data=json_data,
                    file_name=f"{history_item['video_name']}_analysis.json",
                    mime="application/json",
                )

            with col2:
                if st.button("🗑️ 删除这条记录", use_container_width=True):
                    delete_analysis(history_id)
                    st.success("记录已删除")
                    del st.session_state.view_history
                    st.rerun()

        else:
            st.error("找不到该记录")
    else:
        st.info("在侧边栏选择一条历史记录查看详情")
