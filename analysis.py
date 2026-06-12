import cv2
import base64
import os
import json
from pathlib import Path
from anthropic import Anthropic
from typing import Optional


def extract_keyframes(video_path: str, sample_interval: float = 0.5) -> list[tuple[float, bytes]]:
    """
    从视频提取关键帧（智能采样）

    Args:
        video_path: 视频文件路径
        sample_interval: 采样间隔（秒）

    Returns:
        [(时间戳, 帧图像的base64), ...]
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_seconds = total_frames / fps

    keyframes = []
    frame_interval = int(fps * sample_interval)

    current_frame = 0
    while current_frame < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()

        if not ret:
            break

        # 压缩图像以减少 token 使用
        frame_resized = cv2.resize(frame, (640, 480))
        _, buffer = cv2.imencode(".jpg", frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 75])
        frame_b64 = base64.b64encode(buffer).decode("utf-8")

        timestamp = current_frame / fps
        keyframes.append((timestamp, frame_b64))

        current_frame += frame_interval

    cap.release()
    return keyframes


def analyze_video_with_claude(video_path: str, api_key: str, base_url: str) -> dict:
    """
    使用 Claude Vision 分析视频内容

    返回结构化的分析结果：
    {
        "video_summary": {...},
        "music_recommendation": {...},
        "timeline": [...]
    }
    """
    client = Anthropic(api_key=api_key, base_url=base_url)

    # 提取关键帧
    keyframes = extract_keyframes(video_path, sample_interval=0.5)

    if not keyframes:
        raise ValueError("无法从视频提取关键帧")

    # 构建 Claude Vision 消息
    content = [
        {
            "type": "text",
            "text": """你是一个专业的视频内容分析师和音乐制作人。请详细分析这个视频，并生成以下结构化数据：

1. **视频摘要**：
   - title: 视频的简短标题
   - main_theme: 主要主题/故事线
   - overall_emotion: 整体情感（可以多个，如"紧张、专业、感人"）
   - duration: 视频时长（秒）

2. **音乐推荐**：
   - style: 具体的音乐风格（不要泛泛而谈，要具体！比如"电影史诗配乐（弦乐为主）"而非"电影风格"）
   - tempo: 节奏速度（如"60-80 BPM，舒缓稳定"）
   - instrumentation: 建议使用的乐器（如"弦乐、钢琴、低音提琴"）
   - mood_descriptors: 情绪关键词（列表）
   - intensity: 强度等级（1-10）
   - key_characteristics: 关键特征描述
   - ai_prompt: 用于 AI 音乐生成的详细英文提示词（300字以上，包含：风格、情绪、节奏、乐器、结构、动态等）

3. **时间轴分析**（每0.5秒一个采样点）：
   对每一帧，返回以下信息：
   - timestamp: 时间戳（秒）
   - duration_estimate: 估计该场景持续时长（秒）
   - visual_description: 画面描述（简洁）
   - actions: 发生的动作/事件
   - emotion: 该段的情绪
   - sfx_needs: 需要的音效类型（列表，具体！比如"逼真的手机铃声"而非"音效"）
   - sfx_prompts: 每个音效的 AI 生成提示词（中文，具体描述音效的特征、节奏、音量、频率特征等）

4. **整体建议**：
   - video_pacing: 视频节奏描述
   - recommended_bgm_placement: 背景音乐的使用建议
   - critical_sfx_moments: 最需要音效的关键时刻

请生成 JSON 格式的输出，确保数据结构清晰、内容详细、有可操作性。""",
        }
    ]

    # 添加所有关键帧图像
    for idx, (timestamp, frame_b64) in enumerate(keyframes):
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": frame_b64,
                },
            }
        )
        content.append(
            {
                "type": "text",
                "text": f"[Frame {idx + 1} at {timestamp:.1f}s]",
            }
        )

    # 调用 Claude API
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{"role": "user", "content": content}],
    )

    response_text = message.content[0].text

    # 提取 JSON
    try:
        # 查找 JSON 块
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            analysis_result = json.loads(json_str)
        else:
            raise ValueError("无法从响应中提取 JSON")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {str(e)}\n\n响应内容: {response_text}")

    return analysis_result


def generate_music_and_sfx_prompts(analysis_result: dict) -> tuple[str, list[dict]]:
    """
    从分析结果生成详细的音乐和音效提示词

    Returns:
        (音乐提示词, [音效提示词列表])
    """
    music_rec = analysis_result.get("music_recommendation", {})
    timeline = analysis_result.get("timeline", [])

    # 构建音乐提示词
    music_prompt = music_rec.get(
        "ai_prompt",
        "A cinematic background music with emotional depth and professional quality.",
    )

    # 收集所有音效提示词
    sfx_prompts = []
    for segment in timeline:
        for sfx in segment.get("sfx_needs", []):
            sfx_data = {
                "timestamp": segment.get("timestamp"),
                "name": sfx,
                "prompt": segment.get("sfx_prompts", {}).get(
                    sfx, f"Sound effect: {sfx}"
                ),
            }
            sfx_prompts.append(sfx_data)

    return music_prompt, sfx_prompts
