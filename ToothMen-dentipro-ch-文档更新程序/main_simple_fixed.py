#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.16 - 简单修复版
解决EXE启动跳动问题的最简单方案
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
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v3.16")
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
        
        # 特殊文件夹配置（需要倒序排序）
        self.reverse_order_folders = ["补丁更新日志", "patch-notes", "更新记录", "changelog"]
        
        # 确保docs文件夹存在
        self.docs_folder.mkdir(exist_ok=True)
        
        # 部署步骤（用于按钮创建）
        self.deployment_steps = ["刷新文件结构", "生成侧边栏", "本地构建测试", "本地预览", "自动部署"]
        
        # 显示简单的加载提示
        self.loading_label = ttk.Label(self.root, text="正在启动...", font=("Arial", 12))
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update()
        
        # 创建UI（先创建界面）
        self.create_widgets()
        
        # 直接在主线程中初始化（避免后台线程问题）
        self.root.after(100, self.init_in_background)
    
    def init_in_background(self):
        """在后台初始化"""
        try:
            # 加载配置
            self.config = self.load_config()
            
            # 部署流程状态
            self.deployment_started = False
            self.current_step = 0
            
            # 在主线程中完成初始化
            self.root.after(0, self.finish_init)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.show_error(msg))
    
    def finish_init(self):
        """完成初始化"""
        # 隐藏加载提示
        self.loading_label.destroy()
        
        # 显示调试信息
        debug_info = f"项目路径: {self.project_path}\n"
        debug_info += f"文档文件夹: {self.docs_folder}\n"
        debug_info += f"文件夹是否存在: {self.docs_folder.exists()}"
        
        # 在日志中显示
        self.log(f"[DEBUG] {debug_info}", "info")
        
        # 刷新文件夹结构
        self.refresh_folder_structure()
        
        # 记录日志
        self.log("[SUCCESS] 程序启动完成", "success")
        
        # 启用所有按钮
        self.enable_all_buttons()
    
    def show_error(self, error_msg):
        """显示错误"""
        self.loading_label.destroy()
        messagebox.showerror("启动错误", f"程序启动失败:\n{error_msg}")
        self.log(f"[ERROR] 启动失败: {error_msg}", "error")
    
    def enable_all_buttons(self):
        """启用所有按钮"""
        # 启用排序按钮
        self.btn_save_sort.config(state=tk.NORMAL)
        
        # 启用功能按钮
        self.complete_workflow_btn.config(state=tk.NORMAL)
        self.check_mdx_btn.config(state=tk.NORMAL)
        self.deploy_start_btn.config(state=tk.NORMAL)
        self.clean_cache_btn.config(state=tk.NORMAL)
        self.verify_deploy_btn.config(state=tk.NORMAL)
        
        # 启用部署步骤按钮
        for btn in self.step_buttons:
            btn.config(state=tk.NORMAL)
        
        # 启用调试按钮
        for btn in self.debug_buttons:
            btn.config(state=tk.NORMAL)
    
    def load_config(self):
        """加载配置文件"""
        config_path = self.project_path / "config.json"
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
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v3.16", 
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
        
        ttk.Label(sort_frame, text="[FOLDER] 文件夹排序", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        self.btn_folder_up = tk.Button(sort_frame, text="[UP] 上移文件夹", 
                                      command=self.move_folder_up, width=14, state=tk.DISABLED)
        self.btn_folder_up.pack(pady=3)
        
        self.btn_folder_down = tk.Button(sort_frame, text="[DOWN] 下移文件夹", 
                                        command=self.move_folder_down, width=14, state=tk.DISABLED)
        self.btn_folder_down.pack(pady=3)
        
        ttk.Label(sort_frame, text="[FILE] 文件排序", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        
        self.btn_file_up = tk.Button(sort_frame, text="[UP] 上移文件", 
                                    command=self.move_file_up, width=14, state=tk.DISABLED)
        self.btn_file_up.pack(pady=3)
        
        self.btn_file_down = tk.Button(sort_frame, text="[DOWN] 下移文件", 
                                      command=self.move_file_down, width=14, state=tk.DISABLED)
        self.btn_file_down.pack(pady=3)
        
        self.btn_save_sort = tk.Button(sort_frame, text="[SAVE] 保存排序", 
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
        
        self.complete_workflow_btn = ttk.Button(left_frame, text="[ROCKET] 完整工作流", 
                                               command=self.not_implemented, state=tk.DISABLED)
        self.complete_workflow_btn.grid(row=0, column=0, padx=5)
        
        self.check_mdx_btn = ttk.Button(left_frame, text="检测MDX语法", 
                                       command=self.not_implemented, state=tk.DISABLED)
        self.check_mdx_btn.grid(row=0, column=1, padx=5)
        
        self.deploy_start_btn = ttk.Button(left_frame, text="开始部署", 
                                          command=self.not_implemented, state=tk.DISABLED)
        self.deploy_start_btn.grid(row=0, column=2, padx=5)
        
        self.deploy_end_btn = ttk.Button(left_frame, text="结束流程", 
                                        command=self.not_implemented, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=3, padx=5)
        
        self.verify_deploy_btn = ttk.Button(left_frame, text="验证部署", 
                                           command=self.not_implemented, state=tk.DISABLED)
        self.verify_deploy_btn.grid(row=0, column=4, padx=5)
        
        self.clean_cache_btn = ttk.Button(left_frame, text="[CLEAN] 清理缓存", 
                                         command=self.not_implemented, state=tk.DISABLED)
        self.clean_cache_btn.grid(row=0, column=5, padx=5)
        
        right_frame = ttk.Frame(control_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.step_buttons = []
        for i, step in enumerate(self.deployment_steps):
            btn = ttk.Button(right_frame, text=step, command=self.not_implemented, 
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
        log_frame = ttk.LabelFrame(log_debug_frame, text="[DOC] 操作日志", padding="10")
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
            ("🌐 测试网络连接", self.not_implemented),
            ("[DEBUG] 检查Git状态", self.not_implemented),
            ("📊 查看Git日志", self.not_implemented),
            ("🔄 手动推送Git", self.not_implemented),
            ("🔧 Git连接诊断", self.not_implemented),
            ("🔑 切换到SSH", self.not_implemented),
            ("[CLEAN] 清除npm缓存", self.not_implemented),
            ("[OPEN] 打开docs文件夹", self.not_implemented),
            ("[FOLDER] 打开项目文件夹", self.not_implemented),
            ("[DEBUG] 检查配置文件", self.not_implemented),
        ]
        
        self.debug_buttons = []
        for i, (text, command) in enumerate(debug_buttons):
            btn = ttk.Button(debug_frame, text=text, command=self.not_implemented, width=20, state=tk.DISABLED)
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
    # 为了保持简洁，只显示关键部分
    
    def refresh_folder_structure(self):
        """刷新文件夹结构"""
        try:
            # 清空树
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 调试日志：显示监控的文件夹路径
            self.log(f"[DEBUG] 监控文件夹路径: {self.docs_folder}", "info")
            
            # 检查文件夹是否存在
            if not self.docs_folder.exists():
                self.log(f"[ERROR] 监控文件夹不存在: {self.docs_folder}", "error")
                return
            
            # 获取所有文件夹
            all_folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    all_folders.append(item.name)
            
            # 调试日志：显示找到的文件夹
            self.log(f"[DEBUG] 找到 {len(all_folders)} 个文件夹: {all_folders}", "info")
            
            # 读取排序配置文件
            sort_config_path = self.project_path / "sort_config.json"
            self.log(f"[DEBUG] 排序配置文件路径: {sort_config_path}", "info")
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
                
                folder_item = self.tree.insert("", "end", text=f"[OPEN] {folder_name}/", values=("文件夹", str(len(sorted_files))))
                
                for file_name in sorted_files:
                    if file_name.endswith('.mdx'):
                        icon = "[FILE]"
                        file_type = "MDX文件"
                    elif file_name.endswith('.md'):
                        icon = "[DOC]"
                        file_type = "MD文件"
                    else:
                        icon = "📎"
                        file_type = "其他文件"
                    
                    self.tree.insert(folder_item, "end", text=f"{icon} {file_name}", values=(file_type, "1"))
            
            self.log(f"[SUCCESS] 文件夹结构已刷新，共检测到 {total_folders} 个文件夹", "success")
            
        except Exception as e:
            self.log(f"[ERROR] 刷新文件夹结构失败: {str(e)}", "error")
    
    # ========== 排序按钮方法 ==========
    
    def move_folder_up(self):
        """上移文件夹"""
        selection = self.tree.selection()
        if not selection:
            self.log("[WARNING]  请先选择一个文件夹", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not item_text.startswith("[FOLDER]"):
            self.log("[WARNING]  请选择一个文件夹（[FOLDER] 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                self.tree.move(item_id, parent, index - 1)
                self.log(f"[SUCCESS] 文件夹上移: {item_text}", "success")
            else:
                self.log("[WARNING]  文件夹已在最顶部，无法上移", "warning")
    
    def move_folder_down(self):
        """下移文件夹"""
        selection = self.tree.selection()
        if not selection:
            self.log("[WARNING]  请先选择一个文件夹", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not item_text.startswith("[FOLDER]"):
            self.log("[WARNING]  请选择一个文件夹（[FOLDER] 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                self.tree.move(item_id, parent, index + 1)
                self.log(f"[SUCCESS] 文件夹下移: {item_text}", "success")
            else:
                self.log("[WARNING]  文件夹已在最底部，无法下移", "warning")
    
    def move_file_up(self):
        """上移文件"""
        selection = self.tree.selection()
        if not selection:
            self.log("[WARNING]  请先选择一个文件", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not (item_text.startswith("[FILE]") or item_text.startswith("[DOC]")):
            self.log("[WARNING]  请选择一个文件（[FILE] 或 [DOC] 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                self.tree.move(item_id, parent, index - 1)
                self.log(f"[SUCCESS] 文件上移: {item_text}", "success")
            else:
                self.log("[WARNING]  文件已在最顶部，无法上移", "warning")
    
    def move_file_down(self):
        """下移文件"""
        selection = self.tree.selection()
        if not selection:
            self.log("[WARNING]  请先选择一个文件", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not (item_text.startswith("[FILE]") or item_text.startswith("[DOC]")):
            self.log("[WARNING]  请选择一个文件（[FILE] 或 [DOC] 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                self.tree.move(item_id, parent, index + 1)
                self.log(f"[SUCCESS] 文件下移: {item_text}", "success")
            else:
                self.log("[WARNING]  文件已在最底部，无法下移", "warning")
    
    def save_sort_config(self):
        """保存排序配置"""
        try:
            # 读取现有的排序配置
            sort_config_path = self.project_path / "sort_config.json"
            if sort_config_path.exists():
                with open(sort_config_path, 'r', encoding='utf-8') as f:
                    sort_config = json.load(f)
            else:
                sort_config = {"folders": [], "files": {}}
            
            # 清空现有配置
            sort_config["folders"] = []
            sort_config["files"] = {}
            
            # 获取所有顶级项目（文件夹）
            root_items = self.tree.get_children("")
            
            # 保存文件夹顺序
            for item_id in root_items:
                item_text = self.tree.item(item_id, "text")
                if item_text.startswith("[FOLDER]"):
                    # 提取文件夹名称（去掉图标和斜杠）
                    folder_name = item_text.replace("[OPEN] ", "").replace("/", "")
                    sort_config["folders"].append(folder_name)
                    
                    # 保存文件夹内的文件顺序
                    file_items = self.tree.get_children(item_id)
                    file_names = []
                    for file_id in file_items:
                        file_text = self.tree.item(file_id, "text")
                        if file_text.startswith("[FILE]") or file_text.startswith("[DOC]"):
                            # 提取文件名（去掉图标）
                            file_name = file_text.replace("[FILE] ", "").replace("[DOC] ", "")
                            file_names.append(file_name)
                    
                    sort_config["files"][folder_name] = file_names
            
            # 保存到文件
            with open(sort_config_path, 'w', encoding='utf-8') as f:
                json.dump(sort_config, f, indent=2, ensure_ascii=False)
            
            self.log("[SUCCESS] 排序配置已保存", "success")
            
        except Exception as e:
            self.log(f"[ERROR] 保存排序配置失败: {str(e)}", "error")
    
    def on_tree_selection(self, event):
        """树选择事件，用于启用/禁用排序按钮"""
        selection = self.tree.selection()
        if not selection:
            # 没有选择任何项目，禁用所有排序按钮
            self.btn_folder_up.config(state=tk.DISABLED)
            self.btn_folder_down.config(state=tk.DISABLED)
            self.btn_file_up.config(state=tk.DISABLED)
            self.btn_file_down.config(state=tk.DISABLED)
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        # 根据选择的项目类型启用相应的按钮
        if item_text.startswith("[FOLDER]"):
            # 选择了文件夹，启用文件夹排序按钮，禁用文件排序按钮
            self.btn_folder_up.config(state=tk.NORMAL)
            self.btn_folder_down.config(state=tk.NORMAL)
            self.btn_file_up.config(state=tk.DISABLED)
            self.btn_file_down.config(state=tk.DISABLED)
        elif item_text.startswith("[FILE]") or item_text.startswith("[DOC]"):
            # 选择了文件，启用文件排序按钮，禁用文件夹排序按钮
            self.btn_folder_up.config(state=tk.DISABLED)
            self.btn_folder_down.config(state=tk.DISABLED)
            self.btn_file_up.config(state=tk.NORMAL)
            self.btn_file_down.config(state=tk.NORMAL)
        else:
            # 其他情况，禁用所有按钮
            self.btn_folder_up.config(state=tk.DISABLED)
            self.btn_folder_down.config(state=tk.DISABLED)
            self.btn_file_up.config(state=tk.DISABLED)
            self.btn_file_down.config(state=tk.DISABLED)
    
    def on_tree_double_click(self, event):
        """树双击事件"""
        try:
            item = self.tree.selection()[0]
            item_text = self.tree.item(item, "text")
            
            # 如果是文件，尝试打开
            if item_text.startswith("[FILE]") or item_text.startswith("[DOC]"):
                # 提取文件名
                file_name = item_text.replace("[FILE] ", "").replace("[DOC] ", "")
                # 获取文件夹路径
                parent = self.tree.parent(item)
                folder_name = self.tree.item(parent, "text").replace("[OPEN] ", "").replace("/", "")
                
                # 构建完整路径
                file_path = self.docs_folder / folder_name / file_name
                
                if file_path.exists():
                    # 使用默认程序打开文件
                    os.startfile(file_path)
                    self.log(f"[OPEN] 已打开文件: {file_name}", "info")
                else:
                    self.log(f"[ERROR] 文件不存在: {file_name}", "error")
        except IndexError:
            pass  # 没有选择项目
        except Exception as e:
            self.log(f"[ERROR] 打开文件失败: {str(e)}", "error")
    
    def not_implemented(self):
        """功能未实现提示"""
        messagebox.showinfo("功能提示", "此功能在当前简单版本中暂未实现\n\n如需完整功能，请使用完整版程序")
        self.log("[WARNING]  此功能在当前版本中暂未实现", "warning")
    
    # 注意：这里省略了其他工作流方法，它们与原始版本相同
    # 为了保持简洁，只显示关键部分

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()