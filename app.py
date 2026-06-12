import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
import cv2

from analysis import analyze_video_with_claude, generate_music_and_sfx_prompts
from db import init_db, save_analysis, get_analysis_history, get_analysis_by_id, delete_analysis

# 页面配置
st.set_page_config(
    page_title="视频AI配音系统",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎬 视频自动配音效工作流")
st.markdown("上传视频 → AI分析 → 生成音乐/音效提示词")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")

    api_key = st.text_input(
        "API Key",
        value=os.getenv("CLAUDE_API_KEY", ""),
        type="password",
        help="输入你的 Claude API Key（来自 aiapi.uu.cc）"
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
        # 验证 API 密钥
        if not api_key:
            st.error("❌ 请先在侧边栏输入 API Key")
            st.stop()

        # 保存临时视频文件
        os.makedirs("data/videos", exist_ok=True)
        video_path = f"data/videos/{uploaded_file.name}"

        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 检查视频时长
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = total_frames / fps if fps > 0 else 0
        cap.release()

        st.write(f"📹 视频时长: {duration_seconds:.1f} 秒")

        if duration_seconds > 300:
            st.error(f"❌ 视频超过 5 分钟 ({duration_seconds:.1f}s)，请上传更短的视频")
            os.remove(video_path)
            st.stop()

        # 分析按钮
        if st.button("🔍 开始分析", use_container_width=True, type="primary"):
            with st.spinner("🔄 正在分析视频..."):
                try:
                    # 第一步：视频分析
                    st.write("📊 正在提取关键帧...")
                    progress_bar = st.progress(0)

                    analysis_result = analyze_video_with_claude(
                        video_path, api_key, base_url
                    )

                    progress_bar.progress(50)
                    st.write("✅ 视频分析完成")

                    # 第二步：生成提示词
                    st.write("🎵 正在生成音乐/音效提示词...")
                    music_prompt, sfx_prompts = generate_music_and_sfx_prompts(
                        analysis_result
                    )

                    progress_bar.progress(100)

                    # 保存到数据库
                    save_analysis(
                        uploaded_file.name,
                        analysis_result,
                        music_prompt,
                        sfx_prompts,
                        video_path,
                    )

                    st.session_state.current_analysis = {
                        "video_name": uploaded_file.name,
                        "analysis_result": analysis_result,
                        "music_prompt": music_prompt,
                        "sfx_prompts": sfx_prompts,
                    }

                    st.success("✅ 分析完成！")

                except Exception as e:
                    st.error(f"❌ 分析失败: {str(e)}")

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
                        st.write("**音效生��提示词**:")
                        for sfx_name, sfx_prompt in segment.get(
                            "sfx_prompts", {}
                        ).items():
                            st.code(f"{sfx_name}: {sfx_prompt}", language="text")

        # 整体建议
        if "overall_suggestions" in result:
            suggestions = result["overall_suggestions"]
            with st.container(border=True):
                st.write("### 💡 整体建议")
                st.write(f"**视频节奏**: {suggestions.get('video_pacing', 'N/A')}")
                st.write(f"**BGM 使用**: {suggestions.get('recommended_bgm_placement', 'N/A')}")
                st.write(
                    f"**关键音效时刻**: {suggestions.get('critical_sfx_moments', 'N/A')}"
                )

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
            # 生成完整的提示词文档
            full_prompts = f"""视频: {analysis['video_name']}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【音乐生成提示词】
{music_prompt_text}

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
