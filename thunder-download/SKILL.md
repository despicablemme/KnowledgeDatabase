---
name: thunder-download
description: Automate Thunder (迅雷) download on macOS. Use when user wants to find and download torrents/magnets via Thunder. Includes: (1) Navigating seedhub.cc via category/tag URLs (skip search due to Cloudflare blocks), browse results, and identify quality, (2) Opening magnet/Thunder links via thunder:// URL scheme, (3) Reading UI elements with osascript/System Events, (4) Clicking with cliclick, and (5) Using keyboard shortcuts to trigger downloads.
---

# Thunder Download Automation

## Overview

This skill enables automated downloading via Thunder (迅雷) on macOS. It covers two workflows:
1. **Finding downloads on seedhub.cc** - Search and locate content
2. **Opening downloads in Thunder** - Add magnet/torrent links and trigger downloads

## Finding Downloads on seedhub.cc

### Navigation

```bash
# Open browser to seedhub.cc
openclaw browser --browser-profile openclaw navigate https://seedhub.cc
```

### Search for Content

1. Click the search box (ref e10)
2. Type search keywords (e.g., "Person of Interest", "疑犯追踪")
3. Press Enter to search

```bash
# Click search box
openclaw browser --browser-profile openclaw click e10

# Type search query
openclaw browser --browser-profile openclaw type e10 "Person of Interest"

# Submit search
openclaw browser --browser-profile openclaw press Enter
```

### Browse and Select Results

Use snapshot to view results, then click the target item:

```bash
# Get page content (AI format for readability)
openclaw browser --browser-profile openclaw snapshot --format ai --limit 5000

# Click on a search result
openclaw browser --browser-profile openclaw click <element-ref>
```

### Get Download Links

On the detail page, look for download section with tabs:
- 磁力 (Magnet links)
- 迅雷 (Thunder links)
- 夸克 (Quark)
- 百度 (Baidu)

```bash
# Click "迅雷" tab if available (ref e190)
openclaw browser --browser-profile openclaw click e190

# Or click on a specific download link (magnet link ref e62)
openclaw browser --browser-profile openclaw click e62

# Get magnet link from page
openclaw browser --browser-profile openclaw snapshot --format ai --limit 3000
```

### Quality Indicators (蓝光=Bluray, 无损=Lossless, 杜比=Dolby)

| Tag | Meaning |
|-----|---------|
| 蓝光 | Bluray source |
| 4K | 4096x2160 resolution |
| 无损 | Lossless quality |
| 杜比 | Dolby audio |
| iNT组 | iNT release group |

## Prerequisites

### Required Tools

```bash
# Install cliclick (mouse/keyboard automation)
brew install cliclick

# Thunder must be installed at /Applications/Thunder.app
```

### Key Concepts

1. **thunder:// URL scheme** - Opens Thunder and adds magnet/torrent links
2. **osascript + System Events** - Reads macOS app UI elements
3. **cliclick** - Simulates mouse clicks and keyboard input at screen coordinates
4. **AppleScript keyboard events** - Triggers keyboard shortcuts

## Workflow

### Step 1: Add Download Task via Magnet URL

```bash
# Base64 encode magnet link and construct thunder:// URL
magnet="magnet:?xt=urn:btih:..."
thunder_url="thunder://$(echo -n "$magnet" | base64)"
open "$thunder_url"
```

Or directly:
```bash
open "thunder://bWFnbmV0Oj94dD11cm46YnRpaDo3MGMwMGNiMmRjMGQ5YzAyNzliNjU0MWEwN2M4NzJmMDY1YWUwMTY3"
```

### Step 2: Identify UI Elements

Wait for Thunder window to appear, then inspect UI:

```bash
# Get list of windows for Thunder process
osascript -e 'tell application "System Events" to tell process "Thunder" to get windows'

# Get entire contents of a window
osascript -e 'tell application "System Events" to tell process "Thunder" to tell window "新建下载任务" to get entire contents'

# Get position and size of a button
osascript -e 'tell application "System Events" to tell process "Thunder" to tell button "立即下载" of window "新建下载任务" to get {position, size}'

# Get popup button value (current download path)
osascript -e 'tell application "System Events" to tell process "Thunder" to tell pop up button 1 of window 1 to get value'
```

### Step 3: Click Buttons with cliclick

```bash
# Click at coordinates (x, y)
cliclick c:730,658

# Move mouse without clicking
cliclick m:100,200

# Double-click
cliclick dc:100,200

# Type text
cliclick t:"Hello"

# Press Enter
cliclick kp:return

# With restore cursor position after (-r)
cliclick -r c:730,658
```

### Step 4: Trigger Download with Keyboard

If regular clicks don't work, try AppleScript keyboard simulation:

```bash
# Press Enter key
osascript -e 'tell application "System Events" to key code 36'

# Press Return key  
osascript -e 'tell application "System Events" to key code 76'

# Press Escape
osascript -e 'tell application "System Events" to key code 53'

# With modifiers
osascript -e 'tell application "System Events" to keystroke "s" using command down'
```

## Complete Download Automation Script

```bash
#!/bin/bash
# thunder-auto-download.sh

MAGNET="$1"
DEST_DIR="$HOME/Downloads"

# Step 1: Open magnet in Thunder
ENCODED=$(echo -n "$MAGNET" | base64)
open "thunder://$ENCODED"

# Step 2: Wait for window to load
sleep 2

# Step 3: Get button position
osascript -e 'tell application "System Events" to tell process "Thunder" to get windows'

# Step 4: Check current download path
CURRENT_PATH=$(osascript -e 'tell application "System Events" to tell process "Thunder" to tell pop up button 1 of window 1 to get value')
echo "Current path: $CURRENT_PATH"

# Step 5: If path is not "下载", need to change it
# Otherwise click download directly

# Step 6: Click 立即下载 button (coordinates from UI inspection)
cliclick c:730,658

# Step 7: Press Enter to confirm
sleep 0.5
osascript -e 'tell application "System Events" to key code 36'
```

## Common UI Element Queries

### Thunder Window Structure

```
window "新建下载任务"
├── button "选择本地目录"
├── button "立即下载"
├── pop up button 1 (download directory selector)
├── scroll area 1
│   └── outline 1 (file list)
│       └── row N (individual files)
└── static text (status info)
```

### Useful Inspection Commands

```bash
# Get all buttons in window
osascript -e 'tell application "System Events" to tell process "Thunder" to tell window 1 to get every button'

# Get static text (labels/status)
osascript -e 'tell application "System Events" to tell process "Thunder" to tell window 1 to get every static text'

# Get checkbox states
osascript -e 'tell application "System Events" to tell process "Thunder" to tell window 1 to get every checkbox'
```

## Troubleshooting

### "Can't get window" Error
```bash
# Thunder may not be frontmost - activate it first
osascript -e 'tell application "Thunder" to activate'
sleep 1
```

### Button Click Has No Effect
- Some buttons require AXPress action instead of coordinate click
- Try: `osascript -e 'tell application "System Events" to perform action "AXPress" of button "按钮名" of window "窗口名"'`

### Directory Selection Dialog Doesn't Appear
- Thunder uses custom UI that may not respond to standard clicks
- May need manual intervention for directory selection
- Alternative: Set default download directory in Thunder preferences

### File Not Downloading
- Check disk space: `df -h`
- Check if magnet is valid
- Try clearing Thunder's task list and re-adding

## Related Tools

- **cliclick** - Mouse/keyboard CLI: `brew install cliclick`
- **Accessibility Inspector** - UI debugging (requires Xcode)
- **Keyboard Maestro** - Advanced GUI automation ($36)

## Troubleshooting: seedhub.cc Navigation

### Cloudflare Blocks Search
- The site's search triggers Cloudflare protection and gets blocked
- **Solution**: Skip search, use category + tag + sort URLs instead
  - Tags: `/categories/3/tags/1670/movies/?order=date` (2013 dramas)
  - Direct tag navigation is more reliable than search

### Element Refs Change After Navigation
- Element refs (e10, e351, etc.) are **NOT stable** across page loads
- **Always** take a fresh `snapshot` before clicking/interacting
- Never assume a ref from a previous step is still valid

### Click on Link Doesn't Navigate
- Clicking links sometimes doesn't trigger navigation
- **Solution**: Use direct URL navigation instead
  ```bash
  # Instead of clicking, navigate directly
  openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/movies/26400/"
  ```

### Page Content Not Loading
- Some content loads via JavaScript dynamically
- Take a snapshot after waiting 1-2 seconds for content to render

### Reliable Workflow for Finding Content
1. Navigate directly to known category/tag URL
2. Take snapshot to see content
3. Identify target item and its URL
4. Navigate directly to that URL
5. Take snapshot before interacting with download section

Example: Finding Person of Interest S03
```bash
# Navigate to 2013 dramas sorted by date
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/categories/3/tags/1670/movies/?order=date"

# Page to the right page (S03 is around page 3)
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/categories/3/tags/1670/movies/?page=3&order=date"

# Navigate directly to the show's detail page (ID found in snapshot)
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/movies/26400/"

# Get download links
openclaw browser --browser-profile openclaw navigate "https://seedhub.cc/link_start/?seed_id=380116&movie_title=Person.of.Interest.S03"
```

## Cleanup After Task Completion

After a download task is successfully added to Thunder, clean up any temporary screenshots:

```bash
# Remove temporary screenshots created during automation
rm -f ~/Desktop/thunder_screen.png ~/Desktop/thunder_state.png

# Also check ~/Downloads/ for any temp files
ls -lt ~/Downloads/*.png 2>/dev/null && rm -f ~/Downloads/*.png
```
