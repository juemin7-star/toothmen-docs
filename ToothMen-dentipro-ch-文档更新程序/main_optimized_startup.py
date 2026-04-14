#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.16 - 优化启动速度版
功能：文件夹分类管理 + 自动化部署工作流 + 完整构建流程
按照数字前缀文件夹结构自动生成分类侧边栏
包含缓存清理和完整工作流系统
优化启动速度，减少界面跳动
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
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v3.16 - 优化启动版")
        self.root.geometry("1400x1000")
        
        # 设置最小尺寸
        self.root.minsize(1200, 800)
        
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
        
        # 延迟初始化的标志
        self.initialization_complete = False
        
        # 创建UI（先创建界面，后初始化耗时的组件）
        self.create_widgets()
        
        # 显示加载提示
        self.show_loading_message()
        
        # 在后台线程中初始化耗时的组件
        self.init_in_background()
        
    def show_loading_message(self):
        """显示加载提示"""
        self.loading_label = ttk.Label(self.root, text="正在初始化程序，请稍候...", 
                                      font=("Arial", 12))
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update()
        
    def hide_loading_message(self):
        """隐藏加载提示"""
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()
            del self.loading_label
            
    def init_in_background(self):
        """在后台线程中初始化耗时的组件"""
        def _init():
            try:
                # 初始化管理器（这里可能会耗时）
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
                
                # 标记初始化完成
                self.initialization_complete = True
                
                # 在主线程中更新UI
                self.root.after(0, self.on_initialization_complete)
                
            except Exception as e:
                # 在主线程中显示错误
                self.root.after(0, lambda: self.show_init_error(str(e)))
        
        # 启动后台线程
        thread = threading.Thread(target=_init)
        thread.daemon = True
        thread.start()
        
    def on_initialization_complete(self):
        """初始化完成后的回调"""
        # 隐藏加载提示
        self.hide_loading_message()
        
        # 初始加载文件夹结构（也在后台进行）
        self.refresh_folder_structure_in_background()
        
        # 启用所有按钮
        self.enable_all_buttons()
        
        # 记录日志
        self.log("✅ 程序初始化完成", "success")
        
    def show_init_error(self, error_msg):
        """显示初始化错误"""
        self.hide_loading_message()
        messagebox.showerror("初始化错误", f"程序初始化失败:\n{error_msg}")
        self.log(f"❌ 初始化失败: {error_msg}", "error")
        
    def refresh_folder_structure_in_background(self):
        """在后台刷新文件夹结构"""
        def _refresh():
            try:
                # 调用刷新方法
                self.refresh_folder_structure()
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ 刷新文件夹结构失败: {str(e)}", "error"))
        
        thread = threading.Thread(target=_refresh)
        thread.daemon = True
        thread.start()
        
    def enable_all_buttons(self):
        """启用所有按钮"""
        # 这里可以添加启用按钮的代码
        pass
        
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
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v3.16 - 优化启动版", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 创建文件夹结构区域（占据全部宽度）
        self.create_folder_structure_area(main_frame)
        
        # 创建控制按钮区域（初始禁用）
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
        
        # 上移文件夹按钮（初始禁用）
        self.btn_folder_up = tk.Button(sort_frame, text="⬆ 上移文件夹", 
                                      command=self.move_folder_up, width=14, state=tk.DISABLED)
        self.btn_folder_up.pack(pady=3)
        
        # 下移文件夹按钮（初始禁用）
        self.btn_folder_down = tk.Button(sort_frame, text="⬇ 下移文件夹", 
                                        command=self.move_folder_down, width=14, state=tk.DISABLED)
        self.btn_folder_down.pack(pady=3)
        
        # 文件排序标题
        file_sort_label = ttk.Label(sort_frame, text="📄 文件排序", font=("Arial", 10, "bold"))
        file_sort_label.pack(pady=(15, 5))
        
        # 上移文件按钮（初始禁用）
        self.btn_file_up = tk.Button(sort_frame, text="⬆ 上移文件", 
                                    command=self.move_file_up, width=14, state=tk.DISABLED)
        self.btn_file_up.pack(pady=3)
        
        # 下移文件按钮（初始禁用）
        self.btn_file_down = tk.Button(sort_frame, text="⬇ 下移文件", 
                                      command=self.move_file_down, width=14, state=tk.DISABLED)
        self.btn_file_down.pack(pady=3)
        
        # 保存排序按钮（初始禁用）
        self.btn_save_sort = tk.Button(sort_frame, text="💾 保存排序", 
                                      command=self.save_sort_config, width=14, 
                                      bg="#4CAF50", fg="white", state=tk.DISABLED)
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
        
        # 完整工作流按钮（初始禁用）
        self.complete_workflow_btn = ttk.Button(left_frame, text="🚀 完整工作流", 
                                               command=self.complete_workflow, state=tk.DISABLED)
        self.complete_workflow_btn.grid(row=0, column=0, padx=5)
        
        # 检测MDX语法按钮（初始禁用）
        self.check_mdx_btn = ttk.Button(left_frame, text="检测MDX语法", 
                                       command=self.check_mdx_syntax, state=tk.DISABLED)
        self.check_mdx_btn.grid(row=0, column=1, padx=5)
        
        # 部署流程按钮（初始禁用）
        self.deploy_start_btn = ttk.Button(left_frame, text="开始部署", 
                                          command=self.start_deployment, state=tk.DISABLED)
        self.deploy_start_btn.grid(row=0, column=2, padx=5)
        
        self.deploy_end_btn = ttk.Button(left_frame, text="结束流程", 
                                        command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=3, padx=5)
        
        # 验证部署按钮（初始禁用）
        self.verify_deploy_btn = ttk.Button(left_frame, text="验证部署", 
                                           command=self.verify_deployment, state=tk.DISABLED)
        self.verify_deploy_btn.grid(row=0, column=4, padx=5)
        
        # 清理缓存按钮（初始禁用）
        self.clean_cache_btn = ttk.Button(left_frame, text="🧹 清理缓存", 
                                         command=self.clean_cache, state=tk.DISABLED)
        self.clean_cache_btn.grid(row=0, column=5, padx=5)
        
        # 右侧：部署步骤按钮
        right_frame = ttk.Frame(control_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        # 部署步骤按钮（初始禁用）
        self.step_buttons = []
        for i, step in enumerate(["刷新文件结构", "生成侧边栏", "本地构建测试", "本地预览", "自动部署"]):
            btn = ttk.Button(right_frame, text=step, command=lambda s=step: self.execute_step(s), 
                           state=tk.DISABLED)
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
        
        # 调试按钮（初始禁用）
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
        
        # 同时输出到控制台
        print(formatted_message.strip())
    
    # 注意：这里省略了其他方法，因为它们与原始版本相同
    # 为了简洁，我只保留了关键部分
    
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
            
            # 启用排序按钮
            self.btn_save_sort.config(state=tk.NORMAL)
            
            # 启用其他按钮
            self.enable_control_buttons()
            
        except Exception as e:
            self.log(f"❌ 刷新文件夹结构失败: {str(e)}", "error")
    
    def enable_control_buttons(self):
        """启用控制按钮"""
        # 启用功能按钮
        self.complete_workflow_btn.config(state=tk.NORMAL)
        self.check_mdx_btn.config(state=tk.NORMAL)
        self.deploy_start_btn.config(state=tk.NORMAL)
        self.clean_cache_btn.config(state=tk.NORMAL)
        self.verify_deploy_btn.config(state=tk.NORMAL)
        
        # 启用调试按钮
        for btn in self.debug_buttons:
            btn.config(state=tk.NORMAL)
    
    # 注意：这里省略了其他方法（排序按钮方法、工作流方法等）
    # 它们与原始版本相同，只是需要添加状态检查
    
    def move_folder_up(self):
        """上移文件夹"""
        if not self.initialization_complete:
            self.log("⚠️  程序正在初始化，请稍候...", "warning")
            return
        
        # 原有的move_folder_up方法实现...
        pass
    
    # 其他方法类似，需要添加initialization_complete检查

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()