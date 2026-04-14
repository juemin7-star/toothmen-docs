#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.16 - 快速启动版
解决EXE启动跳动问题
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import json
import threading
import subprocess
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 导入自定义模块
from deployment_manager_new import DeploymentManager
from logger import Logger
from mdx_checker import MDXChecker

class ToothMenDocsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v3.16 - 快速启动版")
        self.root.geometry("1400x1000")
        
        # 立即显示窗口，避免闪烁
        self.root.update_idletasks()
        
        # 设置图标
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # 项目路径
        self.project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
        self.docs_folder = self.project_path / "docs"
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 确保docs文件夹存在
        self.docs_folder.mkdir(exist_ok=True)
        
        # 创建UI（立即显示）
        self.create_widgets()
        
        # 显示初始消息
        self.log("🚀 程序启动中...", "info")
        
        # 在后台初始化耗时的组件
        threading.Thread(target=self.delayed_init, daemon=True).start()
    
    def delayed_init(self):
        """延迟初始化耗时的组件"""
        try:
            # 初始化管理器（可能耗时）
            self.deployment_manager = DeploymentManager(self.project_path)
            self.logger = Logger()
            self.mdx_checker = MDXChecker(self.docs_folder)
            
            # 特殊文件夹配置
            self.reverse_order_folders = ["补丁更新日志", "patch-notes", "更新记录", "changelog"]
            
            # 加载配置
            self.config = self.load_config()
            
            # 部署流程状态
            self.deployment_started = False
            self.deployment_steps = [
                "刷新文件结构",
                "生成侧边栏", 
                "本地构建测试",
                "本地预览",
                "自动部署"
            ]
            self.current_step = 0
            self.step_buttons = []
            
            # 在主线程中完成初始化
            self.root.after(0, self.finish_init)
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 初始化失败: {str(e)}", "error"))
    
    def finish_init(self):
        """完成初始化"""
        self.log("✅ 程序初始化完成", "success")
        
        # 刷新文件夹结构（在后台）
        threading.Thread(target=self.refresh_folder_structure, daemon=True).start()
        
        # 启用按钮
        self.enable_buttons()
    
    def enable_buttons(self):
        """启用所有按钮"""
        # 启用排序按钮
        self.btn_save_sort.config(state=tk.NORMAL)
        
        # 启用功能按钮
        self.complete_workflow_btn.config(state=tk.NORMAL)
        self.check_mdx_btn.config(state=tk.NORMAL)
        self.deploy_start_btn.config(state=tk.NORMAL)
        self.clean_cache_btn.config(state=tk.NORMAL)
        self.verify_deploy_btn.config(state=tk.NORMAL)
        
        # 启用调试按钮
        for btn in self.debug_buttons:
            btn.config(state=tk.NORMAL)
    
    def load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                "project_path": str(self.project_path),
                "docs_folder": str(self.docs_folder),
                "sidebars_path": str(self.sidebars_path),
                "npm_path": "npm",
                "git_path": r"C:\Program Files\Git\cmd\git.exe",
                "auto_refresh": True,
                "log_level": "INFO",
                "reverse_order_folders": self.reverse_order_folders
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v3.16 - 快速启动版", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 创建各个区域
        self.create_folder_structure_area(main_frame)
        self.create_control_area(main_frame)
        self.create_log_and_debug_area(main_frame)
    
    def create_folder_structure_area(self, parent):
        """创建文件夹结构显示区域"""
        folder_frame = ttk.LabelFrame(parent, text="文档文件夹结构", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=3)
        folder_frame.columnconfigure(1, weight=1)
        folder_frame.rowconfigure(0, weight=1)
        folder_frame.rowconfigure(1, weight=0)
        
        # 左侧：文件夹树
        tree_frame = ttk.Frame(folder_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.rowconfigure(1, weight=0)
        
        self.tree = ttk.Treeview(tree_frame, columns=("type", "count"), show="tree headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.tree.heading("#0", text="文件/文件夹结构")
        self.tree.heading("type", text="类型")
        self.tree.heading("count", text="数量")
        
        self.tree.column("#0", width=500, minwidth=400)
        self.tree.column("type", width=100, minwidth=80)
        self.tree.column("count", width=80, minwidth=60)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.config(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.config(xscrollcommand=h_scrollbar.set)
        
        # 右侧：排序按钮
        sort_frame = ttk.Frame(folder_frame)
        sort_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(10, 0))
        
        ttk.Label(sort_frame, text="📁 文件夹排序", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        self.btn_folder_up = tk.Button(sort_frame, text="⬆ 上移文件夹", 
                                      command=self.move_folder_up, width=14, state=tk.DISABLED)
        self.btn_folder_up.pack(pady=3)
        
        self.btn_folder_down = tk.Button(sort_frame, text="⬇ 下移文件夹", 
                                        command=self.move_folder_down, width=14, state=tk.DISABLED)
        self.btn_folder_down.pack(pady=3)
        
        ttk.Label(sort_frame, text="📄 文件排序", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        
        self.btn_file_up = tk.Button(sort_frame, text="⬆ 上移文件", 
                                    command=self.move_file_up, width=14, state=tk.DISABLED)
        self.btn_file_up.pack(pady=3)
        
        self.btn_file_down = tk.Button(sort_frame, text="⬇ 下移文件", 
                                      command=self.move_file_down, width=14, state=tk.DISABLED)
        self.btn_file_down.pack(pady=3)
        
        self.btn_save_sort = tk.Button(sort_frame, text="💾 保存排序", 
                                      command=self.save_sort_config, width=14, 
                                      bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.btn_save_sort.pack(pady=(20, 0))
        
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection)
    
    def create_control_area(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        left_frame = ttk.Frame(control_frame)
        left_frame.grid(row=0, column=0, sticky=tk.W)
        
        self.complete_workflow_btn = ttk.Button(left_frame, text="🚀 完整工作流", 
                                               command=self.complete_workflow, state=tk.DISABLED)
        self.complete_workflow_btn.grid(row=0, column=0, padx=5)
        
        self.check_mdx_btn = ttk.Button(left_frame, text="检测MDX语法", 
                                       command=self.check_mdx_syntax, state=tk.DISABLED)
        self.check_mdx_btn.grid(row=0, column=1, padx=5)
        
        self.deploy_start_btn = ttk.Button(left_frame, text="开始部署", 
                                          command=self.start_deployment, state=tk.DISABLED)
        self.deploy_start_btn.grid(row=0, column=2, padx=5)
        
        self.deploy_end_btn = ttk.Button(left_frame, text="结束流程", 
                                        command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=3, padx=5)
        
        self.verify_deploy_btn = ttk.Button(left_frame, text="验证部署", 
                                           command=self.verify_deployment, state=tk.DISABLED)
        self.verify_deploy_btn.grid(row=0, column=4, padx=5)
        
        self.clean_cache_btn = ttk.Button(left_frame, text="🧹 清理缓存", 
                                         command=self.clean_cache, state=tk.DISABLED)
        self.clean_cache_btn.grid(row=0, column=5, padx=5)
        
        right_frame = ttk.Frame(control_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.step_buttons = []
        for i, step in enumerate(["刷新文件结构", "生成侧边栏", "本地构建测试", "本地预览", "自动部署"]):
            btn = ttk.Button(right_frame, text=step, command=lambda s=step: self.execute_step(s), 
                           state=tk.DISABLED)
            btn.grid(row=0, column=i, padx=5)
            self.step_buttons.append(btn)
    
    def create_log_and_debug_area(self, parent):
        """创建日志和调试工具区域"""
        log_debug_frame = ttk.Frame(parent)
        log_debug_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_debug_frame.columnconfigure(0, weight=3)
        log_debug_frame.columnconfigure(1, weight=1)
        log_debug_frame.rowconfigure(0, weight=1)
        
        # 日志区域
        log_frame = ttk.LabelFrame(log_debug_frame, text="📝 操作日志", padding="10")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=("Consolas", 9), height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
        
        # 调试工具区域
        debug_frame = ttk.LabelFrame(log_debug_frame, text="🔧 调试工具", padding="10")
        debug_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        debug_frame.columnconfigure(0, weight=1)
        
        debug_buttons = [
            ("🌐 测试网络连接", self.test_network_connection),
            ("🔍 检查Git状态", self.check_git_status),
            ("📊 查看Git日志", self.show_git_log),
            ("🔄 手动推送Git", self.manual_git_push),
            ("🔧 Git连接诊断", self.diagnose_git_connection),
            ("🔑 切换到SSH", self.switch_to_ssh),
            ("🧹 清除npm缓存", self.clear_npm_cache),
            ("📂 打开docs文件夹", self.open_docs_folder),
            ("📁 打开项目文件夹", self.open_project_folder),
            ("🔍 检查配置文件", self.check_config_files),
        ]
        
        self.debug_buttons = []
        for i, (text, command) in enumerate(debug_buttons):
            btn = ttk.Button(debug_frame, text=text, command=command, width=20, state=tk.DISABLED)
            btn.grid(row=i, column=0, pady=2, sticky=tk.W)
            self.debug_buttons.append(btn)
    
    def log(self, message, level="info"):
        """记录日志"""
        if not hasattr(self, 'log_text'):
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
    
    # 注意：这里省略了其他方法，它们与原始版本相同
    # 为了简洁，只显示关键部分
    
    def refresh_folder_structure(self):
        """刷新文件夹结构"""
        try:
            # 清空树
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 获取所有文件夹
            all_folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    all_folders.append(item.name)
            
            # 读取排序配置文件
            sort_config_path = Path(__file__).parent / "sort_config.json"
            display_folders = []
            
            if sort_config_path.exists():
                with open(sort_config_path, 'r', encoding='utf-8') as f:
                    sort_config = json.load(f)
                
                for folder_name in sort_config.get("folders", []):
                    if folder_name in all_folders:
                        display_folders.append(folder_name)
                
                for folder_name in sorted(all_folders):
                    if folder_name not in display_folders:
                        display_folders.append(folder_name)
            else:
                display_folders = sorted(all_folders)
            
            total_folders = len(display_folders)
            
            for folder_name in display_folders:
                folder_path = self.docs_folder / folder_name
                
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                for file in folder_path.glob("*.md"):
                    mdx_files.append(file.name)
                
                sorted_files = []
                if sort_config_path.exists():
                    config_files = sort_config.get("files", {}).get(folder_name, [])
                    
                    for file_name in config_files:
                        possible_files = [
                            f"{file_name}.mdx",
                            f"{file_name}.md",
                            file_name
                        ]
                        
                        for possible_file in possible_files:
                            if (folder_path / possible_file).exists():
                                sorted_files.append(possible_file)
                                break
                    
                    for file_name in sorted(mdx_files):
                        file_base = file_name
                        if file_name.endswith('.mdx'):
                            file_base = file_name[:-4]
                        elif file_name.endswith('.md'):
                            file_base = file_name[:-3]
                        
                        if file_base not in [f.split('.')[0] for f in sorted_files]:
                            sorted_files.append(file_name)
                else:
                    sorted_files = sorted(mdx_files)
                
                folder_item = self.tree.insert("", "end", text=f"📂 {folder_name}/", values=("文件夹", str(len(sorted_files))))
                
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
                    
                    self.tree.insert(folder_item, "end", text=f"{icon} {file_name}", values=(file_type, "1"))
            
            self.log(f"✅ 文件夹结构已刷新，共检测到 {total_folders} 个文件夹", "success")
            
            # 启用排序按钮
            self.btn_folder_up.config(state=tk.NORMAL)
            self.btn_folder_down.config(state=tk.NORMAL)
            self.btn_file_up.config(state=tk.NORMAL)
            self.btn_file_down.config(state=tk.NORMAL)
            
        except Exception as e:
            self.log(f"❌ 刷新文件夹结构失败: {str(e)}", "error")
    
    # 其他方法（排序按钮方法、工作流方法等）与原始版本相同
    # 这里省略以保持简洁

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()