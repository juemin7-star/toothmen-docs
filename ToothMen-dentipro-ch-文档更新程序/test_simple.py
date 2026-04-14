#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的测试
"""

import tkinter as tk
from tkinter import ttk
import sys

print("测试开始...")

try:
    root = tk.Tk()
    root.title("简单测试")
    root.geometry("400x300")
    
    label = tk.Label(root, text="这是一个简单的测试窗口", font=("Arial", 14))
    label.pack(pady=50)
    
    button = tk.Button(root, text="关闭", command=root.quit)
    button.pack(pady=20)
    
    print("窗口创建成功，进入主循环...")
    root.mainloop()
    print("主循环结束")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    input("按Enter键退出...")