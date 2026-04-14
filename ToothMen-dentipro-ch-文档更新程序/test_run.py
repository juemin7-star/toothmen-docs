#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import json
from pathlib import Path

def test():
    """测试函数"""
    root = tk.Tk()
    root.title("测试窗口")
    root.geometry("800x600")
    
    # 项目路径
    project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
    docs_folder = project_path / "docs"
    
    print(f"[DEBUG] 监控文件夹路径: {docs_folder}")
    print(f"[DEBUG] 文件夹是否存在: {docs_folder.exists()}")
    
    if docs_folder.exists():
        # 获取所有文件夹
        all_folders = []
        for item in docs_folder.iterdir():
            if item.is_dir():
                all_folders.append(item.name)
        
        print(f"[DEBUG] 找到 {len(all_folders)} 个文件夹: {all_folders}")
    else:
        print("[ERROR] 监控文件夹不存在")
    
    # 创建简单的UI
    label = tk.Label(root, text="测试窗口 - 文件夹监控", font=("Arial", 14))
    label.pack(pady=20)
    
    text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10), height=20)
    text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    text.insert(tk.END, f"监控文件夹路径: {docs_folder}\n")
    text.insert(tk.END, f"文件夹是否存在: {docs_folder.exists()}\n")
    
    if docs_folder.exists():
        text.insert(tk.END, f"找到 {len(all_folders)} 个文件夹:\n")
        for folder in all_folders:
            text.insert(tk.END, f"  - {folder}\n")
    else:
        text.insert(tk.END, "[ERROR] 监控文件夹不存在\n")
    
    root.mainloop()

if __name__ == "__main__":
    test()