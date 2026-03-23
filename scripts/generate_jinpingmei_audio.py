#!/usr/bin/env python3
"""生成金瓶梅有声书"""
import asyncio
import edge_tts
import os
import sys
from pathlib import Path

SOURCE_DIR = Path.home() / "Documents/TTSoutputs/金瓶梅"
OUTPUT_DIR = SOURCE_DIR

async def generate_audio(file_path: Path):
    """为一个文本文件生成语音"""
    text = file_path.read_text(encoding="utf-8")
    output_path = OUTPUT_DIR / f"{file_path.stem}.mp3"
    
    if output_path.exists():
        print(f"跳过: {output_path.name}", flush=True)
        return
    
    communicate = edge_tts.Communicate(
        text,
        voice="zh-CN-XiaoxiaoNeural",
        rate="-25%",
        pitch="+0Hz"
    )
    await communicate.save(str(output_path))
    print(f"完成: {output_path.name}", flush=True)

async def main():
    files = sorted(SOURCE_DIR.glob("*.txt"))
    total = len(files)
    print(f"共 {total} 个文件，开始生成...", flush=True)
    
    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{total}] {file_path.name}", flush=True)
        try:
            await generate_audio(file_path)
        except Exception as e:
            print(f"错误: {file_path.name} - {e}", flush=True)
    
    print("全部完成！", flush=True)

if __name__ == "__main__":
    asyncio.run(main())