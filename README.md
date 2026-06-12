# 视频 AI 自动配音效系统

一个使用 Claude Vision API 的视频内容分析和音乐、音效生成提示词的工作流。

## 功能特性

- 📤 **上传视频**：支持 mp4/mov/avi/mkv，时长限制 5 分钟
- 🔍 **AI 分析**：使用 Claude Vision 逐帧分析视频内容
- 📊 **细致报告**：
  - 视频摘要（标题、主题、整体情感）
  - 音乐推荐（具体风格、节奏、乐器、强度）
  - 时间轴分析（每 0.5 秒一个采样点）
  - 音效需求识别
- 🎼 **AI 提示词生成**：
  - 音乐生成提示词（可用于 Suno、爱声音坊等）
  - 音效生成提示词（每个音效都有具体描述）
- 💾 **历史记录**：SQLite 数据库保存所有分析
- 📥 **导出功能**：JSON 报告和完整提示词文本

## 安装

```bash
pip install -r requirements.txt
```

## 使用

### 本地运行

```bash
streamlit run app.py
```

然后在浏览器打开 `http://localhost:8501`

### 配置 API

在 Streamlit 应用的侧边栏输入：
- **API Key**: 你的 Claude API Key（来自 aiapi.uu.cc）
- **Base URL**: API 网关地址（默认 `https://aiapi.uu.cc/v1`）

或者设置环境变量：

```bash
export CLAUDE_API_KEY="your-api-key"
export CLAUDE_BASE_URL="https://aiapi.uu.cc/v1"
```

## 工作流

```
上传视频
    ↓
提取关键帧（每 0.5 秒采样）
    ↓
Claude Vision 分析
    ├─ 视频摘要
    ├─ 音乐推荐（细化到风格、节奏、乐器）
    ├─ 时间轴分析
    └─ 音效需求识别
    ↓
生成 AI 提示词
    ├─ 音乐生成提示词
    └─ 音效生成提示词
    ↓
保存到数据库
    ↓
展示结果 & 导出
```

## 数据库

- 位置：`data/history/analysis_history.db`
- 存储：视频名称、分析时间、完整分析结果、提示词

## 文件结构

```
video-ai-workflow/
├── app.py              # Streamlit 主应用
├── analysis.py         # 视频分析逻辑
├── db.py              # 数据库操作
├── requirements.txt    # 依赖
└── data/
    ├── videos/        # 上传的视频
    └── history/       # SQLite 数据库
```

## API 模型

使用 `claude-3-5-sonnet-20241022` 进行视频分析

## 输出示例

### 音乐推荐
```
风格: 电影史诗配乐（弦乐为主）
节奏: 60-80 BPM，舒缓稳定
乐器: 弦乐、钢琴、低音提琴
强度: 7/10
情绪: 严肃、专业、紧张
```

### AI 生成提示词
```
A cinematic orchestral background music featuring lush strings, 
piano, and subtle cello elements. The composition should convey 
professionalism and tension with a measured tempo around 70 BPM...
```

## 注意事项

- 视频超过 5 分钟会被拒绝
- 关键帧采样间隔为 0.5 秒（可在 `analysis.py` 中调整）
- Claude API 调用成本取决于视频长度和帧数
- 分析结果完全保存，可随时查看历史记录

## 后续集成

- 💾 [可选] 集成 Suno/爱声音坊 API 自动生成音乐
- 🎙️ [可选] 集成音效生成 API 自动生成音效
- 🎬 [可选] 自动视频混音和导出
