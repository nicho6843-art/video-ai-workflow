import base64
import json
from anthropic import Anthropic
from typing import Optional


def analyze_video_with_claude(video_path: str, api_key: str, base_url: str) -> dict:
    """
    使用 Claude Vision 分析视频内容
    """
    client = Anthropic(api_key=api_key, base_url=base_url)

    # 读取视频文件为 base64
    with open(video_path, "rb") as f:
        video_data = f.read()

    video_b64 = base64.b64encode(video_data).decode("utf-8")

    # 构建 Claude Vision 消息
    content = [
        {
            "type": "text",
            "text": """你是一个专业的视频内容分析师。请分析这个视频，并生成以下 JSON 结构的分析结果：

{
  "video_summary": {
    "title": "视频标题",
    "main_theme": "主要主题",
    "overall_emotion": "整体情感（多个情感用、分隔）",
    "duration": 120
  },
  "music_recommendation": {
    "style": "具体的音乐风格（如：电影史诗配乐、弦乐为主）",
    "tempo": "节奏速度（如：60-80 BPM）",
    "instrumentation": "建议的乐器",
    "mood_descriptors": ["情绪1", "情绪2"],
    "intensity": 7,
    "key_characteristics": "关键特征描述",
    "ai_prompt": "用于 AI 音乐生成的英文提示词（300字以上）"
  },
  "timeline": [
    {
      "timestamp": 0,
      "duration_estimate": 5,
      "visual_description": "画面描述",
      "actions": "发生的动作",
      "emotion": "情绪",
      "sfx_needs": ["音效1", "音效2"],
      "sfx_prompts": {
        "音效1": "音效描述"
      }
    }
  ]
}

请仔细分析视频内容，确保数据详细、具体、可操作。""",
        },
        {
            "type": "video",
            "source": {
                "type": "base64",
                "media_type": "video/mp4",
                "data": video_b64,
            },
        },
    ]

    # 调用 Claude API
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{"role": "user", "content": content}],
    )

    response_text = message.content[0].text

    # 提取 JSON
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            analysis_result = json.loads(json_str)
        else:
            raise ValueError("无法从响应中提取 JSON")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {str(e)}")

    return analysis_result


def generate_music_and_sfx_prompts(analysis_result: dict) -> tuple[str, list[dict]]:
    """
    从分析结果生成详细的音乐和音效提示词
    """
    music_rec = analysis_result.get("music_recommendation", {})
    timeline = analysis_result.get("timeline", [])

    music_prompt = music_rec.get(
        "ai_prompt",
        "A cinematic background music with emotional depth and professional quality.",
    )

    sfx_prompts = []
    for segment in timeline:
        for sfx in segment.get("sfx_needs", []):
            sfx_data = {
                "timestamp": segment.get("timestamp"),
                "name": sfx,
                "prompt": segment.get("sfx_prompts", {}).get(sfx, f"Sound effect: {sfx}"),
            }
            sfx_prompts.append(sfx_data)

    return music_prompt, sfx_prompts
