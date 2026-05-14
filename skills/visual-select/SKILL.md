---
name: visual-select
description: 视觉图片精选任务。当需要搜索和发送高质量图片（城市风貌、风光大片、人像佳作、人文纪实）时使用此skill。自动化图片搜索、下载、发送和清理流程。
---

# Visual Select - 视觉图片精选

## 工作流程

1. 接收主题参数（city/landscape/portrait/street）
2. 调用 MCP 搜索图片（优先 pixabay，备用 pexels）
3. 下载到指定目录
4. 组装 qqmedia 标签发送
5. 清理临时文件

## 使用方法

### 快速执行

```bash
# 搜索5张城市图片
python3 scripts/visual-select.py city /tmp/visual

# 搜索5张风光图片
python3 scripts/visual-select.py landscape /tmp/visual

# 搜索3张人像图片
python3 scripts/visual-select.py portrait /tmp/visual 3
```

### 主题参数

| 主题 | 查询词 | 文件前缀 |
|------|--------|----------|
| city | city urban architecture | ct_ |
| landscape | landscape nature scenic | ls_ |
| portrait | portrait people model | pt_ |
| street | street documentary culture | st_ |

### MCP 配置

确保 visual agent 的 `~/.openclaw/agents/visual/workspace/config/mcporter.json` 包含：

```json
{
  "mcpServers": {
    "pexels": {
      "command": "pexels-mcp-server",
      "args": ["--api-key", "你的API_KEY"]
    },
    "pixabay": {
      "command": "pixabay-mcp",
      "env": {
        "PIXABAY_API_KEY": "你的API_KEY"
      }
    }
  }
}
```

## Agent 执行示例

```
任务：搜索5张高质量城市照片并发送

1. 清理旧文件（每次任务重新下载最新图片）：
rm -rf /tmp/visual/*

2. 执行脚本：
mkdir -p /tmp/visual
python3 ~/.openclaw/skills/visual-select/scripts/visual-select.py city /tmp/visual

3. 脚本输出包含 "DOWNLOADED:..." 行，解析下载的文件路径

4. 组装消息发送：
🏙️ 城市风貌（5张）
<qqmedia>/tmp/visual/ct_1.jpg</qqmedia>
<qqmedia>/tmp/visual/ct_2.jpg</qqmedia>
...

5. 不删除缓存文件！方便主人后续使用，/tmp/visual/ 里的图片会保留供当日使用。
```

## 缓存说明

- 图片保存在 `/tmp/visual/` 目录
- 每次任务开始时清理旧图片，重新下载最新
- **不删除缓存** - 图片保留到当日结束，方便查找和使用
- 如需手动清理：`rm -rf /tmp/visual/*`

## 错误处理

- MCP 不可用：自动切换到备选源
- 下载失败：跳过该图片，继续下载其他
- 所有下载失败：脚本返回非0退出码
