#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v2.7 - 纯中文文档管理
功能：文件夹分类管理 + 自动化部署工作流
按照数字前缀文件夹结构自动生成分类侧边栏
移除英文支持，专注于中文文档管理
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
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v2.7 - 纯中文文档管理")
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
        
        # 中英文名称映射
        self.chinese_to_english = {
            # 文件夹映射
            "主程序安装": "main-program-installation",
            "云更新服务": "cloud-update-service", 
            "补丁日志": "patch-log",
            # 文件映射
            "主程序安装说明.mdx": "main-program-installation-guide.mdx",
            "云更新服务注册说明.mdx": "cloud-update-service-registration-guide.mdx",
            "注册规则特殊说明.mdx": "special-registration-rules.mdx",
            "NEW-26040101.mdx": "patch-new-26040101.mdx",
            "NEW-26040902.mdx": "patch-new-26040902.mdx"
        }
        
        # 反向映射（英文到中文）
        self.english_to_chinese = {v: k for k, v in self.chinese_to_english.items()}
        
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
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v2.3 - 新增排序控制功能", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 创建文件夹结构区域（占据全部宽度）
        self.create_folder_structure_area(main_frame)
        
        # 创建控制按钮区域
        self.create_control_area(main_frame)
        
        # 创建日志和调试工具区域
        self.create_log_and_debug_area(main_frame)
        
    def create_folder_structure_area(self, parent):
        """创建中英文文件夹结构显示区域"""
        # 主框架
        main_folder_frame = ttk.LabelFrame(parent, text="中英文文档结构管理", padding="10")
        main_folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 配置网格布局：左中文 | 中控制 | 右英文
        main_folder_frame.columnconfigure(0, weight=1)  # 中文Treeview
        main_folder_frame.columnconfigure(1, weight=0)  # 控制面板
        main_folder_frame.columnconfigure(2, weight=1)  # 英文Treeview
        main_folder_frame.rowconfigure(0, weight=1)
        
        # ========== 左侧：中文文档树 ==========
        chinese_frame = ttk.Frame(main_folder_frame)
        chinese_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        chinese_frame.columnconfigure(0, weight=1)
        chinese_frame.rowconfigure(0, weight=1)
        
        ttk.Label(chinese_frame, text="📚 中文文档", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.tree_chinese = ttk.Treeview(chinese_frame, show="tree")
        self.tree_chinese.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_chinese.heading("#0", text="文件/文件夹结构")
        self.tree_chinese.column("#0", width=300, minwidth=200)
        
        # 中文滚动条
        chinese_v_scroll = ttk.Scrollbar(chinese_frame, orient=tk.VERTICAL, command=self.tree_chinese.yview)
        chinese_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_chinese.config(yscrollcommand=chinese_v_scroll.set)
        
        # ========== 中间：控制面板 ==========
        control_frame = ttk.Frame(main_folder_frame)
        control_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10)
        
        # 文件夹排序按钮
        ttk.Label(control_frame, text="📁 文件夹排序", font=("Arial", 9, "bold")).pack(pady=(10, 5))
        
        self.btn_folder_up = tk.Button(control_frame, text="⬆ 上移文件夹", 
                                      command=self.move_folder_up_both, width=14)
        self.btn_folder_up.pack(pady=3)
        
        self.btn_folder_down = tk.Button(control_frame, text="⬇ 下移文件夹", 
                                        command=self.move_folder_down_both, width=14)
        self.btn_folder_down.pack(pady=3)
        
        # 文件排序按钮
        ttk.Label(control_frame, text="📄 文件排序", font=("Arial", 9, "bold")).pack(pady=(15, 5))
        
        self.btn_file_up = tk.Button(control_frame, text="⬆ 上移文件", 
                                    command=self.move_file_up_both, width=14)
        self.btn_file_up.pack(pady=3)
        
        self.btn_file_down = tk.Button(control_frame, text="⬇ 下移文件", 
                                      command=self.move_file_down_both, width=14)
        self.btn_file_down.pack(pady=3)
        
        # 同步按钮
        ttk.Label(control_frame, text="🔄 同步操作", font=("Arial", 9, "bold")).pack(pady=(20, 5))
        
        self.btn_sync_chinese_to_english = tk.Button(control_frame, text="📥 中→英同步", 
                                                   command=self.sync_chinese_to_english, width=14)
        self.btn_sync_chinese_to_english.pack(pady=3)
        
        self.btn_sync_english_to_chinese = tk.Button(control_frame, text="📤 英→中同步", 
                                                   command=self.sync_english_to_chinese, width=14)
        self.btn_sync_english_to_chinese.pack(pady=3)
        
        # 保存按钮
        self.btn_save_both = tk.Button(control_frame, text="💾 保存双排序", 
                                      command=self.save_both_sort_config, width=14, bg="#4CAF50", fg="white")
        self.btn_save_both.pack(pady=(20, 0))
        
        # ========== 右侧：英文文档树 ==========
        english_frame = ttk.Frame(main_folder_frame)
        english_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        english_frame.columnconfigure(0, weight=1)
        english_frame.rowconfigure(0, weight=1)
        
        ttk.Label(english_frame, text="🌐 英文文档", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.tree_english = ttk.Treeview(english_frame, show="tree")
        self.tree_english.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_english.heading("#0", text="File/Folder Structure")
        self.tree_english.column("#0", width=300, minwidth=200)
        
        # 英文滚动条
        english_v_scroll = ttk.Scrollbar(english_frame, orient=tk.VERTICAL, command=self.tree_english.yview)
        english_v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_english.config(yscrollcommand=english_v_scroll.set)
        
        # 绑定选择事件
        self.tree_chinese.bind('<<TreeviewSelect>>', self.on_chinese_tree_selection)
        self.tree_english.bind('<<TreeviewSelect>>', self.on_english_tree_selection)
        
        # 初始化时禁用所有按钮
        self.update_button_states()
        
        # 绑定双击事件
        self.tree_chinese.bind('<Double-Button-1>', self.on_tree_double_click)
        self.tree_english.bind('<Double-Button-1>', self.on_tree_double_click)
        
    def create_control_area(self, parent):
        """创建控制按钮区域 - 完全按照13:42时的布局"""
        # 控制框架
        control_frame = ttk.LabelFrame(parent, text="文档管理控制", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 第一行：主要功能按钮
        top_frame = ttk.Frame(control_frame)
        top_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 检测语法按钮
        self.btn_check_mdx = tk.Button(top_frame, text="🔍 检测MDX语法", 
                                      command=self.check_mdx_syntax, width=20,
                                      bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_check_mdx.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(control_frame, orient='horizontal').grid(row=1, column=0, columnspan=4, 
                                                              sticky=(tk.W, tk.E), pady=10)
        
        # 第二行：部署流程控制按钮
        deploy_control_frame = ttk.Frame(control_frame)
        deploy_control_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 开始部署流程按钮
        self.btn_start_deploy = tk.Button(deploy_control_frame, text="🚀 开始部署流程", 
                                         command=self.start_deployment, width=20,
                                         bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_start_deploy.pack(side=tk.LEFT, padx=5)
        
        # 结束流程按钮
        self.btn_end_deploy = tk.Button(deploy_control_frame, text="⏹️ 结束流程", 
                                       command=self.end_deployment, width=20, state="disabled",
                                       bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_end_deploy.pack(side=tk.LEFT, padx=5)
        
        # 验证部署按钮（独立，一直可用）
        self.btn_verify_deploy = tk.Button(deploy_control_frame, text="🌐 验证部署", 
                                          command=self.verify_deployment, width=20,
                                          bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_verify_deploy.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, columnspan=4, 
                                                              sticky=(tk.W, tk.E), pady=10)
        
        # 第三行：部署步骤按钮（默认禁用）
        deploy_steps_frame = ttk.Frame(control_frame)
        deploy_steps_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # 部署流程标签
        steps_label = ttk.Label(deploy_steps_frame, text="部署步骤：", font=("Arial", 10, "bold"))
        steps_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # 部署步骤按钮
        self.step_buttons = []
        for i, step in enumerate(self.deployment_steps):
            btn = tk.Button(deploy_steps_frame, text=step, 
                           command=lambda s=step: self.execute_step(s), 
                           width=15, state="disabled",
                           bg="SystemButtonFace", fg="black", relief="raised", bd=2)
            btn.grid(row=0, column=i+1, padx=5)
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
            ("⚙️ 检查配置", self.check_config),
        ]
        
        for i, (text, command) in enumerate(debug_buttons):
            btn = tk.Button(
                debug_frame,
                text=text,
                command=command,
                bg="SystemButtonFace",
                fg="black",
                width=20,
                relief="raised",
                bd=2
            )
            btn.grid(row=i, column=0, pady=5, sticky="ew")
            
    def log_message(self, message, level="info"):
        """记录日志消息"""
        if self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"
            
            self.log_text.insert(tk.END, log_line, level)
            self.log_text.see(tk.END)
            self.log_text.update()
    
    def refresh_folder_structure(self):
        """刷新中英文文件夹结构显示"""
        try:
            # 清空中文树
            for item in self.tree_chinese.get_children():
                self.tree_chinese.delete(item)
            
            # 清空英文树
            for item in self.tree_english.get_children():
                self.tree_english.delete(item)
            
            # 读取排序配置文件
            import json
            sort_config_path = Path(__file__).parent / "sort_config.json"
            sort_config = {"folders": [], "files": {}}
            
            if sort_config_path.exists():
                with open(sort_config_path, 'r', encoding='utf-8') as f:
                    sort_config = json.load(f)
            
            total_folders = 0
            total_files = 0
            
            # ========== 刷新中文文档树 ==========
            self.tree_chinese.insert("", 0, text="📂 docs文件夹 (中文)", open=True)
            
            # 获取所有中文文件夹
            all_folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    all_folders.append(item.name)
            
            # 按照排序配置文件的顺序显示文件夹
            display_folders = []
            for folder_name in sort_config.get("folders", []):
                if folder_name in all_folders:
                    display_folders.append(folder_name)
            
            for folder_name in sorted(all_folders):
                if folder_name not in display_folders:
                    display_folders.append(folder_name)
            
            # 保存每个文件夹的文件列表（用于英文树刷新）
            folder_files_map = {}
            
            # 添加每个文件夹到中文Treeview
            for folder_name in display_folders:
                total_folders += 1
                folder_path = self.docs_folder / folder_name
                folder_id = self.tree_chinese.insert("", tk.END, text=f"📁 {folder_name}", open=True)
                
                # 获取文件夹内的MDX文件
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                
                # 按照配置文件中的文件顺序
                sorted_files = []
                config_files = sort_config.get("files", {}).get(folder_name, [])
                
                for config_file in config_files:
                    config_file_with_ext = f"{config_file}.mdx"
                    if config_file_with_ext in mdx_files:
                        sorted_files.append(config_file_with_ext)
                
                for file_name in sorted(mdx_files):
                    if file_name not in sorted_files:
                        sorted_files.append(file_name)
                
                # 保存到映射表
                folder_files_map[folder_name] = sorted_files
                
                # 添加文件节点
                for file_name in sorted_files:
                    total_files += 1
                    self.tree_chinese.insert(folder_id, tk.END, text=f"📄 {file_name}")
            
            # ========== 刷新英文文档树 ==========
            # 英文文档路径 - 使用绝对路径避免相对路径问题
            try:
                # 方法1：使用项目路径（更可靠）
                english_docs_path = self.project_path / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
                
                # 调试信息
                debug_info = f"英文路径检查: {english_docs_path}"
                print(f"[DEBUG] {debug_info}")  # 控制台输出
                
                if english_docs_path.exists():
                    self.log_message(f"英文目录存在: {english_docs_path}", "info")
                    self.tree_english.insert("", 0, text="📂 docs文件夹 (英文)", open=True)
                    
                    # 获取所有英文文件夹（使用映射关系）
                    for folder_name in display_folders:
                        # 获取对应的英文文件夹名
                        english_folder_name = self.chinese_to_english.get(folder_name, folder_name)
                        folder_english_path = english_docs_path / english_folder_name
                        
                        if folder_english_path.exists():
                            folder_id = self.tree_english.insert("", tk.END, text=f"📁 {english_folder_name}", open=True)
                            
                            # 获取英文文件夹内的MDX文件
                            english_mdx_files = []
                            for file in folder_english_path.glob("*.mdx"):
                                english_mdx_files.append(file.name)
                            
                            # 获取该文件夹对应的文件列表
                            folder_sorted_files = folder_files_map.get(folder_name, [])
                            
                            # 按照相同的顺序添加文件
                            for file_name in folder_sorted_files:
                                # 查找对应的英文文件名
                                english_file_name = self.chinese_to_english.get(file_name, file_name)
                                if english_file_name in english_mdx_files:
                                    self.tree_english.insert(folder_id, tk.END, text=f"📄 {english_file_name}")
                                else:
                                    # 如果英文文件不存在，显示占位符
                                    self.tree_english.insert(folder_id, tk.END, text=f"❓ {file_name} (未翻译)")
                        else:
                            # 如果英文文件夹不存在，显示占位符
                            folder_id = self.tree_english.insert("", tk.END, text=f"⚠️ {english_folder_name} (文件夹未创建)", open=True)
                            self.log_message(f"英文文件夹不存在: {english_folder_name}", "warning")
                else:
                    self.tree_english.insert("", 0, text="⚠️ 英文文档目录不存在", open=True)
                    self.log_message("警告：英文文档目录不存在，请先创建英文文档", "warning")
                    # 详细调试信息
                    self.log_message(f"路径检查失败: {english_docs_path}", "debug")
                    
            except Exception as e:
                self.log_message(f"刷新英文树时出错: {str(e)}", "error")
                self.tree_english.insert("", 0, text="⚠️ 英文文档检查出错", open=True)
            
            self.log_message(f"中英文文件夹结构已刷新，共{total_folders}个分类，{total_files}个MDX文件", "success")
            
        except Exception as e:
            self.log_message(f"刷新文件夹结构失败: {str(e)}", "error")
    
    def clean_name(self, name):
        """清理名称"""
        if name.endswith('.mdx'):
            name = name[:-4]
        
        import re
        name = re.sub(r'^\d+\-', '', name)
        
        return name
    
    def on_tree_double_click(self, event):
        """树形结构双击事件"""
        # 确定是哪个树被双击
        widget = event.widget
        
        if widget == self.tree_chinese:
            tree = self.tree_chinese
            base_path = self.docs_folder
        elif widget == self.tree_english:
            tree = self.tree_english
            base_path = Path(__file__).parent.parent / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
        else:
            return
        
        selection = tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = tree.item(item, "text")
        
        # 检查是否是文件
        if item_text.startswith("📄"):
            # 获取文件路径
            file_name = item_text[2:]  # 去掉"📄 "前缀
            folder_name = tree.item(tree.parent(item), "text")[2:]  # 去掉"📁 "前缀
            
            file_path = base_path / folder_name / file_name
            
            if file_path.exists():
                try:
                    os.startfile(file_path)
                    self.log_message(f"已打开文件: {file_path}", "info")
                except Exception as e:
                    self.log_message(f"打开文件失败: {str(e)}", "error")
            else:
                self.log_message(f"文件不存在: {file_path}", "error")
    
    def check_mdx_syntax(self):
        """检测MDX语法"""
        self.log_message("开始检测MDX语法...")
        
        try:
            success_count = 0
            error_count = 0
            
            # 遍历所有文件夹
            for folder in self.docs_folder.iterdir():
                if folder.is_dir():
                    # 遍历文件夹内的MDX文件
                    for file in folder.glob("*.mdx"):
                        result = self.mdx_checker.check_single_file(file)
                        # 注意：check_single_file返回问题列表，空列表表示没有错误
                        if not result:  # 如果没有问题（空列表）
                            self.log_message(f"  ✓ {folder.name}\\{file.name}", "success")
                            success_count += 1
                        else:  # 如果有问题（非空列表）
                            self.log_message(f"  ✗ {folder.name}\\{file.name}", "error")
                            error_count += 1
            
            self.log_message("=" * 60)
            self.log_message(f"MDX语法检测完成:")
            self.log_message(f"  总文件数: {success_count + error_count}")
            self.log_message(f"  错误文件: {error_count}")
            
            if error_count == 0:
                self.log_message("所有MDX文件语法正确！", "success")
            else:
                self.log_message(f"发现{error_count}个错误文件，请检查", "error")
                
        except Exception as e:
            self.log_message(f"检测MDX语法失败: {str(e)}", "error")
    
    def start_deployment(self):
        """开始部署流程"""
        self.deployment_started = True
        self.current_step = 0
        self.btn_start_deploy.config(state="disabled")
        self.btn_end_deploy.config(state="normal")
        
        # 启用第一个步骤按钮
        if self.step_buttons:
            self.step_buttons[0].config(state="normal")
        
        self.log_message("部署流程已开始，请按顺序执行步骤")
        self.log_message("步骤1: 刷新文件结构 → 步骤2: 生成侧边栏 → 步骤3: 本地构建测试 → 步骤4: 本地预览 → 步骤5: 自动部署")
    
    def end_deployment(self):
        """结束部署流程"""
        self.deployment_started = False
        self.current_step = 0
        self.btn_start_deploy.config(state="normal")
        self.btn_end_deploy.config(state="disabled")
        
        # 禁用所有步骤按钮
        for btn in self.step_buttons:
            btn.config(state="disabled")
        
        self.log_message("部署流程已结束", "success")
    
    def execute_step(self, step_name):
        """执行部署步骤"""
        if not self.deployment_started:
            return
        
        # 更新按钮状态
        step_index = self.deployment_steps.index(step_name)
        if step_index != self.current_step:
            self.log_message(f"请按顺序执行步骤，当前应执行: {self.deployment_steps[self.current_step]}", "warning")
            return
        
        # 执行步骤
        if step_name == "刷新文件结构":
            self.refresh_folder_structure_thread()
        elif step_name == "生成侧边栏":
            self.generate_sidebar_thread()
        elif step_name == "本地构建测试":
            self.local_build_test_thread()
        elif step_name == "本地预览":
            self.local_preview_thread()
        elif step_name == "自动部署":
            self.auto_deploy_thread()
        
        # 更新当前步骤
        self.current_step += 1
        
        # 启用下一个步骤按钮
        if self.current_step < len(self.step_buttons):
            self.step_buttons[self.current_step].config(state="normal")
    
    def refresh_folder_structure_thread(self):
        """刷新文件夹结构线程"""
        thread = threading.Thread(target=self.refresh_folder_structure)
        thread.daemon = True
        thread.start()
    
    def generate_sidebar_thread(self):
        """生成侧边栏线程"""
        thread = threading.Thread(target=self.generate_sidebar)
        thread.daemon = True
        thread.start()
    
    def generate_sidebar(self):
        """生成侧边栏"""
        self.log_message("开始生成侧边栏...")
        
        try:
            sidebar_content = self.deployment_manager.generate_sidebar_content()
            
            # 保存到文件
            with open(self.sidebars_path, 'w', encoding='utf-8') as f:
                f.write(sidebar_content)
            
            self.log_message(f"侧边栏生成成功！", "success")
            self.log_message(f"文件已保存: {self.sidebars_path}")
            
            # 显示生成的侧边栏结构
            self.log_message("生成的侧边栏结构:")
            self.log_message("-" * 40)
            for line in sidebar_content.split('\n'):
                if line.strip():
                    self.log_message(f"  {line}")
            self.log_message("-" * 40)
            
            self.log_message("侧边栏已成功生成并保存！", "success")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("生成侧边栏")
                self.step_buttons[step_index].config(state="disabled")
                self.log_message(f"已解锁步骤 {self.current_step + 1}: {self.deployment_steps[self.current_step]}")
                
        except Exception as e:
            self.log_message(f"生成侧边栏失败: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("生成侧边栏")
                self.step_buttons[step_index].config(state="normal")
    
    def local_build_test_thread(self):
        """本地构建测试线程"""
        thread = threading.Thread(target=self.local_build_test)
        thread.daemon = True
        thread.start()
    
    def local_build_test(self):
        """本地构建测试"""
        self.log_message("开始本地构建测试...")
        
        try:
            success, output = self.deployment_manager.local_build_test()
            if success:
                self.log_message("本地构建测试成功！", "success")
                self.log_message("本地构建测试成功，可以继续下一步")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    step_index = self.deployment_steps.index("本地构建测试")
                    self.step_buttons[step_index].config(state="disabled")
                    self.log_message(f"已解锁步骤 {self.current_step + 1}: {self.deployment_steps[self.current_step]}")
            else:
                self.log_message("本地构建测试失败", "error")
                self.log_message("本地构建测试失败，请查看日志", "error")
                
                # 显示详细错误信息
                for line in output.split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    step_index = self.deployment_steps.index("本地构建测试")
                    self.step_buttons[step_index].config(state="normal")
                    
        except Exception as e:
            self.log_message(f"本地构建测试异常: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("本地构建测试")
                self.step_buttons[step_index].config(state="normal")
    
    def local_preview_thread(self):
        """本地预览线程"""
        thread = threading.Thread(target=self.local_preview)
        thread.daemon = True
        thread.start()
    
    def local_preview(self):
        """本地预览"""
        self.log_message("开始本地预览...")
        
        try:
            success, output = self.deployment_manager.local_preview()
            if success:
                self.log_message("本地预览服务器已启动！", "success")
                self.log_message("本地预览服务器已启动，请在浏览器中查看")
                
                # 延迟后自动打开浏览器
                self.log_message("服务器已启动，3秒后自动打开浏览器...")
                self.root.after(3000, self.open_local_preview)
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    step_index = self.deployment_steps.index("本地预览")
                    self.step_buttons[step_index].config(state="disabled")
                    self.log_message(f"已解锁步骤 {self.current_step + 1}: {self.deployment_steps[self.current_step]}")
            else:
                self.log_message("启动本地预览失败", "error")
                self.log_message("启动本地预览失败，请查看日志", "error")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    step_index = self.deployment_steps.index("本地预览")
                    self.step_buttons[step_index].config(state="normal")
                    
        except Exception as e:
            self.log_message(f"启动本地预览异常: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("本地预览")
                self.step_buttons[step_index].config(state="normal")
    
    def open_local_preview(self):
        """自动打开本地预览页面"""
        try:
            import webbrowser
            import time
            
            # 等待服务器完全启动
            self.log_message("等待服务器完全启动...")
            time.sleep(5)
            
            # 打开网站首页
            url = "http://localhost:3000"
            
            # 同时显示可用的文档链接
            self.log_message("已打开网站首页，可用文档链接:")
            
            # 从侧边栏中获取所有文档链接
            if self.sidebars_path.exists():
                try:
                    with open(self.sidebars_path, 'r', encoding='utf-8') as f:
                        sidebar_content = f.read()
                    
                    # 提取所有文档ID
                    import re
                    doc_ids = re.findall(r"'([^']+/[^']+)'", sidebar_content)
                    
                    if doc_ids:
                        for doc_id in doc_ids:
                            doc_url = f"http://localhost:3000/docs/{doc_id}"
                            self.log_message(f"  • {doc_id}: {doc_url}")
                        
                        # 同时自动打开第一个文档
                        first_doc_id = doc_ids[0]
                        first_doc_url = f"http://localhost:3000/docs/{first_doc_id}"
                        self.log_message(f"同时打开第一个文档: {first_doc_url}")
                        webbrowser.open(first_doc_url)
                    else:
                        self.log_message("  • 未找到文档链接")
                        webbrowser.open(url)
                except Exception as e:
                    self.log_message(f"  • 读取侧边栏失败: {str(e)}")
                    webbrowser.open(url)
            else:
                self.log_message("  • 侧边栏文件不存在")
                webbrowser.open(url)
            
            self.log_message(f"已自动打开浏览器访问: {url}", "success")
            
        except Exception as e:
            self.log_message(f"自动打开浏览器失败: {str(e)}", "error")
            self.log_message("请手动访问: http://localhost:3000")
    
    def auto_deploy_thread(self):
        """自动部署线程"""
        thread = threading.Thread(target=self.auto_deploy)
        thread.daemon = True
        thread.start()
    
    def auto_deploy(self):
        """自动部署"""
        self.log_message("开始自动部署...")
        
        try:
            success, output = self.deployment_manager.auto_deploy()
            if success:
                self.log_message("自动部署成功！", "success")
                self.log_message("网站已成功部署到GitHub Pages")
                
                # 如果是在部署流程中，更新按钮状态并结束流程
                if self.deployment_started:
                    step_index = self.deployment_steps.index("自动部署")
                    self.step_buttons[step_index].config(state="disabled")
                    self.end_deployment()
            else:
                self.log_message("自动部署失败", "error")
                self.log_message("自动部署失败，请查看日志", "error")
                
                # 显示详细错误信息
                for line in output.split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    step_index = self.deployment_steps.index("自动部署")
                    self.step_buttons[step_index].config(state="normal")
                    
        except Exception as e:
            self.log_message(f"自动部署异常: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("自动部署")
                self.step_buttons[step_index].config(state="normal")
    
    def verify_deployment(self):
        """验证部署"""
        self.log_message("开始验证部署...")
        
        try:
            import webbrowser
            webbrowser.open("https://docs.toothmen.com")
            self.log_message("已打开部署网站: https://docs.toothmen.com", "success")
            
        except Exception as e:
            self.log_message(f"验证部署失败: {str(e)}", "error")
    
    # 调试工具方法
    def test_network_connection(self):
        """测试网络连接"""
        self.log_message("测试网络连接...")
        try:
            import urllib.request
            urllib.request.urlopen("https://www.google.com", timeout=5)
            self.log_message("网络连接正常", "success")
        except Exception as e:
            self.log_message(f"网络连接失败: {str(e)}", "error")
    
    def check_git_status(self):
        """检查Git状态"""
        self.log_message("检查Git状态...")
        try:
            result = subprocess.run([self.config["git_path"], "status"], 
                                  cwd=self.project_path, capture_output=True, text=True)
            self.log_message("Git状态:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log_message(f"  {line}")
        except Exception as e:
            self.log_message(f"检查Git状态失败: {str(e)}", "error")
    
    def show_git_log(self):
        """查看Git日志"""
        self.log_message("查看Git日志...")
        try:
            result = subprocess.run([self.config["git_path"], "log", "--oneline", "-10"], 
                                  cwd=self.project_path, capture_output=True, text=True)
            self.log_message("最近10次提交:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log_message(f"  {line}")
        except Exception as e:
            self.log_message(f"查看Git日志失败: {str(e)}", "error")
    
    def manual_git_push(self):
        """手动推送Git"""
        self.log_message("手动推送Git...")
        try:
            # 添加所有文件
            subprocess.run([self.config["git_path"], "add", "."], 
                          cwd=self.project_path, capture_output=True, text=True)
            
            # 提交
            subprocess.run([self.config["git_path"], "commit", "-m", "手动更新"], 
                          cwd=self.project_path, capture_output=True, text=True)
            
            # 推送
            result = subprocess.run([self.config["git_path"], "push"], 
                                  cwd=self.project_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("Git推送成功", "success")
            else:
                self.log_message(f"Git推送失败: {result.stderr}", "error")
        except Exception as e:
            self.log_message(f"手动推送Git失败: {str(e)}", "error")
    
    def diagnose_git_connection(self):
        """Git连接诊断"""
        self.log_message("Git连接诊断...")
        try:
            # 检查远程
            result = subprocess.run([self.config["git_path"], "remote", "-v"], 
                                  cwd=self.project_path, capture_output=True, text=True)
            self.log_message("Git远程:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log_message(f"  {line}")
            
            # 检查分支
            result = subprocess.run([self.config["git_path"], "branch", "-a"], 
                                  cwd=self.project_path, capture_output=True, text=True)
            self.log_message("Git分支:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log_message(f"  {line}")
                    
        except Exception as e:
            self.log_message(f"Git连接诊断失败: {str(e)}", "error")
    
    def switch_to_ssh(self):
        """切换到SSH"""
        self.log_message("切换到SSH...")
        self.log_message("此功能暂未实现", "warning")
    
    def clear_npm_cache(self):
        """清除npm缓存"""
        self.log_message("清除npm缓存...")
        try:
            result = subprocess.run([self.config["npm_path"], "cache", "clean", "--force"], 
                                  cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message("npm缓存已清除", "success")
            else:
                self.log_message(f"清除npm缓存失败: {result.stderr}", "error")
        except Exception as e:
            self.log_message(f"清除npm缓存失败: {str(e)}", "error")
    
    def check_config(self):
        """检查配置"""
        self.log_message("检查配置...")
        self.log_message(f"项目路径: {self.project_path}")
        self.log_message(f"docs文件夹: {self.docs_folder}")
        self.log_message(f"侧边栏路径: {self.sidebars_path}")
        self.log_message(f"npm路径: {self.config.get('npm_path', 'npm')}")     
        self.log_message(f"Git路径: {self.config.get('git_path', '未设置')}")
    
    def on_chinese_tree_selection(self, event):
        """处理中文Treeview选择事件"""
        self.update_button_states()
    
    def on_english_tree_selection(self, event):
        """处理英文Treeview选择事件"""
        self.update_button_states()
    
    def update_button_states(self):
        """更新按钮状态"""
        # 获取中文和英文的选择
        chinese_selection = self.tree_chinese.selection()
        english_selection = self.tree_english.selection()
        
        # 默认禁用所有按钮
        self.btn_folder_up.config(state=tk.DISABLED)
        self.btn_folder_down.config(state=tk.DISABLED)
        self.btn_file_up.config(state=tk.DISABLED)
        self.btn_file_down.config(state=tk.DISABLED)
        
        # 检查是否有选择
        if not chinese_selection and not english_selection:
            return
        
        # 优先使用中文选择，如果没有则使用英文选择
        selection = chinese_selection if chinese_selection else english_selection
        tree = self.tree_chinese if chinese_selection else self.tree_english
        
        if selection:
            item_text = tree.item(selection[0], "text")
            # 判断选中的是文件夹还是文件
            if item_text.startswith("📁"):
                # 选中文件夹，启用文件夹排序按钮
                self.btn_folder_up.config(state=tk.NORMAL)
                self.btn_folder_down.config(state=tk.NORMAL)
            elif item_text.startswith("📄"):
                # 选中文件，启用文件排序按钮
                self.btn_file_up.config(state=tk.NORMAL)
                self.btn_file_down.config(state=tk.NORMAL)
    
    def move_folder_up_both(self):
        """同时上移中英文文件夹"""
        self.move_folder_up(self.tree_chinese)
        self.move_folder_up(self.tree_english)
        self.log_message("中英文文件夹已同时上移", "success")
    
    def move_folder_down_both(self):
        """同时下移中英文文件夹"""
        self.move_folder_down(self.tree_chinese)
        self.move_folder_down(self.tree_english)
        self.log_message("中英文文件夹已同时下移", "success")
    
    def move_file_up_both(self):
        """同时上移中英文文件"""
        self.move_file_up(self.tree_chinese)
        self.move_file_up(self.tree_english)
        self.log_message("中英文文件已同时上移", "success")
    
    def move_file_down_both(self):
        """同时下移中英文文件"""
        self.move_file_down(self.tree_chinese)
        self.move_file_down(self.tree_english)
        self.log_message("中英文文件已同时下移", "success")
    
    def move_folder_up(self, tree):
        """上移文件夹（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📁"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                tree.move(item_id, parent, index - 1)
    
    def move_folder_down(self, tree):
        """下移文件夹（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📁"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                tree.move(item_id, parent, index + 1)
    
    def move_file_up(self, tree):
        """上移文件（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📄"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                tree.move(item_id, parent, index - 1)
    
    def move_file_down(self, tree):
        """下移文件（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📄"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                tree.move(item_id, parent, index + 1)
    
    def sync_chinese_to_english(self):
        """将中文排序同步到英文"""
        try:
            # 获取中文树的所有文件夹和文件顺序
            chinese_folders = []
            chinese_files_by_folder = {}
            
            # 获取文件夹顺序
            root_children = self.tree_chinese.get_children()
            for folder_id in root_children:
                folder_text = self.tree_chinese.item(folder_id, "text")
                if folder_text.startswith("📁"):
                    folder_name = folder_text[2:]  # 去掉"📁 "前缀
                    chinese_folders.append(folder_name)
                    
                    # 获取文件顺序
                    file_items = self.tree_chinese.get_children(folder_id)
                    files = []
                    for file_id in file_items:
                        file_text = self.tree_chinese.item(file_id, "text")
                        if file_text.startswith("📄"):
                            file_name = file_text[2:]  # 去掉"📄 "前缀
                            files.append(file_name)
                    
                    chinese_files_by_folder[folder_name] = files
            
            # 更新英文树
            # 先清空英文树
            for item in self.tree_english.get_children():
                self.tree_english.delete(item)
            
            # 重新添加英文树
            self.tree_english.insert("", 0, text="📂 docs文件夹 (英文)", open=True)
            
            # 英文文档路径
            english_docs_path = Path(__file__).parent.parent / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
            
            for chinese_folder_name in chinese_folders:
                # 获取对应的英文文件夹名
                english_folder_name = self.chinese_to_english.get(chinese_folder_name, chinese_folder_name)
                folder_english_path = english_docs_path / english_folder_name
                
                if folder_english_path.exists():
                    folder_id = self.tree_english.insert("", tk.END, text=f"📁 {english_folder_name}", open=True)
                    
                    # 获取英文文件夹内的MDX文件
                    english_mdx_files = []
                    for file in folder_english_path.glob("*.mdx"):
                        english_mdx_files.append(file.name)
                    
                    # 按照中文顺序添加文件（使用映射关系）
                    for chinese_file_name in chinese_files_by_folder.get(chinese_folder_name, []):
                        english_file_name = self.chinese_to_english.get(chinese_file_name, chinese_file_name)
                        if english_file_name in english_mdx_files:
                            self.tree_english.insert(folder_id, tk.END, text=f"📄 {english_file_name}")
                        else:
                            self.tree_english.insert(folder_id, tk.END, text=f"❓ {chinese_file_name} (未翻译)")
                else:
                    folder_id = self.tree_english.insert("", tk.END, text=f"⚠️ {english_folder_name} (文件夹未创建)", open=True)
            
            self.log_message("中文排序已同步到英文", "success")
            
        except Exception as e:
            self.log_message(f"同步中文到英文失败: {str(e)}", "error")
    
    def sync_english_to_chinese(self):
        """将英文排序同步到中文"""
        try:
            # 获取英文树的所有文件夹和文件顺序
            english_folders = []
            english_files_by_folder = {}
            
            # 获取文件夹顺序
            root_children = self.tree_english.get_children()
            for folder_id in root_children:
                folder_text = self.tree_english.item(folder_id, "text")
                if folder_text.startswith("📁"):
                    folder_name = folder_text[2:]  # 去掉"📁 "前缀
                    english_folders.append(folder_name)
                    
                    # 获取文件顺序
                    file_items = self.tree_english.get_children(folder_id)
                    files = []
                    for file_id in file_items:
                        file_text = self.tree_english.item(file_id, "text")
                        if file_text.startswith("📄"):
                            file_name = file_text[2:]  # 去掉"📄 "前缀
                            files.append(file_name)
                    
                    english_files_by_folder[folder_name] = files
            
            # 更新中文树
            # 先清空中文树
            for item in self.tree_chinese.get_children():
                self.tree_chinese.delete(item)
            
            # 重新添加中文树
            self.tree_chinese.insert("", 0, text="📂 docs文件夹 (中文)", open=True)
            
            for english_folder_name in english_folders:
                # 获取对应的中文文件夹名
                chinese_folder_name = self.english_to_chinese.get(english_folder_name, english_folder_name)
                folder_path = self.docs_folder / chinese_folder_name
                
                if folder_path.exists():
                    folder_id = self.tree_chinese.insert("", tk.END, text=f"📁 {chinese_folder_name}", open=True)
                    
                    # 获取中文文件夹内的MDX文件
                    mdx_files = []
                    for file in folder_path.glob("*.mdx"):
                        mdx_files.append(file.name)
                    
                    # 按照英文顺序添加文件（使用映射关系）
                    for english_file_name in english_files_by_folder.get(english_folder_name, []):
                        chinese_file_name = self.english_to_chinese.get(english_file_name, english_file_name)
                        if chinese_file_name in mdx_files:
                            self.tree_chinese.insert(folder_id, tk.END, text=f"📄 {chinese_file_name}")
                        else:
                            self.tree_chinese.insert(folder_id, tk.END, text=f"❓ {english_file_name} (文件不存在)")
                else:
                    folder_id = self.tree_chinese.insert("", tk.END, text=f"⚠️ {chinese_folder_name} (文件夹不存在)", open=True)
            
            self.log_message("英文排序已同步到中文", "success")
            
        except Exception as e:
            self.log_message(f"同步英文到中文失败: {str(e)}", "error")
    
    def save_both_sort_config(self):
        """保存中英文排序配置"""
        try:
            # 使用中文树的顺序作为基准
            folders = []
            files_by_folder = {}
            
            # 获取文件夹顺序
            root_children = self.tree_chinese.get_children()
            for folder_id in root_children:
                folder_text = self.tree_chinese.item(folder_id, "text")
                if folder_text.startswith("📁"):
                    folder_name = folder_text[2:]  # 去掉"📁 "前缀
                    folders.append(folder_name)
                    
                    # 获取文件顺序
                    file_items = self.tree_chinese.get_children(folder_id)
                    files = []
                    for file_id in file_items:
                        file_text = self.tree_chinese.item(file_id, "text")
                        if file_text.startswith("📄"):
                            file_name = file_text[2:]  # 去掉"📄 "前缀
                            # 去掉.mdx扩展名
                            if file_name.endswith(".mdx"):
                                file_name = file_name[:-4]
                            files.append(file_name)
                    
                    files_by_folder[folder_name] = files
            
            # 保存到配置文件
            import json
            sort_config = {
                "folders": folders,
                "files": files_by_folder
            }
            
            sort_config_path = Path(__file__).parent / "sort_config.json"
            with open(sort_config_path, 'w', encoding='utf-8') as f:
                json.dump(sort_config, f, ensure_ascii=False, indent=2)
            
            self.log_message("中英文排序配置已保存", "success")
            
        except Exception as e:
            self.log_message(f"保存排序配置失败: {str(e)}", "error")
    
    # 旧的排序方法已删除，使用新的中英文同步方法

def main():
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()