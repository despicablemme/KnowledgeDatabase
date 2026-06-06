---
name: chaturbate-monitor
description: Chaturbate streamer monitor and OBS recording controller. Monitors Chaturbate streamers via Events API long-polling, detects when followed broadcasters go live, opens Chrome, handles age verification overlays, and controls OBS WebSocket to start or stop recording. Use when: (1) user asks to monitor a Chaturbate streamer for going live, (2) user wants to auto-record a stream, (3) user asks to check if a specific streamer is online, (4) user wants to start or stop OBS recording for a stream. Prerequisites: OBS must have obs-websocket plugin installed and WebSocket enabled on port 10086 with password openclaw. Chrome must have Allow JavaScript from Apple Events enabled (View Developer menu). Events API token required for real-time monitoring.
---

# Chaturbate Monitor & OBS Recording Controller

## Overview

Full automated workflow: **Events API real-time monitoring → Detect Live → Open Chrome → Click Overlay → Start OBS Recording → Auto-stop when offline**.

## Prerequisites

1. **OBS WebSocket**: obs-websocket plugin installed, OBS → Settings → Advanced → WebSocket enabled on port 10086, password `openclaw`
2. **Chrome Permissions**: View → Developer → ✅ "Allow JavaScript from Apple Events"
3. **Proxy**: macOS proxy at `127.0.0.1:7897` (for Events API calls)
4. **Events API Token**: From https://zh-hans.chaturbate.com/settings/tokens/ with Events API scope

## Core Scripts

`scripts/listener.py` - Main real-time event listener:

```bash
# Start real-time monitoring (blocks, keeps listening)
python3 scripts/listener.py listen

# Start monitoring in background
nohup python3 scripts/listener.py listen > /tmp/cb_listener.log 2>&1 &
```

`scripts/monitor.py` - Manual control scripts:

```bash
python3 scripts/monitor.py check          # Check if default streamer is online
python3 scripts/monitor.py open          # Open streamer in Chrome
python3 scripts/monitor.py close-overlay # Click age verification
python3 scripts/monitor.py start-recording
python3 scripts/monitor.py stop-recording
python3 scripts/monitor.py status
```

## Configuration

Edit the CONFIG section at the top of each script:
- `USERNAME` = your Chaturbate username
- `TOKEN` = your Events API token
- `STREAMER` = default streamer to monitor
- `OBS_HOST/PORT/PASSWORD` = OBS WebSocket settings
- `PROXY` = your HTTP proxy

## Events API (Real-Time Monitoring)

The Events API provides long-polling event streams. Endpoint:
```
https://eventsapi.chaturbate.com/events/:username/:token/
```

Supported events:
- `broadcastStart` - Followed broadcaster started streaming
- `broadcastStop` - Followed broadcaster stopped streaming
- `tip` - User sent a tip
- `chatMessage` - Chat message received
- `privateMessage` - Private message received
- `follow` / `unfollow` - User followed/unfollowed

The listener script automatically follows the `nextUrl` chain for continuous monitoring.

## Full Workflow

1. **Start listener** (background cron or manual):
   ```bash
   nohup python3 scripts/listener.py listen > /tmp/cb_listener.log 2>&1 &
   ```

2. **When broadcastStart detected**:
   - Opens `https://chaturbate.com/:broadcaster/` in Chrome
   - Clicks through age verification overlay
   - Starts OBS recording automatically

3. **When broadcastStop detected**:
   - Stops OBS recording automatically

4. **Manual stop** (anytime):
   ```bash
   python3 scripts/monitor.py stop-recording
   ```

## Recording Storage

OBS recordings: `~/Movies/YYYY-MM-DD HH-MM-SS.mov`

## Troubleshooting

- **"No button found" on overlay click**: Overlay HTML may have changed. Take screenshot, visually inspect buttons, update the JS selector in the script.
- **OBS auth fails**: Verify obs-websocket installed and port/password match CONFIG.
- **Chrome JS execution error**: Ensure Chrome → View → Developer → "Allow JavaScript from Apple Events" is enabled.
- **Events API fetch fails**: Verify proxy is running at 127.0.0.1:7897.
- **Listener exits unexpectedly**: Check log at /tmp/cb_listener.log