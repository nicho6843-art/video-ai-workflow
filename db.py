import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = "data/history/analysis_history.db"


def init_db():
    """初始化数据库"""
    os.makedirs("data/history", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_name TEXT NOT NULL,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        analysis_result TEXT NOT NULL,
        music_prompt TEXT,
        sfx_prompts TEXT,
        video_path TEXT
    )
    """
    )
    conn.commit()
    conn.close()


def save_analysis(video_name, analysis_result, music_prompt, sfx_prompts, video_path):
    """保存分析结果到数据库"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO analysis_history (video_name, analysis_result, music_prompt, sfx_prompts, video_path)
    VALUES (?, ?, ?, ?, ?)
    """,
        (
            video_name,
            json.dumps(analysis_result, ensure_ascii=False),
            music_prompt,
            json.dumps(sfx_prompts, ensure_ascii=False),
            video_path,
        ),
    )
    conn.commit()
    conn.close()


def get_analysis_history():
    """获取所有分析历史"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT id, video_name, upload_time, analysis_result, music_prompt, sfx_prompts
    FROM analysis_history
    ORDER BY upload_time DESC
    """
    )
    results = cursor.fetchall()
    conn.close()

    history = []
    for row in results:
        history.append(
            {
                "id": row[0],
                "video_name": row[1],
                "upload_time": row[2],
                "analysis_result": json.loads(row[3]),
                "music_prompt": row[4],
                "sfx_prompts": json.loads(row[5]),
            }
        )

    return history


def delete_analysis(analysis_id):
    """删除某个分析记录"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analysis_history WHERE id = ?", (analysis_id,))
    conn.commit()
    conn.close()


def get_analysis_by_id(analysis_id):
    """获取某个具体的分析记录"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT id, video_name, upload_time, analysis_result, music_prompt, sfx_prompts
    FROM analysis_history
    WHERE id = ?
    """,
        (analysis_id,),
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "id": result[0],
            "video_name": result[1],
            "upload_time": result[2],
            "analysis_result": json.loads(result[3]),
            "music_prompt": result[4],
            "sfx_prompts": json.loads(result[5]),
        }
    return None
