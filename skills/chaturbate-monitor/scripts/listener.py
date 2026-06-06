#!/usr/bin/env python3
"""
Chaturbate Events API Listener
Long-polls the Events API for broadcast events and triggers OBS recording.
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
import urllib.error

# === CONFIG ===
EVENTS_API_URL = "https://eventsapi.chaturbate.com"
USERNAME = "despicablemme"
TOKEN = "OxHmmjoAC1kJgE1TWeTRgsub"
PROXY = "http://127.0.0.1:7897"
OBS_HOST = "127.0.0.1"
OBS_PORT = 10086
OBS_PASSWORD = "openclaw"
STREAMER = "_milkyway"  # default streamer to record
CHROME_TAB_SCRIPT = "/tmp/open_cb.scpt"
CHROME_JS_SCRIPT = "/tmp/click_agree.scpt"


def obs_auth_and_call(ws, req_type, req_data=None):
    """Auth with OBS and make a request."""
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
    print(f"[Chrome] Opened {url}")
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
    print(f"[Overlay] {result.stdout.strip()}")


def start_recording():
    resp = obs_call("StartRecording")
    if resp.get('status') == 'ok':
        print(f"[OBS] Recording started: {resp.get('recordingFilename', 'unknown')}")
        return True
    print(f"[OBS] Failed: {resp}")
    return False


def stop_recording():
    resp = obs_call("StopRecording")
    if resp.get('status') == 'ok':
        print(f"[OBS] Recording stopped")
        return True
    print(f"[OBS] Stop failed: {resp}")
    return False


def is_recording():
    resp = obs_call("GetRecordingStatus")
    return resp.get('isRecording', False)


def open_streamer_page(streamer):
    url = f"https://chaturbate.com/{streamer}/"
    open_chrome(url)
    time.sleep(3)
    close_overlay()


def fetch_via_proxy(url):
    """Fetch URL via proxy."""
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=__import__('ssl')._create_unverified_context()) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"[API] Fetch error: {e}")
        return None


def listen_events():
    """Main event listener loop."""
    url = f"{EVENTS_API_URL}/events/{USERNAME}/{TOKEN}/"
    print(f"[Listener] Starting Events API listener for @{USERNAME}")
    print(f"[Listener] Monitoring followed broadcasters. Waiting for broadcastStart...")
    
    while True:
        data = fetch_via_proxy(url)
        if data is None:
            print("[Listener] Connection failed, retrying in 10s...")
            time.sleep(10)
            continue
        
        events = data.get('events', [])
        if events:
            for event in events:
                event_type = event.get('type', '')
                broadcaster = event.get('broadcaster', '')
                if event_type == 'broadcastStart':
                    print(f"\n{'='*50}")
                    print(f"[LIVE] @{broadcaster} has started broadcasting!")
                    print(f"{'='*50}")
                    
                    # Open Chrome and start recording
                    open_streamer_page(broadcaster)
                    if start_recording():
                        print(f"[DONE] Now recording @{broadcaster}")
                        print(f"[DONE] Say 'stop recording' or 'jarvis stop' to stop")
                    else:
                        print(f"[ERROR] Could not start recording")
                elif event_type == 'broadcastStop':
                    print(f"[OFFLINE] @{broadcaster} has stopped broadcasting")
                    if is_recording():
                        print("[OBS] Streamer went offline, stopping recording...")
                        stop_recording()
                else:
                    print(f"[Event] {event_type} from @{broadcaster}")
        
        next_url = data.get('nextUrl')
        if next_url:
            url = next_url
        else:
            print("[Listener] No nextUrl in response, restarting...")
            url = f"{EVENTS_API_URL}/events/{USERNAME}/{TOKEN}/"
            time.sleep(5)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "listen"
    
    if cmd == "listen":
        try:
            listen_events()
        except KeyboardInterrupt:
            print("\n[Listener] Stopped by user")
            if is_recording():
                print("[OBS] Stopping recording before exit...")
                stop_recording()
            sys.exit(0)
    elif cmd == "status":
        resp = obs_call("GetRecordingStatus")
        print(json.dumps(resp, indent=2))
    elif cmd == "start":
        ok = start_recording()
        sys.exit(0 if ok else 1)
    elif cmd == "stop":
        ok = stop_recording()
        sys.exit(0 if ok else 1)
    elif cmd == "open":
        open_streamer_page(sys.argv[2] if len(sys.argv) > 2 else STREAMER)
    else:
        print(f"Usage: {sys.argv[0]} [listen|status|start|stop|open <streamer>]")