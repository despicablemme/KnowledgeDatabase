#!/bin/bash
# Script to search for Detective Conan on seedhub.cc with anti-detection measures

echo "=== Step 1: Navigate to seedhub.cc ==="
openclaw browser --browser-profile openclaw navigate "https://www.seedhub.cc"
sleep 5

echo "=== Step 2: Take snapshot to find search box ==="
openclaw browser --browser-profile openclaw snapshot --format ai --limit 2000 2>&1 | head -50

echo "=== Step 3: Click search box ==="
openclaw browser --browser-profile openclaw click e10
sleep 2

echo "=== Step 4: Type search query ==="
openclaw browser --browser-profile openclaw type e10 "名侦探柯南 666"
sleep 3

echo "=== Step 5: Press Enter ==="
openclaw browser --browser-profile openclaw press Enter
sleep 5

echo "=== Step 6: Take snapshot of results ==="
openclaw browser --browser-profile openclaw snapshot --format ai --limit 5000 2>&1
