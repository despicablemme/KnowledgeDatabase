#!/usr/bin/env python3
"""电子书格式转换：统一转为 UTF-8 txt"""
import sys
import re
from pathlib import Path

def convert_txt(file_path: Path) -> str:
    """读取 txt 文件"""
    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法解码: {file_path}")

def convert_epub(file_path: Path) -> str:
    """解析 epub 文件"""
    try:
        import ebooklib
        from ebooklib import epub
    except ImportError:
        print("需要安装: pip install ebooklib")
        sys.exit(1)
    
    book = epub.read_epub(str(file_path))
    text_parts = []
    
    for item in book.get_items():
        if item.get_type() == 9:  # HTML
            content = item.get_content().decode('utf-8', errors='ignore')
            # 简单去除 HTML 标签
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                text_parts.append(text)
    
    return '\n'.join(text_parts)

def convert_mobi(file_path: Path) -> str:
    """解析 mobi 文件"""
    try:
        import mobi
    except ImportError:
        print("需要安装: pip install python-mobi")
        sys.exit(1)
    
    from mobi import MobiBook
    book = MobiBook(str(file_path))
    return book.extract()

def convert_pdf(file_path: Path) -> str:
    """解析 pdf 文件"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("需要安装: pip install pymupdf")
        sys.exit(1)
    
    doc = fitz.open(str(file_path))
    text_parts = []
    
    for page in doc:
        text = page.get_text()
        if text.strip():
            text_parts.append(text)
    
    return '\n'.join(text_parts)

def convert_ebook(file_path: Path, output_path: Path = None) -> str:
    """转换电子书为纯文本"""
    suffix = file_path.suffix.lower()
    
    if suffix == '.txt':
        text = convert_txt(file_path)
    elif suffix == '.epub':
        text = convert_epub(file_path)
    elif suffix in ['.mobi', '.azw', '.azw3']:
        text = convert_mobi(file_path)
    elif suffix == '.pdf':
        text = convert_pdf(file_path)
    else:
        raise ValueError(f"不支持的格式: {suffix}")
    
    if output_path:
        output_path.write_text(text, encoding='utf-8')
        print(f"已保存到: {output_path}")
    
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 convert_ebook.py <电子书路径> [输出txt路径]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        text = convert_ebook(file_path, output_path)
        print(f"转换完成，共 {len(text)} 字符")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
