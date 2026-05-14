#!/usr/bin/env python3
"""
visual-select.py - 图片搜索与下载脚本（去重版）
Usage: python3 visual-select.py <theme> <output_dir> [count]
Themes: city, landscape, portrait, street

新功能：
- 记录已发送图片ID，绕过重复
- 分页获取新图片
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# 历史记录文件
HISTORY_FILE = Path.home() / '.openclaw' / 'agents' / 'visual' / 'visual-history.json'
MAX_HISTORY = 100  # 每个主题保留最近100个ID

def load_history():
    """加载历史记录"""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except:
            pass
    return {}

def save_history(history):
    """保存历史记录"""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

def add_to_history(theme, image_ids):
    """添加已使用的图片ID到历史"""
    history = load_history()
    if theme not in history:
        history[theme] = []
    # 添加新ID到前面
    for img_id in image_ids:
        if img_id in history[theme]:
            history[theme].remove(img_id)
        history[theme].insert(0, img_id)
    # 限制每个主题的ID数量
    history[theme] = history[theme][:MAX_HISTORY]
    save_history(history)

def search_pixabay(query, theme, per_page=15):
    """通过 pixabay MCP 搜索图片（去重+分页）"""
    history = load_history()
    exclude_ids = history.get(theme, [])[:20]  # 排除最近20个
    
    # 尝试多个分页，寻找未被排除的图片
    for page in range(1, 5):
        cmd = [
            '/opt/homebrew/bin/mcporter', 'call', 'pixabay.search_pixabay_images',
            f'query={query}', f'per_page={per_page}', f'page={page}', 'order=latest'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            continue
        try:
            data = json.loads(result.stdout)
            hits = data.get('hits', [])
            if not hits:
                continue
            # 过滤掉已使用过的ID
            filtered = [hit for hit in hits if str(hit.get('id', '')) not in exclude_ids]
            if filtered:
                # 返回 (urls, ids) 元组
                urls = [hit['largeImageURL'] for hit in filtered]
                ids = [str(hit['id']) for hit in filtered]
                return urls, ids
        except:
            continue
    return [], []

def search_pexels(query, theme, per_page=15):
    """通过 pexels MCP 搜索图片（去重+分页）"""
    history = load_history()
    exclude_ids = history.get(theme, [])[:20]
    
    for page in range(1, 5):
        cmd = [
            '/opt/homebrew/bin/mcporter', 'call', 'pexels.searchPhotos',
            f'query={query}', f'per_page={per_page}', f'page={page}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            continue
        try:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if not photos:
                continue
            # 过滤掉已使用过的ID
            filtered = [photo for photo in photos if str(photo.get('id', '')) not in exclude_ids]
            if filtered:
                urls = [photo['src']['large'] for photo in filtered]
                ids = [str(photo['id']) for photo in filtered]
                return urls, ids
        except:
            continue
    return [], []

def download_image(url, path):
    """下载单张图片"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: visual-select.py <theme> <output_dir> [count]")
        sys.exit(1)
    
    theme = sys.argv[1]
    output_dir = sys.argv[2]
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    # 主题配置
    themes = {
        'city': ('city urban architecture', 'ct_'),
        'landscape': ('landscape nature scenic', 'ls_'),
        'portrait': ('portrait people model', 'pt_'),
        'street': ('street documentary culture', 'st_')
    }
    
    if theme not in themes:
        print(f"Unknown theme: {theme}", file=sys.stderr)
        sys.exit(1)
    
    query, prefix = themes[theme]
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 搜索图片（带去重）
    urls, ids = search_pixabay(query, theme, per_page=15)
    if not urls:
        urls, ids = search_pexels(query, theme, per_page=15)
    
    if not urls:
        print("No images found", file=sys.stderr)
        sys.exit(1)
    
    # 下载图片
    downloaded = []
    downloaded_ids = []
    for i, (url, img_id) in enumerate(zip(urls[:count], ids[:count]), 1):
        path = os.path.join(output_dir, f"{prefix}{i}.jpg")
        if download_image(url, path):
            downloaded.append(path)
            downloaded_ids.append(img_id)
            print(f"Downloaded: {path} (id: {img_id})")
    
    if not downloaded:
        sys.exit(1)
    
    # 记录到历史
    add_to_history(theme, downloaded_ids)
    
    # 输出下载的文件列表（供agent读取）
    print(f"\nDOWNLOADED:{','.join(downloaded)}")

if __name__ == '__main__':
    main()
