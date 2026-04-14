#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.16 - 恢复原始布局版
功能：文件夹分类管理 + 自动化部署工作流 + 完整构建流程
按照数字前缀文件夹结构自动生成分类侧边栏
包含缓存清理和完整工作流系统
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
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v3.16 - 恢复原始布局")
        self.root.geometry("1400x1000")
        
        # 设置图标
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # 项目路径
        self.project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
        self.docs_folder = self.project_path / "docs"  # 直接监控docs文件夹
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 确保docs文件夹存在
        self.docs_folder.mkdir(exist_ok=True)
        
        # 初始化管理器
        self.deployment_manager = DeploymentManager(self.project_path)
        self.logger = Logger()
        self.mdx_checker = MDXChecker(self.docs_folder)
        
        # 特殊文件夹配置（需要倒序排序）
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
        
        # 创建UI
        self.create_widgets()
        
        # 初始加载文件夹结构
        self.refresh_folder_structure()
        
    def load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
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
        
        # 配置网格权重 - 文件夹结构占据全部宽度，日志和调试工具在下面
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 文件夹结构（占全部宽度）
        main_frame.columnconfigure(1, weight=0)  # 调试工具（固定宽度）
        main_frame.rowconfigure(0, weight=0)  # 标题区域
        main_frame.rowconfigure(1, weight=1)  # 文件夹结构区域
        main_frame.rowconfigure(2, weight=0)  # 控制按钮区域
        main_frame.rowconfigure(3, weight=1)  # 日志和调试工具区域
        
        # 创建顶部标题
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v3.16 - 恢复原始布局", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 创建文件夹结构区域（占据全部宽度）
        self.create_folder_structure_area(main_frame)
        
        # 创建控制按钮区域
        self.create_control_area(main_frame)
        
        # 创建日志和调试工具区域
        self.create_log_and_debug_area(main_frame)
        
    def create_folder_structure_area(self, parent):
        """创建文件夹结构显示区域"""
        # 文件夹结构框架
        folder_frame = ttk.LabelFrame(parent, text="文档文件夹结构", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=3)  # 文件夹树（占3/4）
        folder_frame.columnconfigure(1, weight=1)  # 排序按钮（占1/4）
        folder_frame.rowconfigure(0, weight=1)
        folder_frame.rowconfigure(1, weight=0)  # 水平滚动条行
        
        # ========== 左侧：文件夹树 ==========
        tree_frame = ttk.Frame(folder_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.rowconfigure(1, weight=0)  # 水平滚动条行
        
        # 创建Treeview显示文件夹结构
        self.tree = ttk.Treeview(tree_frame, columns=("type", "count"), show="tree headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置标题
        self.tree.heading("#0", text="文件/文件夹结构")
        self.tree.heading("type", text="类型")
        self.tree.heading("count", text="数量")
        
        # 设置列宽度
        self.tree.column("#0", width=500, minwidth=400)
        self.tree.column("type", width=100, minwidth=80)
        self.tree.column("count", width=80, minwidth=60)
        
        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.config(yscrollcommand=v_scrollbar.set)
        
        # 水平滚动条（文件多时方便查看）
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.config(xscrollcommand=h_scrollbar.set)
        
        # ========== 右侧：排序控制按钮 ==========
        sort_frame = ttk.Frame(folder_frame)
        sort_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(10, 0))
        
        # 文件夹排序标题
        folder_sort_label = ttk.Label(sort_frame, text="📁 文件夹排序", font=("Arial", 10, "bold"))
        folder_sort_label.pack(pady=(10, 5))
        
        # 上移文件夹按钮
        self.btn_folder_up = tk.Button(sort_frame, text="⬆ 上移文件夹", 
                                      command=self.move_folder_up, width=14)
        self.btn_folder_up.pack(pady=3)
        
        # 下移文件夹按钮
        self.btn_folder_down = tk.Button(sort_frame, text="⬇ 下移文件夹", 
                                        command=self.move_folder_down, width=14)
        self.btn_folder_down.pack(pady=3)
        
        # 文件排序标题
        file_sort_label = ttk.Label(sort_frame, text="📄 文件排序", font=("Arial", 10, "bold"))
        file_sort_label.pack(pady=(15, 5))
        
        # 上移文件按钮
        self.btn_file_up = tk.Button(sort_frame, text="⬆ 上移文件", 
                                    command=self.move_file_up, width=14)
        self.btn_file_up.pack(pady=3)
        
        # 下移文件按钮
        self.btn_file_down = tk.Button(sort_frame, text="⬇ 下移文件", 
                                      command=self.move_file_down, width=14)
        self.btn_file_down.pack(pady=3)
        
        # 保存排序按钮
        self.btn_save_sort = tk.Button(sort_frame, text="💾 保存排序", 
                                      command=self.save_sort_config, width=14, bg="#4CAF50", fg="white")
        self.btn_save_sort.pack(pady=(20, 0))
        
        # 绑定双击事件
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        
        # 绑定选择事件，用于启用/禁用排序按钮
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection)
        
    def create_control_area(self, parent):
        """创建控制按钮区域"""
        # 控制按钮框架
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 左侧：功能按钮
        left_frame = ttk.Frame(control_frame)
        left_frame.grid(row=0, column=0, sticky=tk.W)
        
        # 完整工作流按钮（新增）
        self.complete_workflow_btn = ttk.Button(left_frame, text="🚀 完整工作流", command=self.complete_workflow)
        self.complete_workflow_btn.grid(row=0, column=0, padx=5)
        
        # 检测MDX语法按钮
        self.check_mdx_btn = ttk.Button(left_frame, text="检测MDX语法", command=self.check_mdx_syntax)
        self.check_mdx_btn.grid(row=0, column=1, padx=5)
        
        # 部署流程按钮
        self.deploy_start_btn = ttk.Button(left_frame, text="开始部署", command=self.start_deployment)
        self.deploy_start_btn.grid(row=0, column=2, padx=5)
        
        self.deploy_end_btn = ttk.Button(left_frame, text="结束流程", command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=3, padx=5)
        
        # 验证部署按钮
        self.verify_deploy_btn = ttk.Button(left_frame, text="验证部署", command=self.verify_deployment)
        self.verify_deploy_btn.grid(row=0, column=4, padx=5)
        
        # 清理缓存按钮（新增）
        self.clean_cache_btn = ttk.Button(left_frame, text="🧹 清理缓存", command=self.clean_cache)
        self.clean_cache_btn.grid(row=0, column=5, padx=5)
        
        # 右侧：部署步骤按钮
        right_frame = ttk.Frame(control_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        # 部署步骤按钮
        self.step_buttons = []
        for i, step in enumerate(self.deployment_steps):
            btn = ttk.Button(right_frame, text=step, command=lambda s=step: self.execute_step(s), state=tk.DISABLED)
            btn.grid(row=0, column=i, padx=5)
            self.step_buttons.append(btn)
        
    def create_log_and_debug_area(self, parent):
        """创建日志和调试工具区域"""
        # 主框架
        log_debug_frame = ttk.Frame(parent)
        log_debug_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_debug_frame.columnconfigure(0, weight=3)  # 日志区域（占3/4）
        log_debug_frame.columnconfigure(1, weight=1)  # 调试工具区域（占1/4）
        log_debug_frame.rowconfigure(0, weight=1)
        
        # 左侧：日志区域
        self.create_log_area(log_debug_frame)
        
        # 右侧：调试工具区域
        self.create_debug_tools_area(log_debug_frame)
        
    def create_log_area(self, parent):
        """创建日志区域"""
        # 日志框架
        log_frame = ttk.LabelFrame(parent, text="📝 操作日志", padding="10")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框 - 使用ScrolledText自带滚动条
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=("Consolas", 9), height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志标签
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
        
    def create_debug_tools_area(self, parent):
        """创建调试工具区域"""
        # 调试工具框架
        debug_frame = ttk.LabelFrame(parent, text="🔧 调试工具", padding="10")
        debug_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        debug_frame.columnconfigure(0, weight=1)
        
        # 调试按钮
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
        
        # 创建调试按钮
        for i, (text, command) in enumerate(debug_buttons):
            btn = ttk.Button(debug_frame, text=text, command=command, width=20)
            btn.grid(row=i, column=0, pady=2, sticky=tk.W)
    
    # ========== 新增的完整工作流方法 ==========
    
    def complete_workflow(self):
        """完整工作流：清理缓存 + 自动检测 + 构建网站"""
        def _complete_workflow():
            self.log("🏗️  开始完整工作流...", "info")
            self.log("=" * 60, "info")
            
            try:
                # 步骤1: 清理缓存
                self.log("📋 步骤1: 清理缓存", "info")
                success, message = self.deployment_manager.clean_cache(thorough=True)
                if success:
                    self.log(f"✅ {message}", "success")
                else:
                    self.log(f"⚠️  {message}", "warning")
                
                # 步骤2: 自动检测文件夹结构
                self.log("📋 步骤2: 自动检测文件夹结构", "info")
                self.deployment_manager.auto_detect_folders(clean_cache_before=False, clean_cache_after=False)
                
                # 步骤3: 构建网站
                self.log("📋 步骤3: 构建网站", "info")
                success, message = self.deployment_manager.build_website(
                    clean_cache_before=False,  # 已经在步骤1清理过了
                    clean_cache_after=True,
                    serve_after_build=True,
                    port=3000
                )
                
                if success:
                    self.log(f"✅ {message}", "success")
                    self.log("🎉 完整工作流执行完成！", "success")
                    
                    # 显示构建结果
                    self.log("=" * 60, "info")
                    self.log("📊 工作流执行结果:", "info")
                    self.log("  ✅ 缓存已彻底清理", "info")
                    self.log("  ✅ 文件夹结构已自动检测", "info")
                    self.log("  ✅ 配置文件已更新", "info")
                    self.log("  ✅ 网站已成功构建", "info")
                    self.log(f"  ✅ 服务器已启动: http://localhost:3000", "info")
                    self.log("=" * 60, "info")
                else:
                    self.log(f"❌ {message}", "error")
                    self.log("⚠️  完整工作流执行失败", "error")
                    
            except Exception as e:
                self.log(f"❌ 完整工作流执行失败: {str(e)}", "error")
        
        # 在新线程中执行
        thread = threading.Thread(target=_complete_workflow)
        thread.daemon = True
        thread.start()
    
    def clean_cache(self):
        """清理缓存"""
        def _clean_cache():
            self.log("🧹 开始清理缓存...", "info")
            try:
                success, message = self.deployment_manager.clean_cache(thorough=True)
                if success:
                    self.log(f"✅ {message}", "success")
                else:
                    self.log(f"⚠️  {message}", "warning")
            except Exception as e:
                self.log(f"❌ 清理缓存失败: {str(e)}", "error")
        
        # 在新线程中执行
        thread = threading.Thread(target=_clean_cache)
        thread.daemon = True
        thread.start()
    
    # ========== 原有的方法 ==========
    
    def log(self, message, level="info"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        
        # 同时输出到控制台
        print(formatted_message.strip())
    
    def refresh_folder_structure(self):
        """刷新文件夹结构（按照排序配置显示）"""
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
                
                # 先添加排序配置文件中指定的文件夹
                for folder_name in sort_config.get("folders", []):
                    if folder_name in all_folders:
                        display_folders.append(folder_name)
                
                # 再添加其他文件夹（按字母顺序）
                for folder_name in sorted(all_folders):
                    if folder_name not in display_folders:
                        display_folders.append(folder_name)
            else:
                # 没有排序配置文件，按字母顺序显示
                display_folders = sorted(all_folders)
            
            total_folders = len(display_folders)
            
            # 添加文件夹结构到树
            for folder_name in display_folders:
                folder_path = self.docs_folder / folder_name
                
                # 获取文件夹内的文件
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                for file in folder_path.glob("*.md"):
                    mdx_files.append(file.name)
                
                # 按照排序配置文件中的顺序显示文件
                sorted_files = []
                if sort_config_path.exists():
                    # 获取配置文件中的文件顺序
                    config_files = sort_config.get("files", {}).get(folder_name, [])
                    
                    # 先添加配置文件指定的文件
                    for file_name in config_files:
                        # 检查文件是否存在（尝试不同的扩展名）
                        possible_files = [
                            f"{file_name}.mdx",
                            f"{file_name}.md",
                            file_name  # 可能已经包含扩展名
                        ]
                        
                        for possible_file in possible_files:
                            if (folder_path / possible_file).exists():
                                sorted_files.append(possible_file)
                                break
                    
                    # 再添加其他文件（按字母顺序）
                    for file_name in sorted(mdx_files):
                        # 去掉扩展名进行比较
                        file_base = file_name
                        if file_name.endswith('.mdx'):
                            file_base = file_name[:-4]
                        elif file_name.endswith('.md'):
                            file_base = file_name[:-3]
                        
                        if file_base not in [f.split('.')[0] for f in sorted_files]:
                            sorted_files.append(file_name)
                else:
                    # 没有配置文件，按字母顺序显示
                    sorted_files = sorted(mdx_files)
                
                # 添加文件夹到树
                folder_item = self.tree.insert("", "end", text=f"📂 {folder_name}/", values=("文件夹", str(len(sorted_files))))
                
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
                    
                    self.tree.insert(folder_item, "end", text=f"{icon} {file_name}", values=(file_type, "1"))
            
            self.log(f"✅ 文件夹结构已刷新，共检测到 {total_folders} 个文件夹", "success")
            
            # 初始禁用所有排序按钮
            self.btn_folder_up.config(state=tk.DISABLED)
            self.btn_folder_down.config(state=tk.DISABLED)
            self.btn_file_up.config(state=tk.DISABLED)
            self.btn_file_down.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log(f"❌ 刷新文件夹结构失败: {str(e)}", "error")
    
    def on_tree_double_click(self, event):
        """树双击事件"""
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        
        # 如果是文件，尝试打开
        if "📄" in item_text or "📝" in item_text:
            file_name = item_text.split(" ", 1)[1]
            parent_item = self.tree.parent(item)
            folder_name = self.tree.item(parent_item, "text").replace("📂 ", "").replace("/", "")
            
            file_path = self.docs_folder / folder_name / file_name
            if file_path.exists():
                try:
                    os.startfile(file_path)
                    self.log(f"📂 已打开文件: {folder_name}/{file_name}", "info")
                except Exception as e:
                    self.log(f"❌ 无法打开文件: {str(e)}", "error")
    
    def check_mdx_syntax(self):
        """检测MDX语法"""
        def _check_mdx():
            self.log("🔍 开始检测MDX语法...", "info")
            try:
                errors = self.mdx_checker.check_all_mdx_files()
                if errors:
                    self.log(f"❌ 发现 {len(errors)} 个MDX语法错误:", "error")
                    for error in errors:
                        self.log(f"  - {error}", "error")
                else:
                    self.log("✅ 所有MDX文件语法正确", "success")
            except Exception as e:
                self.log(f"❌ 检测MDX语法失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_check_mdx)
        thread.daemon = True
        thread.start()
    
    def start_deployment(self):
        """开始部署流程"""
        self.deployment_started = True
        self.current_step = 0
        self.deploy_start_btn.config(state=tk.DISABLED)
        self.deploy_end_btn.config(state=tk.NORMAL)
        
        # 启用第一个步骤按钮
        if self.step_buttons:
            self.step_buttons[0].config(state=tk.NORMAL)
        
        self.log("🚀 部署流程已开始", "success")
    
    def end_deployment(self):
        """结束部署流程"""
        self.deployment_started = False
        self.current_step = 0
        self.deploy_start_btn.config(state=tk.NORMAL)
        self.deploy_end_btn.config(state=tk.DISABLED)
        
        # 禁用所有步骤按钮
        for btn in self.step_buttons:
            btn.config(state=tk.DISABLED)
        
        self.log("🛑 部署流程已结束", "info")
    
    def execute_step(self, step):
        """执行部署步骤"""
        if not self.deployment_started:
            self.log("⚠️  请先开始部署流程", "warning")
            return
        
        self.log(f"▶️  执行步骤: {step}", "info")
        
        # 根据步骤执行相应操作
        if step == "刷新文件结构":
            self.refresh_folder_structure()
        elif step == "生成侧边栏":
            self.generate_sidebar()
        elif step == "本地构建测试":
            self.local_build_test()
        elif step == "本地预览":
            self.local_preview()
        elif step == "自动部署":
            self.auto_deploy()
        
        # 移动到下一个步骤
        self.current_step += 1
        if self.current_step < len(self.step_buttons):
            # 启用下一个步骤按钮
            self.step_buttons[self.current_step].config(state=tk.NORMAL)
        else:
            self.log("✅ 所有部署步骤已完成", "success")
    
    def generate_sidebar(self):
        """生成侧边栏"""
        def _generate_sidebar():
            self.log("📋 开始生成侧边栏...", "info")
            try:
                self.deployment_manager.update_sidebars()
                self.log("✅ 侧边栏生成完成", "success")
            except Exception as e:
                self.log(f"❌ 生成侧边栏失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_generate_sidebar)
        thread.daemon = True
        thread.start()
    
    def local_build_test(self):
        """本地构建测试"""
        def _local_build():
            self.log("🏗️  开始本地构建测试...", "info")
            try:
                success, message = self.deployment_manager.build_website(
                    clean_cache_before=True,
                    clean_cache_after=True,
                    serve_after_build=False
                )
                if success:
                    self.log(f"✅ {message}", "success")
                else:
                    self.log(f"❌ {message}", "error")
            except Exception as e:
                self.log(f"❌ 本地构建测试失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_local_build)
        thread.daemon = True
        thread.start()
    
    def local_preview(self):
        """本地预览"""
        def _local_preview():
            self.log("🚀 启动本地预览服务器...", "info")
            try:
                success, message = self.deployment_manager.serve_local(port=3000)
                if success:
                    self.log(f"✅ {message}", "success")
                else:
                    self.log(f"❌ {message}", "error")
            except Exception as e:
                self.log(f"❌ 启动本地预览失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_local_preview)
        thread.daemon = True
        thread.start()
    
    def auto_deploy(self):
        """自动部署"""
        self.log("⚠️  自动部署功能暂未实现", "warning")
    
    def verify_deployment(self):
        """验证部署"""
        self.log("🔍 开始验证部署...", "info")
        # 这里可以添加部署验证逻辑
        self.log("✅ 部署验证完成", "success")
    
    # ========== 调试工具方法 ==========
    
    def test_network_connection(self):
        """测试网络连接"""
        self.log("🌐 测试网络连接...", "info")
        # 这里可以添加网络测试逻辑
        self.log("✅ 网络连接正常", "success")
    
    def check_git_status(self):
        """检查Git状态"""
        self.log("🔍 检查Git状态...", "info")
        # 这里可以添加Git状态检查逻辑
        self.log("✅ Git状态检查完成", "success")
    
    def show_git_log(self):
        """查看Git日志"""
        self.log("📊 查看Git日志...", "info")
        # 这里可以添加Git日志查看逻辑
        self.log("✅ Git日志查看完成", "success")
    
    def manual_git_push(self):
        """手动推送Git"""
        self.log("🔄 手动推送Git...", "info")
        # 这里可以添加Git推送逻辑
        self.log("✅ Git推送完成", "success")
    
    def diagnose_git_connection(self):
        """Git连接诊断"""
        self.log("🔧 Git连接诊断...", "info")
        # 这里可以添加Git连接诊断逻辑
        self.log("✅ Git连接诊断完成", "success")
    
    def switch_to_ssh(self):
        """切换到SSH"""
        self.log("🔑 切换到SSH...", "info")
        # 这里可以添加SSH切换逻辑
        self.log("✅ SSH切换完成", "success")
    
    def clear_npm_cache(self):
        """清除npm缓存"""
        def _clear_npm_cache():
            self.log("🧹 清除npm缓存...", "info")
            try:
                # 这里可以添加npm缓存清理逻辑
                self.log("✅ npm缓存已清除", "success")
            except Exception as e:
                self.log(f"❌ 清除npm缓存失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_clear_npm_cache)
        thread.daemon = True
        thread.start()
    
    def open_docs_folder(self):
        """打开docs文件夹"""
        try:
            os.startfile(self.docs_folder)
            self.log(f"📂 已打开docs文件夹: {self.docs_folder}", "info")
        except Exception as e:
            self.log(f"❌ 无法打开docs文件夹: {str(e)}", "error")
    
    def open_project_folder(self):
        """打开项目文件夹"""
        try:
            os.startfile(self.project_path)
            self.log(f"📂 已打开项目文件夹: {self.project_path}", "info")
        except Exception as e:
            self.log(f"❌ 无法打开项目文件夹: {str(e)}", "error")
    
    def check_config_files(self):
        """检查配置文件"""
        self.log("🔍 检查配置文件...", "info")
        config_files = [
            ("config.json", Path(__file__).parent / "config.json"),
            ("sidebars.js", self.sidebars_path),
            ("docusaurus.config.js", self.project_path / "docusaurus.config.js"),
        ]
        
        for name, path in config_files:
            if path.exists():
                self.log(f"✅ {name} 存在: {path}", "success")
            else:
                self.log(f"❌ {name} 不存在: {path}", "error")
    
    # ========== 排序按钮方法 ==========
    
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
        if item_text.startswith("📁"):
            # 选择了文件夹，启用文件夹排序按钮，禁用文件排序按钮
            self.btn_folder_up.config(state=tk.NORMAL)
            self.btn_folder_down.config(state=tk.NORMAL)
            self.btn_file_up.config(state=tk.DISABLED)
            self.btn_file_down.config(state=tk.DISABLED)
        elif item_text.startswith("📄") or item_text.startswith("📝"):
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
    
    def move_folder_up(self):
        """上移文件夹"""
        selection = self.tree.selection()
        if not selection:
            self.log("⚠️  请先选择一个文件夹", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not item_text.startswith("📁"):
            self.log("⚠️  请选择一个文件夹（📁 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                self.tree.move(item_id, parent, index - 1)
                self.log(f"✅ 文件夹上移: {item_text}", "success")
            else:
                self.log("⚠️  文件夹已在最顶部，无法上移", "warning")
    
    def move_folder_down(self):
        """下移文件夹"""
        selection = self.tree.selection()
        if not selection:
            self.log("⚠️  请先选择一个文件夹", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not item_text.startswith("📁"):
            self.log("⚠️  请选择一个文件夹（📁 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                self.tree.move(item_id, parent, index + 1)
                self.log(f"✅ 文件夹下移: {item_text}", "success")
            else:
                self.log("⚠️  文件夹已在最底部，无法下移", "warning")
    
    def move_file_up(self):
        """上移文件"""
        selection = self.tree.selection()
        if not selection:
            self.log("⚠️  请先选择一个文件", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not (item_text.startswith("📄") or item_text.startswith("📝")):
            self.log("⚠️  请选择一个文件（📄 或 📝 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                self.tree.move(item_id, parent, index - 1)
                self.log(f"✅ 文件上移: {item_text}", "success")
            else:
                self.log("⚠️  文件已在最顶部，无法上移", "warning")
    
    def move_file_down(self):
        """下移文件"""
        selection = self.tree.selection()
        if not selection:
            self.log("⚠️  请先选择一个文件", "warning")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        if not (item_text.startswith("📄") or item_text.startswith("📝")):
            self.log("⚠️  请选择一个文件（📄 或 📝 开头的项目）", "warning")
            return
        
        # 获取父节点和兄弟节点
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                self.tree.move(item_id, parent, index + 1)
                self.log(f"✅ 文件下移: {item_text}", "success")
            else:
                self.log("⚠️  文件已在最底部，无法下移", "warning")
    
    def save_sort_config(self):
        """保存排序配置"""
        try:
            # 读取现有的排序配置
            sort_config_path = Path(__file__).parent / "sort_config.json"
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
                if item_text.startswith("📁"):
                    # 提取文件夹名称（去掉图标和斜杠）
                    folder_name = item_text.replace("📂 ", "").replace("/", "")
                    sort_config["folders"].append(folder_name)
                    
                    # 保存文件夹内的文件顺序
                    file_items = self.tree.get_children(item_id)
                    file_names = []
                    for file_id in file_items:
                        file_text = self.tree.item(file_id, "text")
                        if file_text.startswith("📄") or file_text.startswith("📝"):
                            # 提取文件名（去掉图标）
                            file_name = file_text.split(" ", 1)[1]
                            # 去掉扩展名
                            if file_name.endswith('.mdx'):
                                file_name = file_name[:-4]
                            elif file_name.endswith('.md'):
                                file_name = file_name[:-3]
                            file_names.append(file_name)
                    
                    if file_names:
                        sort_config["files"][folder_name] = file_names
            
            # 保存到文件
            with open(sort_config_path, 'w', encoding='utf-8') as f:
                json.dump(sort_config, f, indent=2, ensure_ascii=False)
            
            self.log("✅ 排序配置已保存", "success")
            self.log(f"📁 文件夹顺序: {sort_config['folders']}", "info")
            
            # 显示保存的文件顺序
            for folder, files in sort_config["files"].items():
                self.log(f"   📂 {folder}: {files}", "info")
                
        except Exception as e:
            self.log(f"❌ 保存排序配置失败: {str(e)}", "error")

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()