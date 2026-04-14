#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试按钮状态问题
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主程序
from main_restored_layout import ToothMenDocsManager

def test_button_states():
    """测试按钮状态"""
    root = tk.Tk()
    root.title("测试按钮状态")
    
    # 创建应用实例
    app = ToothMenDocsManager(root)
    
    # 等待窗口初始化
    root.update()
    
    print("=" * 60)
    print("测试按钮状态")
    print("=" * 60)
    
    # 检查step_buttons
    print(f"step_buttons数量: {len(app.step_buttons)}")
    print(f"deployment_steps: {app.deployment_steps}")
    
    # 检查按钮状态
    for i, btn in enumerate(app.step_buttons):
        state = btn["state"]
        text = btn["text"]
        print(f"按钮 {i} ('{text}'): 状态 = {state}")
    
    print("\n测试开始流程按钮点击...")
    
    # 模拟点击开始流程按钮
    def simulate_start_workflow():
        print("\n模拟点击'开始流程'按钮...")
        app.start_workflow()
        
        # 检查按钮状态变化
        print("\n点击后按钮状态:")
        for i, btn in enumerate(app.step_buttons):
            state = btn["state"]
            text = btn["text"]
            print(f"按钮 {i} ('{text}'): 状态 = {state}")
        
        print(f"\n开始流程按钮状态: {app.start_workflow_btn['state']}")
        print(f"结束流程按钮状态: {app.deploy_end_btn['state']}")
    
    # 添加测试按钮
    test_btn = ttk.Button(root, text="测试开始流程", command=simulate_start_workflow)
    test_btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_button_states()