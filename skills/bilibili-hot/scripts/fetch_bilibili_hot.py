#!/usr/bin/env python3
"""B站热门日报生成"""
import asyncio
import edge_tts
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path.home() / "Documents/TTSoutputs/每日热点"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_bilibili_hot():
    """获取B站热门视频"""
    import subprocess
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
    
    result = subprocess.run(
        ["curl", "-s", "--max-time", "10", url,
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
         "-H", "Referer: https://www.bilibili.com/",
         "-H", "Origin: https://www.bilibili.com"],
        capture_output=True, text=True
    )
    
    data = json.loads(result.stdout)
    
    if data['code'] != 0:
        raise Exception(f"B站API错误: {data['message']}")
    
    return data['data']['list']

def format_number(num):
    """格式化数字"""
    if num >= 100000000:
        return f"{num/100000000:.1f}亿"
    elif num >= 10000:
        return f"{num/10000:.1f}万"
    else:
        return str(num)

def clean_title(title):
    """清理标题中的特殊字符"""
    # 移除emoji和不必要的符号但保留核心内容
    title = re.sub(r'[^\w\s\u4e00-\u9fff\-_]', '', title)
    return title.strip()

def generate_report(videos):
    """生成播报文字"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    lines = [f"B站热门日报 - {today}"]
    lines.append("")
    
    for i, video in enumerate(videos[:10], 1):
        title = clean_title(video['title'])
        author = video['owner']['name']
        views = format_number(video['stat']['view'])
        likes = format_number(video['stat']['like'])
        category = video['tname']
        
        lines.append(f"第{i}名：{title}")
        lines.append(f"UP主：{author} | 播放：{views} | 点赞：{likes} | 分区：{category}")
        lines.append("")
    
    lines.append("以上就是今天的B站热门视频，我是Jarvis，明天见！")
    
    return "\n".join(lines)

async def generate_tts(text, output_path):
    """生成TTS音频"""
    communicate = edge_tts.Communicate(
        text,
        voice="zh-CN-XiaoxiaoNeural",
        rate="-25%",
        pitch="+0Hz"
    )
    await communicate.save(str(output_path))

async def main():
    print("正在获取B站热门...")
    videos = fetch_bilibili_hot()
    print(f"获取到 {len(videos)} 条热门视频")
    
    print("正在生成播报文字...")
    report = generate_report(videos)
    
    # 保存文字版
    today_str = datetime.now().strftime("%Y%m%d")
    txt_path = OUTPUT_DIR / f"热点日报_{today_str}.txt"
    txt_path.write_text(report, encoding='utf-8')
    print(f"文字版已保存: {txt_path}")
    
    # 生成语音
    mp3_path = OUTPUT_DIR / f"热点日报_{today_str}.mp3"
    print("正在生成语音...")
    await generate_tts(report, mp3_path)
    print(f"语音已保存: {mp3_path}")
    
    return str(mp3_path)

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n完成！语音文件: {result}")
