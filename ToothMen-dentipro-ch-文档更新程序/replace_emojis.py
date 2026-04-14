#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量替换emoji字符
"""

import re

def replace_emojis_in_file(file_path):
    """替换文件中的emoji字符"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换emoji为文本
    replacements = {
        '🔍': '[DEBUG]',
        '❌': '[ERROR]',
        '📁': '[FOLDER]',
        '📄': '[FILE]',
        '📂': '[OPEN]',
        '📝': '[DOC]',
        '✅': '[SUCCESS]',
        '⚠️': '[WARNING]',
        '🚀': '[ROCKET]',
        '🧹': '[CLEAN]',
        '💾': '[SAVE]',
        '⬆': '[UP]',
        '⬇': '[DOWN]'
    }
    
    for emoji, text in replacements.items():
        content = content.replace(emoji, text)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已处理文件: {file_path}")

if __name__ == "__main__":
    replace_emojis_in_file("main_simple_fixed.py")