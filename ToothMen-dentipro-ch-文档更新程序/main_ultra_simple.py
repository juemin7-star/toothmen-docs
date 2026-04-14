#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 - 超简单版
只包含基本功能，解决启动问题
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import json
from pathlib import Path

class ToothMenDocsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ToothMen文档管理工具 - 超简单版")
        self.root.geometry("1200x800")
        
        # 项目路径
        self.project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
        self.docs_folder = self.project_path / "docs"
        
        # 确保docs文件夹存在
        self.docs_folder.mkdir(exist_ok=True)
        
        # 创建UI
        self.create_widgets()
        
        # 刷新文件夹结构
        self.refresh_folder_structure()
        
        # 记录日志
        self.log("程序启动完成")
    
    def create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = tk.Label(main_frame, text="📁 ToothMen文档管理系统", 
                              font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 文件夹结构区域
        folder_frame = ttk.LabelFrame(main_frame, text="文档文件夹结构", padding="10")
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        folder_frame.rowconfigure(0, weight=1)
        
        # 树形视图
        self.tree = ttk.Treeview(folder_frame, columns=("类型", "文件数"), show="tree headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 列配置
        self.tree.column("#0", width=400)
        self.tree.column("类型", width=100)
        self.tree.column("文件数", width=80)
        
        # 列标题
        self.tree.heading("#0", text="文件夹/文件")
        self.tree.heading("类型", text="类型")
        self.tree.heading("文件数", text="文件数")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(folder_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=("Consolas", 9), height=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))
        
        refresh_btn = ttk.Button(button_frame, text="刷新文件夹", 
                                command=self.refresh_folder_structure)
        refresh_btn.grid(row=0, column=0, padx=5)
        
        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.quit)
        exit_btn.grid(row=0, column=1, padx=5)
    
    def refresh_folder_structure(self):
        """刷新文件夹结构"""
        try:
            # 清空树
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.log(f"监控文件夹路径: {self.docs_folder}")
            
            # 检查文件夹是否存在
            if not self.docs_folder.exists():
                self.log(f"错误: 监控文件夹不存在: {self.docs_folder}")
                return
            
            # 获取所有文件夹
            all_folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    all_folders.append(item.name)
            
            self.log(f"找到 {len(all_folders)} 个文件夹")
            
            # 按字母顺序排序
            display_folders = sorted(all_folders)
            
            total_folders = len(display_folders)
            
            for folder_name in display_folders:
                folder_path = self.docs_folder / folder_name
                
                # 获取文件
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                for file in folder_path.glob("*.md"):
                    mdx_files.append(file.name)
                
                sorted_files = sorted(mdx_files)
                
                # 添加文件夹到树
                folder_item = self.tree.insert("", "end", text=f"📂 {folder_name}/", 
                                              values=("文件夹", str(len(sorted_files))))
                
                # 添加文件到树
                for file_name in sorted_files:
                    if file_name.endswith('.mdx'):
                        icon = "📄"
                        file_type = "MDX文件"
                    elif file_name.endswith('.md'):
                        icon = "📝"
                        file_type = "MD文件"
                    else:
                        icon = "📎"
                        file_type = "其他文件"
                    
                    self.tree.insert(folder_item, "end", text=f"{icon} {file_name}", 
                                    values=(file_type, "1"))
            
            self.log(f"成功: 文件夹结构已刷新，共检测到 {total_folders} 个文件夹")
            
        except Exception as e:
            self.log(f"错误: 刷新文件夹结构失败: {str(e)}")
    
    def log(self, message):
        """记录日志"""
        timestamp = tk.StringVar()
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()