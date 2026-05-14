# bilibili-hot Skill

每天抓取 B站热门排行榜，生成语音播报。

## 功能

1. 从 B站 API 获取热门视频列表
2. 整理成文字（标题、UP主、播放量、点赞数）
3. 用 Edge TTS 生成语音
4. 输出文件到 `~/Documents/TTSoutputs/每日热点/`

## 使用方式

### 手动执行
```bash
/Library/Developer/CommandLineTools/usr/bin/python3 ~/.openclaw/workspace/bilibili-hot/scripts/fetch_bilibili_hot.py
```

### 定时任务（每天早上9点）
在 OpenClaw cron 中配置：
- 时间：每天 09:00
- 命令：执行上面的脚本
- 输出：通过 QQ 发送语音给主人

## 输出格式

```
B站热门日报 - 2026年3月23日

第1名：视频标题
UP主：xxx | 播放：xxx万 | 点赞：xxx

第2名：视频标题
...

今日热点已生成语音，点击收听。
```

## 技术细节

### B站 API
```bash
curl "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all" \
  -H "User-Agent: Mozilla/5.0"
```

### 字段说明
- `title`: 视频标题
- `owner.name`: UP主名称
- `stat.view`: 播放量
- `stat.like`: 点赞数
- `tname`: 分区名称

### TTS 参数
- 声音：zh-CN-XiaoxiaoNeural
- 语速：-25%（0.75倍）
- 音调：+0Hz

## 目录结构
```
bilibili-hot/
├── SKILL.md
└── scripts/
    └── fetch_bilibili_hot.py
```

## 定时任务配置

在 HEARTBEAT.md 或 cron 中设置：
- 时间：每天 09:00 GMT+8
- 任务：生成当日热点语音
- 通知：完成后发 QQ 消息提醒主人收听
