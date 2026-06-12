# 🎬 视频AI自动配音工作流 - 快速开始指南

## 第一步：环境准备

### 1. 克隆/下载项目到本地
```bash
cd ~/video-ai-workflow
```

### 2. 安装依赖（推荐使用 Python 3.9+）

**使用 pip：**
```bash
pip install -r requirements.txt
```

**或使用 conda：**
```bash
conda create -n video-ai python=3.9
conda activate video-ai
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 信息：
```
CLAUDE_API_KEY=sk-your-api-key-here
CLAUDE_BASE_URL=https://aiapi.uu.cc/v1
```

> 💡 提示：也可以在 Streamlit 应用的侧边栏直接输入 API Key，不用 `.env` 文件

---

## 第二步：启动应用

### 方法 A：直接运行（推荐）

```bash
streamlit run app.py
```

应用会自动在浏览器打开，地址：`http://localhost:8501`

### 方法 B：使用启动脚本

```bash
bash run.sh
```

---

## 第三步：使用应用

### 🎯 完整工作流

#### 1️⃣ **上传视频**
- 在"📤 新建分析"标签页中上传视频
- 支持格式：MP4, MOV, AVI, MKV
- 时长限制：≤ 5 分钟
- 应用会自动检查视频时长

#### 2️⃣ **开始分析**
- 点击"🔍 开始分析"按钮
- 应用会：
  - 🎬 提取关键帧（每 0.5 秒采样）
  - 👁️ 上传到 Claude Vision API
  - 🧠 进行深度视频内容分析
  - 📊 生成结构化分析报告

#### 3️⃣ **查看分析结果**

应用会展示：

**📺 视频摘要**
- 视频标题
- 主要主题
- 整体情感
- 视频时长

**🎵 音乐推荐**（非常详细！）
- 具体的音乐风格（如"电影史诗配乐、弦乐为主"）
- 建议的节奏（BPM 范围）
- 推荐的乐器组合
- 情绪关键词
- 强度等级（1-10）
- 关键特征描述

**🎼 AI 音乐生成提示词**
- 长 300+ 字的英文提示词
- 包含：风格、情绪、节奏、乐器、结构等所有细节
- **可直接复制到 Suno/爱声音坊/Google Lyria 等工具**

**⏱️ 时间轴分析**
- 每个关键场景（~0.5-1秒）的详细分析
- 包含：
  - 画面描述
  - 发生的动作/事件
  - 当前情绪
  - 需要的音效（具体！如"逼真的手机铃声"）
  - 每个音效的 AI 生成提示词

#### 4️⃣ **导出和使用提示词**

**两种导出方式：**

1. **分析报告 (JSON)**
   - 包含完整的结构化分析结果
   - 可用于二次开发或存档

2. **完整提示词文档 (TXT)**
   - 包含所有音乐和音效的 AI 生成提示词
   - 可直接用于各种 AI 工具

**接下来的步骤：**

```
复制提示词
  ↓
粘贴到 Suno/爱声音坊/Google Lyria（音乐）
粘贴到 Adobe Firefly/爱声音坊（音效）
  ↓
生成音乐和音效
  ↓
在视频编辑软件中合成
```

---

## 第四步：查看历史记录

### 在侧边栏查看历史
- 所有分析都自动保存到本地数据库
- 侧边栏显示最近的分析
- 可以查看、导出或删除任何历史记录

### 查看历史详情
- 切换到"📚 历史详情"标签页
- 从侧边栏选择一条记录
- 查看完整的分析和提示词

---

## 💡 高级使用技巧

### 1. 调整关键帧采样率
编辑 `analysis.py` 中的 `extract_keyframes` 函数：

```python
keyframes = extract_keyframes(video_path, sample_interval=0.5)
# 改为 1.0 = 每 1 秒采样一帧（更快，但精度降低）
# 改为 0.3 = 每 0.3 秒采样一帧（更详细，但成本增加）
```

### 2. 修改分析 prompt
编辑 `analysis.py` 中的分析 prompt，定制分析内容

### 3. 集成其他 API
准备好集成爱声音坊/Suno API 时，可以添加到 `app.py` 中

---

## 🔧 故障排查

### 问题 1: "API Key 无效"
- ✅ 检查 `.env` 文件中的 API Key 是否正确
- ✅ 确保没有多余的空格或换行符
- ✅ 也可以直接在 Streamlit 侧边栏输入 API Key

### 问题 2: "视频上传失败"
- ✅ 确保视频格式支持（MP4, MOV, AVI, MKV）
- ✅ 确保视频时长 ≤ 5 分钟
- ✅ 确保视频文件不损坏（可用 FFmpeg 验证）

### 问题 3: "分析超时或失败"
- 视频太长或关键帧太多
- 网络连接不稳定
- Claude API 暂时不可用

### 问题 4: "找不到数据库"
- 确保 `data/history/` 目录存在
- 应用会自动创建，如果没有可以手动创建：
  ```bash
  mkdir -p data/history
  ```

---

## 📊 数据存储

### 数据库位置
```
~/video-ai-workflow/data/history/analysis_history.db
```

### 存储内容
- 视频名称
- 分析时间
- 完整的分析结果 (JSON)
- 音乐生成提示词
- 音效生成提示词列表

### 备份建议
定期备份数据库文件：
```bash
cp data/history/analysis_history.db data/history/analysis_history_backup.db
```

---

## 🎓 分析结果质量指南

### 什么是"高质量"分析？

✅ **好的分析特征：**
- 音乐风格具体（"电影史诗配乐，弦乐为主，钢琴和小提琴"）
- 节奏有具体数字（"60-80 BPM"而非"中等速度"）
- 情绪关键词丰富（3-5 个相关词）
- 时间轴细致（关键场景都有描述）
- 音效需求具体（"逼真的手机铃声，带有轻微的回音"而非"铃声"）

❌ **需要改进的分析：**
- 风格过于泛泛（"电影风格"）
- 缺少技术细节（乐器、节奏、强度）
- 时间轴分析不足

### 如何改进分析

1. **修改视频**：
   - 剪辑视频，突出主要内容
   - 确保关键场景清晰

2. **调整提示词**：
   - 编辑 `analysis.py` 中的分析 prompt
   - 在系统提示中添加更多细节要求

3. **增加采样率**：
   - 降低 `sample_interval` 以获得更细致的帧分析

---

## 📝 示例输出

### 原始输入
- 一个 2 分钟的商务会议视频

### 分析输出示例

**音乐推荐：**
```
风格: 企业配乐（钢琴和现代弦乐）
节奏: 75-90 BPM，稳重且专业
乐器: 钢琴主旋律、小提琴和中提琴背景、低音提琴基础
强度: 6/10
情绪: 专业、信任、动力、决心
```

**AI 生成提示词示例：**
```
A professional corporate background music composition featuring 
elegant piano melodies with supporting strings (violin, viola, cello). 
The tempo should be around 75-90 BPM, creating a sense of professionalism 
and reliability. The mood should convey trust, determination, and forward momentum...
```

**时间轴示例：**
```
[0:00-0:05] 会议开始，CEO 坐在办公室
情绪: 准备、聚焦
音效: 轻微的环境音（办公室背景音）
提示词: 细微的办公室背景音，键盘声、空调声，音量低，频率高

[0:05-0:12] 拿起电话准备通话
情绪: 紧张、集中
音效: 电话铃声、电话接通音
提示词: 逼真的办公电话铃声，然后是清晰的电话接通音效
```

---

## 🚀 下一步

### 当前状态
✅ 视频分析完成
✅ 音乐/音效提示词生成完成
✅ 历史记录保存完成
⏸️ 音乐/音效自动生成（待集成）

### 未来计划
- 集成 Suno API（自动生成音乐）
- 集成爱声音坊 API（自动生成音效）
- 视频和音频自动混合（FFmpeg）
- 支持批量分析

---

## 📞 获取帮助

- 检查 README.md 了解项目结构
- 查看代码中的注释
- 确保 API 密钥有效
- 检查网络连接

---

**祝你使用愉快！🎉**
