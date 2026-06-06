#!/usr/bin/env python3
"""
Chaturbate Monitor & OBS Controller
Monitors a Chaturbate streamer, detects when they go live,
opens Chrome, and controls OBS to record.
"""
import websocket
import json
import base64
import hashlib
import time
import subprocess
import sys
import os
import urllib.request

# === CONFIG ===
USERNAME = "despicablemme"
TOKEN = "OxHmmjoAC1kJgE1TWeTRgsub"
STATS_API_URL = "https://chaturbate.com/statsapi/"
EVENTS_API_URL = "https://eventsapi.chaturbate.com"
STREAMER = "_milkyway"
PROXY = "http://127.0.0.1:7897"
OBS_HOST = "127.0.0.1"
OBS_PORT = 10086
OBS_PASSWORD = "openclaw"
CHROME_TAB_SCRIPT = "/tmp/open_cb.scpt"
CHROME_JS_SCRIPT = "/tmp/click_agree.scpt"
RECORDINGS_DIR = os.path.expanduser("~/Movies")


def fetch_via_proxy(url):
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=__import__('ssl')._create_unverified_context()) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Fetch error: {e}")
        return None


def obs_auth_and_call(ws, req_type, req_data=None):
    ws.send(json.dumps({"request-type": "GetAuthRequired", "message-id": "1"}))
    resp = json.loads(ws.recv())
    if resp.get('authRequired'):
        salt = resp['salt']
        challenge = resp['challenge']
        secret = base64.b64encode(hashlib.sha256((OBS_PASSWORD + salt).encode('utf-8')).digest())
        auth = base64.b64encode(hashlib.sha256(secret + challenge.encode('utf-8')).digest()).decode('utf-8')
        ws.send(json.dumps({"request-type": "Authenticate", "message-id": "2", "auth": auth}))
        ws.recv()
    req_id = str(int(time.time()))
    req = {"request-type": req_type, "message-id": req_id}
    if req_data:
        req["request-data"] = req_data
    ws.send(json.dumps(req))
    resp = json.loads(ws.recv())
    return resp


def obs_call(req_type, req_data=None):
    ws = websocket.create_connection(f"ws://{OBS_HOST}:{OBS_PORT}", timeout=5)
    result = obs_auth_and_call(ws, req_type, req_data)
    ws.close()
    return result


def check_online(streamer=None):
    """Check if streamer is online via Stats API."""
    s = streamer or STREAMER
    url = f"{STATS_API_URL}?username={USERNAME}&token={TOKEN}"
    data = fetch_via_proxy(url)
    if data is None:
        return None, "API fetch failed"
    # Stats API returns own user's info, not followed streamers' status
    # So we fall back to HTML parsing for followed streamers
    url2 = f"https://chaturbate.com/{s}/"
    try:
        import re
        proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
        req = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=__import__('ssl')._create_unverified_context()) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            if 'room_status' in html:
                m = re.search(r'room_status\\?"[:\\s]+([\w]+)', html)
                if m:
                    status = m.group(1)
                    return status == 'online', status
    except Exception as e:
        pass
    return False, "unknown"


def open_chrome(url):
    script = f'''
tell application "Google Chrome"
    activate
    tell window 1
        set newTab to make new tab at end of tabs
        set URL of newTab to "{url}"
    end tell
end tell
'''
    with open(CHROME_TAB_SCRIPT, 'w') as f:
        f.write(script)
    subprocess.run(['osascript', CHROME_TAB_SCRIPT], timeout=10)
    time.sleep(5)


def close_overlay():
    script = '''
tell application "Google Chrome"
    execute active tab of window 1 javascript "
(function() {
    var allEls = document.querySelectorAll('*');
    for (var i = 0; i < allEls.length; i++) {
        var style = window.getComputedStyle(allEls[i]);
        var z = parseInt(style.zIndex) || 0;
        if (z >= 1100 && allEls[i].textContent.includes('18 AND AGREE')) {
            var buttons = allEls[i].querySelectorAll('button, a');
            for (var j = 0; j < buttons.length; j++) {
                var txt = buttons[j].textContent.trim();
                if (txt.toLowerCase().indexOf('privacy') === -1 && txt.length > 0 && buttons[j].offsetParent !== null) {
                    buttons[j].click();
                    return 'Clicked: ' + txt;
                }
            }
        }
    }
    return 'No button found';
})()
"
end tell
'''
    with open(CHROME_JS_SCRIPT, 'w') as f:
        f.write(script)
    result = subprocess.run(['osascript', CHROME_JS_SCRIPT], capture_output=True, text=True, timeout=10)
    return result.stdout.strip()


def start_recording():
    resp = obs_call("StartRecording")
    return resp.get('status') == 'ok', resp.get('recordingFilename', '')


def stop_recording():
    resp = obs_call("StopRecording")
    return resp.get('status') == 'ok'


def get_recording_status():
    return obs_call("GetRecordingStatus")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    streamer = sys.argv[2] if len(sys.argv) > 2 else STREAMER

    if cmd == "check":
        online, status = check_online(streamer)
        print(f"Streamer {streamer}: {status.upper()} ({'ONLINE' if online else 'OFFLINE'})")
        sys.exit(0 if online else 1)
    elif cmd == "start-recording":
        ok, filename = start_recording()
        if ok:
            print(f"Recording started: {filename}")
        else:
            print("Failed to start recording")
        sys.exit(0 if ok else 1)
    elif cmd == "stop-recording":
        ok = stop_recording()
        print("Recording stopped" if ok else "Failed to stop recording")
        sys.exit(0 if ok else 1)
    elif cmd == "status":
        status = get_recording_status()
        print(json.dumps(status, indent=2))
    elif cmd == "open":
        url = f"https://chaturbate.com/{streamer}/"
        open_chrome(url)
        print(f"Opened {url}")
        sys.exit(0)
    elif cmd == "close-overlay":
        result = close_overlay()
        print(f"Overlay click: {result}")
        sys.exit(0)
    else:
        print(f"Usage: {sys.argv[0]} [check|start-recording|stop-recording|status|open|close-overlay] [streamer]")
        sys.exit(1)