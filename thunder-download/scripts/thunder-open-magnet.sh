#!/bin/bash
# thunder-open-magnet.sh
# Opens a magnet link in Thunder and initiates download

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <magnet-link>"
    echo "Example: $0 'magnet:?xt=urn:btih:...'"
    exit 1
fi

MAGNET="$1"

# Base64 encode the magnet link
ENCODED=$(echo -n "$MAGNET" | base64)

# Construct thunder:// URL
THUNDER_URL="thunder://$ENCODED"

echo "Opening Thunder with magnet link..."
open "$THUNDER_URL"

# Wait for Thunder to process
sleep 3

# Activate Thunder to bring window to front
osascript -e 'tell application "Thunder" to activate' 2>/dev/null || true
sleep 1

# Get current windows
echo "Checking Thunder windows..."
WINDOWS=$(osascript -e 'tell application "System Events" to tell process "Thunder" to get windows' 2>/dev/null || echo "")

if [ -z "$WINDOWS" ]; then
    echo "Warning: No Thunder windows detected. Is Thunder installed and running?"
    exit 1
fi

echo "Thunder window detected: $WINDOWS"

# Get download button position
echo "Getting download button position..."
osascript -e 'tell application "System Events" to tell process "Thunder" to tell button "立即下载" of window 1 to get {position, size}' 2>/dev/null || {
    echo "Could not find download button. Manual intervention may be required."
    exit 1
}

echo "Done. Please check Thunder window for download status."
