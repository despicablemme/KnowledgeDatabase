#!/usr/bin/env python3
"""电子书TTS语音生成"""
import asyncio
import edge_tts
import sys
import re
from pathlib import Path
from typing import List, Tuple

SOURCE_DIR = Path.home() / "Documents/TTSoutputs"
OUTPUT_DIR = SOURCE_DIR

# 章节标题匹配模式
CHAPTER_PATTERNS = [
    r'^第([一二三四五六七八九十百千万零〇\\d]+)[回章节卷篇部]',
    r'^[第][一二三四五六七八九十百千万\\d]+[回章节卷篇部]',
    r'^(CHAPTER|Chapter|chapter)\s+\d+',
    r'^第\s*\d+\s*[回章节卷篇部]',
    r'^\d+\.\s*.+',
    r'^第[一二三四五六七八九十百千万\\d]+?[回章节]',
]

def detect_chapters(text: str) -> List[Tuple[str, int]]:
    """检测文本中的章节标题，返回 (标题, 起始位置) 列表"""
    chapters = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        for pattern in CHAPTER_PATTERNS:
            if re.match(pattern, line):
                chapters.append((line, i))
                break
    
    return chapters

def split_by_chapters(text: str, chapters: List[Tuple[str, int]]) -> List[Tuple[str, str]]:
    """按章节分割文本，返回 [(章节标题, 章节内容)]"""
    if not chapters:
        return [("全文", text)]
    
    result = []
    for idx, (title, start_pos) in enumerate(chapters):
        if idx + 1 < len(chapters):
            end_pos = chapters[idx + 1][1]
        else:
            end_pos = len(text.split('\n'))
        
        lines = text.split('\n')[start_pos:end_pos]
        content = '\n'.join(lines)
        result.append((title, content))
    
    return result

async def generate_audio(text: str, output_path: Path) -> bool:
    """生成单个音频文件"""
    if output_path.exists():
        print(f"跳过（已存在）: {output_path.name}", flush=True)
        return True
    
    try:
        communicate = edge_tts.Communicate(
            text,
            voice="zh-CN-XiaoxiaoNeural",
            rate="+10%",
            pitch="-5Hz"
        )
        await communicate.save(str(output_path))
        print(f"生成完成: {output_path.name}", flush=True)
        return True
    except Exception as e:
        print(f"错误: {output_path.name} - {e}", flush=True)
        return False

async def process_book(book_name: str, txt_file: Path):
    """处理整本书"""
    book_dir = SOURCE_DIR / book_name
    book_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"开始处理: {book_name}", flush=True)
    
    # 读取文本
    try:
        text = txt_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = txt_file.read_text(encoding="gbk")
        except:
            print(f"无法读取文件编码: {txt_file}")
            return
    
    # 检测章节
    chapters = detect_chapters(text)
    print(f"检测到 {len(chapters)} 个章节", flush=True)
    
    if not chapters:
        # 无章节标题，整本作为一个章节
        chapter_list = [("全文", text)]
    else:
        chapter_list = split_by_chapters(text, chapters)
    
    # 生成音频
    for idx, (title, content) in enumerate(chapter_list, 1):
        # 清理标题中的非法字符
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        if len(safe_title) > 50:
            safe_title = safe_title[:50]
        
        txt_name = f"{idx:03d}_{safe_title}.txt"
        mp3_name = f"{idx:03d}_{safe_title}.mp3"
        
        txt_path = book_dir / txt_name
        mp3_path = book_dir / mp3_name
        
        # 保存文本
        txt_path.write_text(content, encoding="utf-8")
        
        # 生成音频
        await generate_audio(content, mp3_path)
        
        print(f"[{idx}/{len(chapter_list)}] {title}", flush=True)
    
    print(f"全部完成！共 {len(chapter_list)} 章", flush=True)

async def main():
    if len(sys.argv) < 3:
        print("用法: python3 generate_tts.py <书名> <文本文件路径>")
        sys.exit(1)
    
    book_name = sys.argv[1]
    txt_file = Path(sys.argv[2])
    
    if not txt_file.exists():
        print(f"文件不存在: {txt_file}")
        sys.exit(1)
    
    await process_book(book_name, txt_file)

if __name__ == "__main__":
    asyncio.run(main())
