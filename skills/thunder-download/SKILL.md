---
name: thunder-download
description: Automate Thunder (迅雷) download on macOS with anti-detection measures. Use when user wants to find and download torrents/magnets via Thunder. Includes: (1) Cloudflare bypass with human-like behavior, (2) Navigating seedhub.cc via category/tag URLs, (3) Opening magnet/Thunder links via thunder:// URL scheme, (4) Reading UI elements with osascript/System Events, (5) Clicking with randomized positions/timing to avoid detection.
---

# Thunder Download Automation (Anti-Detection Edition)

## Overview

This skill enables automated downloading via Thunder (迅雷) on macOS with measures to avoid Cloudflare and other bot detections.

**核心原则：模拟人类行为，不要像机器一样操作。**

---

## 🌟 Anti-Detection 核心规则

### 1. 随机延迟（必须）
```
每次操作后等待 1-5 秒随机时间
页面加载后等待 2-4 秒再操作
点击之间等待 1-3 秒
```

### 2. 随机点击位置（必须）
```
不要点击精确坐标，每次偏移 ±5-15 像素
不要从同一位置开始移动鼠标
```

### 3. 鼠标移动轨迹（必须）
```
用贝塞尔曲线或随机折线，不要直线移动
移动过程中有停顿，模拟人类犹豫
```

### 4. 操作节奏
```
避免规律性操作（每次都1秒不行）
随机化是王道
```

---

## Finding Downloads on seedhub.cc

### Navigation

**推荐：使用 category + tag + sort URL 代替搜索（搜索会被 Cloudflare 拦截）**

```bash
# 打开浏览器到 seedhub.cc
openclaw browser --browser-profile openclaw navigate https://seedhub.cc
```

### 反检测浏览器配置

使用 stealth 浏览器配置文件（第一次使用需要创建）：

```bash
# 创建 stealth profile（只在第一次）
openclaw browser --browser-profile stealth create

# 使用 stealth profile 访问
openclaw browser --browser-profile stealth navigate https://seedhub.cc
```

### 安全操作流程（反检测版）

**Step 1: 打开网站**
```bash
openclaw browser --browser-profile stealth navigate https://seedhub.cc
```
⏱ 等待 3-5 秒（让 Cloudflare 验证通过）

**Step 2: 获取页面内容**
```bash
openclaw browser --browser-profile stealth snapshot --format ai --limit 5000
```
⏱ 等待 2-3 秒

**Step 3: 点击搜索框（随机化位置）**
```bash
# 基础坐标 + 随机偏移
# 假设搜索框在 e10，先移动鼠标到附近随机位置
openclaw browser --browser-profile stealth mouse move 500+rand(10,20),400+rand(10,20)
# 然后再点击
openclaw browser --browser-profile stealth click e10
```
⏱ 等待 1-2 秒

**Step 4: 输入搜索词（模拟人类打字）**
```bash
# 每个字符之间随机延迟 50-150ms
openclaw browser --browser-profile stealth type e10 "Person of Interest"
```
⏱ 等待 2-4 秒

**Step 5: 提交搜索**
```bash
# 移动鼠标模拟人类点击位置偏移
openclaw browser --browser-profile stealth mouse move 300+rand(5,15),50+rand(5,15)
openclaw browser --browser-profile stealth press Enter
```
⏱ 等待 3-5 秒

**Step 6: 浏览结果**
```bash
openclaw browser --browser-profile stealth snapshot --format ai --limit 5000
```
⏱ 等待 2-3 秒

**Step 7: 点击结果（随机位置+移动轨迹）**
```bash
# 模拟鼠标移动到目标位置
openclaw browser --browser-profile stealth mouse move 400+rand(-10,10),300+rand(-10,10)
openclaw browser --browser-profile stealth click <element-ref>
```
⏱ 等待 2-4 秒

### Category/Tag URL 导航（绕过搜索，推荐）

由于搜索会触发 Cloudflare，推荐使用分类 URL：

```bash
# 按分类+标签+排序直接导航
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/categories/3/tags/1670/movies/?order=date"

# 翻页
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/categories/3/tags/1670/movies/?page=3&order=date"

# 直接到详情页
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/movies/26400/"

# 获取下载链接
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/link_start/?seed_id=380116&movie_title=Person.of.Interest.S03"
```

### Element Refs 注意事项
- Refs (e10, e351 等) **不是固定的**
- 每次页面加载后都要重新 snapshot 获取

### 页面内容不加载
- 内容是 JS 动态加载的
- 等待 2-3 秒后再获取 snapshot

---

## 反检测技术细节

### 延迟函数
```javascript
// 随机延迟 1-5 秒
const humanDelay = () => new Promise(r => 
  setTimeout(r, Math.random() * 4000 + 1000)
);

// 打字延迟 50-200ms 每字符
const typeDelay = () => new Promise(r => 
  setTimeout(r, Math.random() * 150 + 50)
);
```

### 鼠标移动
```javascript
// 贝塞尔曲线移动
async function humanMouseMove(page, targetX, targetY) {
  const startX = Math.random() * 100 + 400;
  const startY = Math.random() * 100 + 300;
  const steps = 10 + Math.floor(Math.random() * 10);
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = startX + (targetX - startX) * t + (Math.random() - 0.5) * 10;
    const y = startY + (targetY - startY) * t + (Math.random() - 0.5) * 10;
    await page.mouse.move(x, y);
    await page.waitForTimeout(20 + Math.random() * 30);
  }
}
```

### 点击位置随机化
```javascript
function randomizeClick(page, selector) {
  const box = await page.locator(selector).boundingBox();
  if (box) {
    const x = box.x + box.width / 2 + (Math.random() - 0.5) * 20;
    const y = box.y + box.height / 2 + (Math.random() - 0.5) * 20;
    await page.mouse.click(x, y);
  }
}
```

---

## Thunder 下载流程

### Step 1: 构造 thunder:// URL
```bash
magnet="magnet:?xt=urn:btih:..."
thunder_url="thunder://$(echo -n "$magnet" | base64)"
open "$thunder_url"
```
⏱ 等待 2-3 秒

### Step 2: 检查 Thunder 窗口
```bash
osascript -e 'tell application "System Events" to tell process "Thunder" to get windows'
sleep 2
```

### Step 3: 获取按钮位置
```bash
osascript -e 'tell application "System Events" to tell process "Thunder" to tell button "立即下载" of window "新建下载任务" to get {position, size}'
sleep 1
```

### Step 4: 随机化点击位置
```bash
# 基础位置 ± 随机偏移
X=730+$((RANDOM % 20 - 10))
Y=658+$((RANDOM % 20 - 10))
cliclick c:$X,$Y
```
⏱ 等待 1-2 秒

### Step 5: 确认下载
```bash
sleep 1
osascript -e 'tell application "System Events" to key code 36'
```

---

## Quality Indicators

| Tag | Meaning |
|-----|---------|
| 蓝光 | Bluray source |
| 4K | 4096x2160 resolution |
| 无损 | Lossless quality |
| 杜比 | Dolby audio |
| iNT组 | iNT release group |

---

## Prerequisites

```bash
# Install cliclick
brew install cliclick

# Thunder must be installed at /Applications/Thunder.app
```

---

## 完整脚本示例

```bash
#!/bin/bash
# thunder-open-magnet.sh - 反检测版

MAGNET="$1"
DELAY=$((RANDOM % 3000 + 2000))  # 2-5秒随机延迟

# Step 1: 打开 Thunder
ENCODED=$(echo -n "$MAGNET" | base64)
open "thunder://$ENCODED"
sleep $DELAY

# Step 2: 获取窗口状态
osascript -e 'tell application "Thunder" to activate'
sleep 2

# Step 3: 获取按钮位置（带随机偏移）
POS=$(osascript -e 'tell application "System Events" to tell process "Thunder" to tell button "立即下载" of window 1 to get {position}' | tr -d ',')
X=$(echo $POS | awk '{print $1}' | tr -d '{')
Y=$(echo $POS | awk '{print $2}' | tr -d '}')
X=$((X + RANDOM % 20 - 10))
Y=$((Y + RANDOM % 20 - 10))

# Step 4: 模拟鼠标移动轨迹
cliclick -r m:$((X + 50)),$((Y + 50))
usleep 200000
cliclick -r m:$X,$Y

# Step 5: 点击
cliclick c:$X,$Y
sleep 1

# Step 6: 回车确认
osascript -e 'tell application "System Events" to key code 36'
```

---

## Troubleshooting: Cloudflare

### Cloudflare 仍然拦截？
1. **等待足够长时间**（Cloudflare 验证需要 3-5 秒）
2. **不要重复快速刷新**（会被临时封禁）
3. **换时间段**（高峰时段检测更严）
4. **手动先访问一次**（建立浏览器会话）

### Element Refs 变化
- Refs (e10, e351 等) **不是固定的**
- 每次页面加载后都要重新 snapshot 获取

### 页面内容不加载
- 内容是 JS 动态加载的
- 等待 2-3 秒后再获取 snapshot

---

## 任务完成后清理

```bash
rm -f ~/Desktop/thunder_screen.png ~/Desktop/thunder_state.png
ls -lt ~/Downloads/*.png 2>/dev/null && rm -f ~/Downloads/*.png
```
