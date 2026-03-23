# ebook-tts Skill

将电子书（txt/epub/mobi/pdf）转换为有声书。

## 角色

- **主 Agent**：接收任务、分析需求、创建子 Agent、监控进度、汇报结果
- **子 Agent**：执行具体的文件解析、章节拆分、TTS 生成

## 工作流程

1. 接收电子书文件（主人发送文件路径）
2. 创建子 Agent 处理任务
3. 主 Agent 监控进度，保持可用

## 子 Agent 执行步骤

### Step 1: 解析电子书

根据文件类型解析：
- **.txt**：直接按章节分割
- **.epub**：用 Python epub 库解析
- **.mobi**：用 python-mobi 解析
- **.pdf**：用 PyPDF2 或 pdfplumber 解析

### Step 2: 章节分割

- 检测章节标题（正则匹配：第X回、第X章、第X卷 等）
- 将内容按章节分割为独立 .txt 文件
- 文件命名：`001_第一章.txt`、`002_第二章.txt`

### Step 3: TTS 语音生成

- 使用 edge-tts（已安装）
- 声音：zh-CN-XiaoxiaoNeural
- 语速：+10%，音调：-5Hz
- 输出格式：.mp3
- 文件命名：`001_第一章.mp3`

### Step 4: 存储结构

```
~/Documents/TTSoutputs/{书名}/
├── 001_第一章.txt
├── 001_第一章.mp3
├── 002_第二章.txt
├── 002_第二章.mp3
└── ...
```

## 输出目录

`~/Documents/TTSoutputs/{书名}/`

## 监控汇报

子 Agent 需要：
- 每生成 5 个章节向主 Agent 发送进度
- 全部完成后发送最终汇报
- 汇报格式：`{书名} 有声书制作完成！共 X 章，文件在 ~/Documents/TTSoutputs/{书名}/`

## 技术要点

### 依赖

```bash
pip install edge-tts ebooklib python-mobi pymupdf
```

### 章节标题正则

```python
import re
# 中文小说章节匹配
patterns = [
    r'^第([一二三四五六七八九十百千万零〇\\d]+)[回章节卷篇]',  # 第X回/第X章/第X卷
    r'^[第][一二三四五六七八九十百千万\\d]+[回章节]',           # 第X回
    r'^(CHAPTER|Chapter|chapter)\\s+\\d+',                    # CHAPTER 1
    r'^\\d+\\.\\s+.+',                                        # 1. 标题
]
```

### TTS 生成脚本

见 `scripts/generate_tts.py`

## 注意事项

- txt 文件编码统一使用 UTF-8
- 章节标题尽量保持原样
- 生成的 txt 和 mp3 同名，便于对应
- 如果文件过大（>1MB），TTS 可能需要分批处理
