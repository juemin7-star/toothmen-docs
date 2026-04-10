#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 - 全新版本
功能：文件夹分类管理 + 自动化部署工作流
按照数字前缀文件夹结构自动生成分类侧边栏
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
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v2.1")
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
        main_frame.rowconfigure(0, weight=0)  # 标题行
        main_frame.rowconfigure(1, weight=1)  # 文件夹结构区域
        main_frame.rowconfigure(2, weight=0)  # 控制按钮区域
        main_frame.rowconfigure(3, weight=1)  # 日志和调试工具区域
        
        # 创建顶部标题
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v2.0", 
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
        folder_frame.columnconfigure(0, weight=1)
        folder_frame.rowconfigure(0, weight=1)
        folder_frame.rowconfigure(1, weight=0)  # 水平滚动条行
        
        # 创建Treeview显示文件夹结构
        self.tree = ttk.Treeview(folder_frame, columns=("type", "count"), show="tree headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置列
        self.tree.heading("#0", text="文件夹/文件结构")
        self.tree.heading("type", text="类型")
        self.tree.heading("count", text="数量")
        
        # 设置列宽度 - 加大左侧按钮区域
        self.tree.column("#0", width=700, minwidth=500)  # 加大宽度
        self.tree.column("type", width=120, minwidth=100)  # 加大宽度
        self.tree.column("count", width=100, minwidth=80)  # 加大宽度
        
        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(folder_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.config(yscrollcommand=v_scrollbar.set)
        
        # 水平滚动条（文件多时方便查看）
        h_scrollbar = ttk.Scrollbar(folder_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.config(xscrollcommand=h_scrollbar.set)
        
        # 绑定双击事件
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        
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
        
        # 配置日志输出（直接输出到控制台和文件）
        # 重写logger的log方法，同时输出到文本框
        original_log = self.logger.log
        def new_log(message, level="INFO"):
            original_log(message, level)
            # 同时输出到文本框
            self.log_text.insert(tk.END, f"[{level}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.update()
        self.logger.log = new_log
        
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
            ("⚡ 切换到SSH", self.switch_to_ssh),
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
        
    def create_control_area(self, parent):
        """创建控制按钮区域"""
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
        self.btn_start_deploy = tk.Button(deploy_control_frame, text="▶ 开始部署流程", 
                                         command=self.start_deployment_flow, width=20,
                                         bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_start_deploy.pack(side=tk.LEFT, padx=5)
        
        # 结束流程按钮
        self.btn_end_deploy = tk.Button(deploy_control_frame, text="■ 结束流程", 
                                       command=self.end_deployment_flow, width=20, state="disabled",
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
        ttk.Label(deploy_steps_frame, text="部署步骤:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # 部署步骤按钮（按顺序执行）
        self.deployment_buttons = [
            ("刷新文件结构", self.refresh_folder_structure, "刷新并显示文件夹结构"),
            ("生成侧边栏", self.generate_sidebar, "生成Docusaurus侧边栏"),
            ("本地构建测试", self.local_build_test, "执行npm run build测试构建"),
            ("本地预览", self.local_preview, "启动本地开发服务器预览"),
            ("自动部署", self.auto_deploy, "执行Git推送和Cloudflare部署"),
        ]
        
        # 创建部署步骤按钮（默认禁用）
        for i, (text, command, tooltip) in enumerate(self.deployment_buttons):
            btn = tk.Button(deploy_steps_frame, text=text, command=command, width=15, state="disabled",
                          bg="SystemButtonFace", fg="black", relief="raised", bd=2)
            btn.pack(side=tk.LEFT, padx=5)
            
            # 存储按钮引用以便更新状态
            setattr(self, f"btn_{text.replace(' ', '_')}", btn)
            
            # 添加工具提示
            self.create_tooltip(btn, tooltip)
        
        # 部署流程状态变量
        self.deployment_started = False
        self.deployment_step = 0
    
    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def enter(event):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(self.tooltip, text=text, background="#ffffe0", 
                             relief="solid", borderwidth=1, padding=5)
            label.pack()
        
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                delattr(self, 'tooltip')
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def refresh_folder_structure(self):
        """刷新文件夹结构显示"""
        self.logger.info("开始刷新文件夹结构...")
        
        # 如果是在部署流程中，更新按钮状态为运行中
        if self.deployment_started:
            self.update_button_state("刷新文件结构", "running")
        
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 扫描docs文件夹结构
        self.scan_and_display_structure()
        
        # 记录日志
        self.logger.info("文件夹结构已刷新")
        
        # 如果是在部署流程中，更新按钮状态
        if self.deployment_started:
            self.update_button_state("刷新文件结构", "success")
        
    def scan_and_display_structure(self):
        """扫描并显示文件夹结构"""
        try:
            # 获取所有一级文件夹（按数字前缀排序）
            folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    folders.append(item.name)
            
            # 按数字前缀排序
            sorted_folders = self.sort_by_number_prefix(folders)
            
            total_files = 0
            total_folders = len(sorted_folders)
            
            # 添加每个文件夹到树
            for folder_name in sorted_folders:
                folder_path = self.docs_folder / folder_name
                
                # 清理文件夹显示名称（移除数字前缀）
                display_name = self.clean_name(folder_name)
                
                # 判断是否需要倒序排序
                is_reverse = self.should_reverse_order(folder_name)
                
                # 获取文件夹内的MDX文件
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                
                # 按规则排序文件
                sorted_files = self.sort_files_by_rule(mdx_files, reverse=is_reverse)
                
                # 添加文件夹节点 - 默认展开
                folder_id = self.tree.insert("", "end", text=f"📁 {display_name}", 
                                           values=("文件夹", f"{len(sorted_files)}个文件"),
                                           open=True)  # 默认展开
                
                # 添加文件节点
                for file_name in sorted_files:
                    # 清理文件显示名称
                    file_display_name = self.clean_name(file_name)
                    self.tree.insert(folder_id, "end", text=f"📄 {file_display_name}", 
                                   values=("MDX文件", ""))
                    total_files += 1
                
                # 如果没有文件，显示提示
                if not sorted_files:
                    self.tree.insert(folder_id, "end", text="(空文件夹)", 
                                   values=("提示", "无MDX文件"))
            
            # 添加根节点统计
            root_text = f"📂 docs文件夹 (共{total_folders}个分类，{total_files}个MDX文件)"
            self.tree.insert("", 0, text=root_text, values=("根目录", ""), open=True)
            
        except Exception as e:
            self.logger.error(f"扫描文件夹结构失败: {str(e)}")
    
    def sort_by_number_prefix(self, items: List[str]) -> List[str]:
        """按数字前缀排序项目"""
        def extract_sort_key(name: str) -> Tuple[float, str]:
            """提取排序键值"""
            # 匹配数字前缀（支持整数和小数）
            match = re.match(r'^([0-9]+(?:\.[0-9]+)?)-(.+)$', name)
            if match:
                num = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
                return (num, match.group(2))
            
            # 无前缀，按原名称排序
            return (float('inf'), name)
        
        return sorted(items, key=extract_sort_key)
    
    def clean_name(self, name: str) -> str:
        """
        清理名称 - 移除数字前缀和扩展名
        
        Args:
            name: 原始名称（如"1-程序安装说明.mdx"）
        
        Returns:
            清理后的名称（如"程序安装说明"）
        """
        # 移除.mdx扩展名
        if name.endswith('.mdx'):
            name = name[:-4]
        
        # 移除数字前缀（如"1-"）
        import re
        name = re.sub(r'^\d+\-', '', name)
        
        return name
    
    def clean_name_for_url(self, name: str) -> str:
        """
        清理名称用于URL - 移除数字前缀和扩展名，中文转英文
        
        Args:
            name: 原始名称（如"1-程序安装说明.mdx"）
        
        Returns:
            清理后的英文名称（如"program-installation-guide"）
        """
        # 移除.mdx扩展名
        if name.endswith('.mdx'):
            name = name[:-4]
        
        # 移除数字前缀（如"1-"）
        import re
        name = re.sub(r'^\d+\-', '', name)
        
        # 中文转英文/拼音映射表
        chinese_to_english = {
            # 文件夹名称映射
            '程序安装说明': 'program-installation-guide',
            '云更新服务注册说明': 'cloud-update-service-registration',
            '补丁更新日志': 'patch-update-log',
            
            # 文件名称映射
            '主程序安装说明': 'main-program-installation',
            '云更新服务注册说明': 'cloud-update-service-registration',
            '注册规则特殊说明': 'registration-rules-special',
            'NEW-26040101': 'new-26040101',
            'NEW-26040902': 'new-26040902',
        }
        
        # 如果名称在映射表中，使用英文名称
        if name in chinese_to_english:
            return chinese_to_english[name]
        
        # 否则，将中文转换为拼音（简单实现）
        # 这里使用简单的替换，实际可以使用pypinyin库
        pinyin_map = {
            '程序': 'program',
            '安装': 'installation',
            '说明': 'guide',
            '云': 'cloud',
            '更新': 'update',
            '服务': 'service',
            '注册': 'registration',
            '规则': 'rules',
            '特殊': 'special',
            '补丁': 'patch',
            '日志': 'log',
            '主': 'main',
        }
        
        # 简单的中文转英文
        result = name
        for chinese, english in pinyin_map.items():
            result = result.replace(chinese, english)
        
        # 如果还有中文字符，使用通用格式
        if any('\u4e00' <= char <= '\u9fff' for char in result):
            # 生成安全的英文名称：移除特殊字符，用连字符连接
            import unicodedata
            result = unicodedata.normalize('NFKD', result)
            result = result.encode('ascii', 'ignore').decode('ascii')
            result = re.sub(r'[^\w\s-]', '', result).strip().lower()
            result = re.sub(r'[-\s]+', '-', result)
        
        return result
    
    def should_reverse_order(self, folder_name: str) -> bool:
        """判断文件夹是否需要倒序排序"""
        clean_name = self.clean_name(folder_name)
        for pattern in self.reverse_order_folders:
            if pattern in clean_name:
                return True
        return False
    
    def sort_files_by_rule(self, files: List[str], reverse: bool = False) -> List[str]:
        """按规则排序文件"""
        def extract_number(filename: str) -> float:
            """提取文件数字前缀"""
            match = re.match(r'^([0-9]+(?:\.[0-9]+)?)-', filename)
            if match:
                num = match.group(1)
                return float(num) if '.' in num else int(num)
            return float('inf')  # 无数字前缀的排最后
        
        return sorted(files, key=extract_number, reverse=reverse)
    
    def on_tree_double_click(self, event):
        """树节点双击事件"""
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        
        # 切换展开/折叠状态
        if self.tree.item(item, "open"):
            self.tree.item(item, open=False)
        else:
            self.tree.item(item, open=True)
    
    def check_mdx_syntax(self):
        """检测MDX语法"""
        self.logger.info("开始检测MDX语法...")
        
        # 在新线程中执行检测
        thread = threading.Thread(target=self._check_mdx_syntax_thread)
        thread.daemon = True
        thread.start()
    
    def _check_mdx_syntax_thread(self):
        """检测MDX语法线程"""
        try:
            total_files = 0
            error_files = []
            
            # 遍历所有MDX文件
            for mdx_file in self.docs_folder.rglob("*.mdx"):
                total_files += 1
                relative_path = mdx_file.relative_to(self.docs_folder)
                
                try:
                    # 使用check_single_file方法检测单个文件
                    issues = self.mdx_checker.check_single_file(mdx_file)
                    
                    if issues:
                        error_files.append(str(relative_path))
                        for issue in issues:
                            self.logger.error(f"  {relative_path}: 行{issue['line']} - {issue['type']}: {issue['message']}")
                    else:
                        self.logger.info(f"  ✓ {relative_path}")
                        
                except Exception as e:
                    error_files.append(str(relative_path))
                    self.logger.error(f"  {relative_path}: 检测失败 - {str(e)}")
            
            # 显示统计信息
            self.logger.info("=" * 60)
            self.logger.info(f"MDX语法检测完成:")
            self.logger.info(f"  总文件数: {total_files}")
            self.logger.info(f"  错误文件: {len(error_files)}")
            
            if error_files:
                self.logger.warning("错误文件列表:")
                for file in error_files:
                    self.logger.warning(f"  ❌ {file}")
                self.logger.warning(f"检测完成：发现{len(error_files)}个文件有语法错误")
            else:
                self.logger.success("所有MDX文件语法正确！")
                
        except Exception as e:
            self.logger.error(f"检测MDX语法失败: {str(e)}")
    
    def generate_sidebar(self):
        """生成侧边栏"""
        self.logger.info("开始生成侧边栏...")
        
        # 如果是在部署流程中，更新按钮状态为运行中
        if self.deployment_started:
            self.update_button_state("生成侧边栏", "running")
        
        # 在新线程中执行生成
        thread = threading.Thread(target=self._generate_sidebar_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_sidebar_thread(self):
        """生成侧边栏线程"""
        try:
            # 获取文件夹结构并生成侧边栏内容
            sidebar_content = self.generate_sidebar_content()
            
            # 写入sidebars.js文件
            with open(self.sidebars_path, 'w', encoding='utf-8') as f:
                f.write(sidebar_content)
            
            self.logger.success("侧边栏生成成功！")
            self.logger.info(f"文件已保存: {self.sidebars_path}")
            
            # 显示生成的侧边栏内容
            self.logger.info("生成的侧边栏结构:")
            self.logger.info("-" * 40)
            for line in sidebar_content.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
            
            self.logger.success("侧边栏已成功生成并保存！")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                self.update_button_state("生成侧边栏", "success")
            
        except Exception as e:
            self.logger.error(f"生成侧边栏失败: {str(e)}")
            self.logger.error(f"生成侧边栏失败: {str(e)}")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                self.update_button_state("生成侧边栏", "error")
    
    def generate_sidebar_content(self) -> str:
        """生成侧边栏内容"""
        lines = []
        lines.append("const sidebars = {")
        lines.append("  tutorialSidebar: [")
        
        # 获取所有一级文件夹（按数字前缀排序）
        folders = []
        for item in self.docs_folder.iterdir():
            if item.is_dir():
                folders.append(item.name)
        
        sorted_folders = self.sort_by_number_prefix(folders)
        
        for folder_name in sorted_folders:
            folder_path = self.docs_folder / folder_name
            
            # 清理文件夹显示名称（显示中文）
            display_name = self.clean_name(folder_name)
            
            # 判断是否需要倒序排序
            is_reverse = self.should_reverse_order(folder_name)
            
            # 获取文件夹内的MDX文件
            mdx_files = []
            for file in folder_path.glob("*.mdx"):
                mdx_files.append(file.name)
            
            # 按规则排序文件
            sorted_files = self.sort_files_by_rule(mdx_files, reverse=is_reverse)
            
            if sorted_files:
                lines.append("    {")
                lines.append(f"      type: 'category',")
                lines.append(f"      label: '{display_name}',")
                lines.append(f"      items: [")
                
                for file_name in sorted_files:
                        # 生成文档ID（Docusaurus格式：文件夹名/文件名）
                        # 使用clean_name保持中文文档ID，与文件实际路径一致
                        # 例如：1-主程序安装说明.mdx → 程序安装说明/主程序安装说明
                        clean_file_name = self.clean_name(file_name)
                        doc_id = f"{self.clean_name(folder_name)}/{clean_file_name}"
                        
                        # 生成英文slug用于URL路径
                        english_folder_name = self.clean_name_for_url(folder_name)
                        english_file_name = self.clean_name_for_url(file_name)
                        english_slug = f"{english_folder_name}/{english_file_name}"
                        
                        # 使用完整语法：type: 'doc', id: 'docId', label: '...'
                        # 注意：slug应该放在doc对象内部，但Docusaurus可能不支持
                        # 根据文档，我们需要使用简写语法或完整语法，但不能混合
                        # 暂时先使用简写语法，slug问题通过其他方式解决
                        lines.append(f"        '{doc_id}',")
                
                lines.append(f"      ],")
                lines.append(f"      collapsed: true,")
                lines.append("    },")
        
        lines.append("  ],")
        lines.append("};")
        lines.append("")
        lines.append("export default sidebars;")
        
        return "\n".join(lines)
    
    def open_docs_folder(self):
        """打开docs文件夹"""
        try:
            os.startfile(str(self.docs_folder))
            self.logger.info(f"已打开文件夹: {self.docs_folder}")
        except Exception as e:
            self.logger.error(f"打开文件夹失败: {str(e)}")
    
    def local_build_test(self):
        """本地构建测试"""
        self.logger.info("开始本地构建测试...")
        
        # 如果是在部署流程中，更新按钮状态为运行中
        if self.deployment_started:
            self.update_button_state("本地构建测试", "running")
        
        # 在新线程中执行构建
        thread = threading.Thread(target=self._local_build_test_thread)
        thread.daemon = True
        thread.start()
    
    def _local_build_test_thread(self):
        """本地构建测试线程"""
        try:
            success, output = self.deployment_manager.local_build_test()
            if success:
                self.logger.success("本地构建测试成功！")
                self.logger.info("本地构建测试成功！")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    self.update_button_state("本地构建测试", "success")
            else:
                self.logger.error("本地构建测试失败")
                self.logger.error("本地构建测试失败，请查看日志")
                # 输出详细错误信息
                self.logger.error("详细错误信息:")
                for line in output.split('\n'):
                    if line.strip():
                        self.logger.error(f"  {line}")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    self.update_button_state("本地构建测试", "error")
        except Exception as e:
            self.logger.error(f"本地构建测试异常: {str(e)}")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                self.update_button_state("本地构建测试", "error")
    
    def local_preview(self):
        """本地预览"""
        self.logger.info("开始本地预览...")
        
        # 如果是在部署流程中，更新按钮状态为运行中
        if self.deployment_started:
            self.update_button_state("本地预览", "running")
        
        # 在新线程中执行预览
        thread = threading.Thread(target=self._local_preview_thread)
        thread.daemon = True
        thread.start()
    
    def _local_preview_thread(self):
        """本地预览线程"""
        try:
            success, output = self.deployment_manager.local_preview()
            if success:
                self.logger.success("本地预览服务器已启动！")
                self.logger.info("本地预览服务器已启动，请在浏览器中查看")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    self.update_button_state("本地预览", "success")
                
                # 延迟3秒后自动打开浏览器
                self.logger.info("服务器已启动，3秒后自动打开浏览器...")
                self.root.after(3000, self.open_local_preview)
            else:
                self.logger.error("启动本地预览失败")
                self.logger.error("启动本地预览失败，请查看日志")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    self.update_button_state("本地预览", "error")
        except Exception as e:
            self.logger.error(f"启动本地预览异常: {str(e)}")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                self.update_button_state("本地预览", "error")
    
    def open_local_preview(self):
        """自动打开本地预览页面"""
        try:
            import webbrowser
            import time
            
            # 等待服务器完全启动（增加等待时间）
            self.logger.info("等待服务器完全启动...")
            time.sleep(5)
            
            # 测试服务器是否真的在运行
            try:
                import urllib.request
                response = urllib.request.urlopen("http://localhost:3000", timeout=10)
                status_code = response.getcode()
                self.logger.info(f"本地服务器状态码: {status_code}")
            except Exception as e:
                self.logger.warning(f"服务器可能尚未完全启动: {str(e)}")
                self.logger.info("请稍等几秒再刷新页面")
            
            # 打开网站首页
            url = "http://localhost:3000"
            
            # 同时显示可用的文档链接，方便用户快速访问
            self.logger.info("已打开网站首页，可用文档链接:")
            
            # 从侧边栏中获取所有文档链接
            sidebars_path = self.project_path / "sidebars.js"
            if sidebars_path.exists():
                try:
                    with open(sidebars_path, 'r', encoding='utf-8') as f:
                        sidebar_content = f.read()
                    
                    # 提取所有文档ID
                    import re
                    doc_ids = re.findall(r"'([^']+/[^']+)'", sidebar_content)
                    
                    if doc_ids:
                        for doc_id in doc_ids:
                            # 将中文文档ID转换为英文URL路径
                            # 例如：程序安装说明/主程序安装说明 → program-installation-guide/main-program-installation
                            if '/' in doc_id:
                                folder_part, file_part = doc_id.split('/', 1)
                                folder_english = self.clean_name_for_url(folder_part)
                                file_english = self.clean_name_for_url(file_part)
                                english_doc_id = f"{folder_english}/{file_english}"
                                doc_url = f"http://localhost:3000/docs/{english_doc_id}"
                            else:
                                doc_url = f"http://localhost:3000/docs/{doc_id}"
                            self.logger.info(f"  • {doc_id}: {doc_url}")
                        
                        # 同时自动打开第一个文档（避免首页404）
                        first_doc_id = doc_ids[0]
                        if '/' in first_doc_id:
                            folder_part, file_part = first_doc_id.split('/', 1)
                            folder_english = self.clean_name_for_url(folder_part)
                            file_english = self.clean_name_for_url(file_part)
                            english_first_doc_id = f"{folder_english}/{file_english}"
                            first_doc_url = f"http://localhost:3000/docs/{english_first_doc_id}"
                        else:
                            first_doc_url = f"http://localhost:3000/docs/{first_doc_id}"
                        self.logger.info(f"同时打开第一个文档: {first_doc_url}")
                        webbrowser.open(first_doc_url)
                    else:
                        self.logger.info("  • 未找到文档链接")
                        webbrowser.open(url)
                except Exception as e:
                    self.logger.info(f"  • 读取侧边栏失败: {str(e)}")
                    webbrowser.open(url)
            else:
                self.logger.info("  • 侧边栏文件不存在")
                webbrowser.open(url)
            
            self.logger.success(f"已自动打开浏览器访问: {url}")
            self.logger.info("如果显示404，请:")
            self.logger.info("1. 清除浏览器缓存")
            self.logger.info("2. 使用无痕模式")
            self.logger.info("3. 等待几秒后刷新页面")
            
        except Exception as e:
            self.logger.error(f"自动打开浏览器失败: {str(e)}")
            self.logger.info("请手动访问: http://localhost:3000")
    
    def auto_deploy(self):
        """自动部署"""
        self.logger.info("开始自动部署...")
        
        # 如果是在部署流程中，更新按钮状态为运行中
        if self.deployment_started:
            self.update_button_state("自动部署", "running")
        
        # 在新线程中执行部署
        thread = threading.Thread(target=self._auto_deploy_thread)
        thread.daemon = True
        thread.start()
    
    def _auto_deploy_thread(self):
        """自动部署线程"""
        try:
            success, output = self.deployment_manager.auto_deploy()
            if success:
                self.logger.success("自动部署成功！")
                self.logger.info("自动部署成功！")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    self.update_button_state("自动部署", "success")
            else:
                self.logger.error("自动部署失败")
                self.logger.error("自动部署失败，请查看日志")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    self.update_button_state("自动部署", "error")
        except Exception as e:
            self.logger.error(f"自动部署异常: {str(e)}")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                self.update_button_state("自动部署", "error")
    
    def verify_deployment(self):
        """验证部署（独立功能，随时可用）"""
        self.logger.info("验证部署状态...")
        
        # 在新线程中执行验证
        thread = threading.Thread(target=self._verify_deployment_thread)
        thread.daemon = True
        thread.start()
    
    def _verify_deployment_thread(self):
        """验证部署线程 - 简单打开网页，不写入日志"""
        try:
            # 直接调用验证部署，它会自动打开网页
            success, output = self.deployment_manager.verify_deployment()
            
            # 只在日志中显示简单信息
            self.logger.info(f"验证部署: {output}")
            
        except Exception as e:
            # 即使出错也不显示错误
            self.logger.info("验证部署: 请手动访问 https://docs.toothmen.com")
    
    # ==================== 调试工具方法 ====================
    
    def test_network_connection(self):
        """测试网络连接"""
        self.logger.info("正在测试网络连接...")
        
        import subprocess
        import threading
        
        def _test_network():
            try:
                # 测试ping GitHub
                self.logger.info("测试ping github.com...")
                result = subprocess.run(
                    ["ping", "-n", "4", "github.com"],
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
                
                if result.returncode == 0:
                    self.logger.success("✅ Ping测试成功")
                    # 提取关键信息
                    for line in result.stdout.split('\n'):
                        if "数据包:" in line or "Packets:" in line:
                            self.logger.info(f"网络状态: {line.strip()}")
                        if "平均 =" in line or "Average =" in line:
                            self.logger.info(f"网络延迟: {line.strip()}")
                else:
                    self.logger.error("❌ Ping测试失败")
                    self.logger.error(f"错误信息: {result.stderr}")
                
                # 测试HTTPS访问
                self.logger.info("测试HTTPS访问...")
                import urllib.request
                try:
                    response = urllib.request.urlopen("https://github.com", timeout=10)
                    self.logger.success(f"✅ HTTPS访问成功 (状态码: {response.status})")
                except Exception as e:
                    self.logger.error(f"❌ HTTPS访问失败: {str(e)}")
                    
            except Exception as e:
                self.logger.error(f"网络测试异常: {str(e)}")
        
        # 在新线程中执行网络测试
        thread = threading.Thread(target=_test_network)
        thread.daemon = True
        thread.start()
    
    def check_git_status(self):
        """检查Git状态"""
        self.logger.info("正在检查Git状态...")
        
        import threading
        
        def _check_git():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["status", "--short"]
                )
                
                if success:
                    if output.strip():
                        self.logger.info("Git状态:")
                        self.logger.info(output)
                    else:
                        self.logger.success("✅ 工作区干净，没有未提交的更改")
                else:
                    self.logger.error(f"❌ Git状态检查失败: {output}")
                    
            except Exception as e:
                self.logger.error(f"Git状态检查异常: {str(e)}")
        
        thread = threading.Thread(target=_check_git)
        thread.daemon = True
        thread.start()
    
    def show_git_log(self):
        """查看Git日志"""
        self.logger.info("正在获取Git提交历史...")
        
        import threading
        
        def _show_log():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-10"]
                )
                
                if success:
                    self.logger.info("最近10次提交:")
                    self.logger.info(output)
                else:
                    self.logger.error(f"❌ 获取Git日志失败: {output}")
                    
            except Exception as e:
                self.logger.error(f"获取Git日志异常: {str(e)}")
        
        thread = threading.Thread(target=_show_log)
        thread.daemon = True
        thread.start()
    
    def manual_git_push(self):
        """手动推送Git"""
        self.logger.info("正在手动推送Git...")
        
        import threading
        
        def _manual_push():
            try:
                # 先添加所有更改
                success1, output1 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["add", "."]
                )
                
                if not success1:
                    self.logger.error(f"❌ Git添加失败: {output1}")
                    return
                
                # 提交
                import datetime
                commit_msg = f"手动推送: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                success2, output2 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["commit", "-m", commit_msg]
                )
                
                if not success2:
                    # 如果没有更改可提交
                    if "nothing to commit" in output2.lower():
                        self.logger.warning("⚠️ 没有需要提交的更改")
                    else:
                        self.logger.error(f"❌ Git提交失败: {output2}")
                        return
                
                # 推送
                success3, output3 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["push", "origin", "master"]
                )
                
                if success3:
                    self.logger.success("✅ 手动推送成功")
                    self.logger.info(output3)
                else:
                    self.logger.error(f"❌ 手动推送失败: {output3}")
                    
            except Exception as e:
                self.logger.error(f"手动推送异常: {str(e)}")
        
        thread = threading.Thread(target=_manual_push)
        thread.daemon = True
        thread.start()
    
    def diagnose_git_connection(self):
        """诊断Git连接问题"""
        self.logger.info("🔧 开始Git连接诊断...")
        
        import threading
        
        def _diagnose():
            try:
                self.logger.info("=" * 60)
                self.logger.info("Git连接问题诊断报告")
                self.logger.info("=" * 60)
                
                # 1. 测试网络连接
                self.logger.info("\n1. 测试网络连接...")
                success_ping, output_ping = self.deployment_manager.run_command(
                    "ping",
                    ["-n", "4", "github.com"]
                )
                
                if success_ping:
                    self.logger.success("✅ Ping测试成功")
                    # 提取延迟信息
                    if "平均" in output_ping:
                        for line in output_ping.split('\n'):
                            if "平均" in line:
                                self.logger.info(f"网络延迟: {line.strip()}")
                else:
                    self.logger.error("❌ Ping测试失败")
                    self.logger.warning("可能原因: 网络断开、DNS问题、防火墙阻止")
                
                # 2. 测试HTTPS连接
                self.logger.info("\n2. 测试HTTPS连接...")
                try:
                    import urllib.request
                    import urllib.error
                    import ssl
                    
                    # 创建不验证SSL的上下文（仅用于测试）
                    context = ssl._create_unverified_context()
                    req = urllib.request.Request("https://github.com", method="HEAD")
                    
                    try:
                        response = urllib.request.urlopen(req, timeout=10, context=context)
                        self.logger.success(f"✅ HTTPS连接成功 (状态码: {response.status})")
                    except urllib.error.URLError as e:
                        self.logger.error(f"❌ HTTPS连接失败: {str(e)}")
                except Exception as e:
                    self.logger.error(f"HTTPS测试异常: {str(e)}")
                
                # 3. 检查Git配置
                self.logger.info("\n3. 检查Git配置...")
                
                # 检查远程仓库
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.logger.info("远程仓库配置:")
                    self.logger.info(output_remote)
                else:
                    self.logger.error("❌ 无法获取远程仓库配置")
                
                # 检查代理设置
                success_proxy, output_proxy = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["config", "--global", "http.proxy"]
                )
                
                if success_proxy and output_proxy.strip():
                    self.logger.warning(f"⚠️ 检测到Git代理设置: {output_proxy.strip()}")
                else:
                    self.logger.success("✅ 无Git代理设置")
                
                # 4. 测试Git连接
                self.logger.info("\n4. 测试Git连接...")
                success_git, output_git = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["ls-remote", "https://github.com/juemin7-star/toothmen-docs.git", "--heads"]
                )
                
                if success_git:
                    self.logger.success("✅ Git连接成功")
                else:
                    self.logger.error("❌ Git连接失败")
                    self.logger.error(f"错误详情: {output_git}")
                    
                    # 分析错误类型
                    error_lower = output_git.lower()
                    if "permission denied" in error_lower or "authentication failed" in error_lower:
                        self.logger.warning("\n🔐 检测到认证问题:")
                        self.logger.info("  1. 检查SSH密钥配置")
                        self.logger.info("  2. 检查GitHub Token是否有效")
                        self.logger.info("  3. 检查远程仓库权限")
                    elif "connection" in error_lower or "timeout" in error_lower or "could not connect" in error_lower:
                        self.logger.warning("\n🌐 检测到网络连接问题:")
                        self.logger.info("  1. 检查网络连接")
                        self.logger.info("  2. 检查防火墙设置")
                        self.logger.info("  3. 尝试使用VPN或切换网络")
                    elif "proxy" in error_lower:
                        self.logger.warning("\n🔄 检测到代理问题:")
                        self.logger.info("  清除代理: git config --global --unset http.proxy")
                
                # 5. 检查本地提交状态
                self.logger.info("\n5. 检查本地提交状态...")
                
                # 获取最后提交
                success_log, output_log = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-1"]
                )
                
                if success_log:
                    self.logger.info(f"最后提交: {output_log.strip()}")
                else:
                    self.logger.warning("无法获取提交信息")
                
                # 检查未推送的提交
                success_unpushed, output_unpushed = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "origin/master..HEAD", "--oneline"]
                )
                
                if success_unpushed and output_unpushed.strip():
                    self.logger.warning("⚠️ 有未推送的提交:")
                    self.logger.info(output_unpushed)
                else:
                    self.logger.success("✅ 所有提交已推送或没有新提交")
                
                # 6. 提供解决方案
                self.logger.info("\n" + "=" * 60)
                self.logger.info("💡 解决方案建议:")
                self.logger.info("=" * 60)
                
                self.logger.info("\n🔹 如果HTTPS连接失败:")
                self.logger.info("  1. 切换到SSH方式（点击'切换到SSH'按钮）")
                self.logger.info("  2. 检查防火墙设置")
                self.logger.info("  3. 清除代理: git config --global --unset http.proxy")
                self.logger.info("  4. 尝试使用VPN或手机热点")
                
                self.logger.info("\n🔹 如果认证失败:")
                self.logger.info("  1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email\"")
                self.logger.info("  2. 添加公钥到GitHub")
                self.logger.info("  3. 测试SSH连接: ssh -T git@github.com")
                
                self.logger.info("\n🔹 立即操作:")
                self.logger.info("  1. 使用'切换到SSH'按钮")
                self.logger.info("  2. 使用'手动推送Git'按钮")
                self.logger.info("  3. 检查网络连接后重试")
                
                self.logger.success("\n✅ 诊断完成！")
                
            except Exception as e:
                self.logger.error(f"诊断过程中出现异常: {str(e)}")
        
        thread = threading.Thread(target=_diagnose)
        thread.daemon = True
        thread.start()
    
    def switch_to_ssh(self):
        """切换到SSH方式"""
        self.logger.info("⚡ 正在切换到SSH方式...")
        
        import threading
        
        def _switch_ssh():
            try:
                # 1. 显示当前配置
                self.logger.info("当前远程仓库配置:")
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.logger.info(output_remote)
                else:
                    self.logger.error("无法获取远程仓库配置")
                    return
                
                # 2. 切换到SSH
                self.logger.info("\n正在修改远程URL为SSH...")
                success_switch, output_switch = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "set-url", "origin", "git@github.com:juemin7-star/toothmen-docs.git"]
                )
                
                if success_switch:
                    self.logger.success("✅ 已切换到SSH方式")
                    
                    # 3. 显示新配置
                    self.logger.info("\n新的远程仓库配置:")
                    success_new, output_new = self.deployment_manager.run_command(
                        self.deployment_manager.git_path,
                        ["remote", "-v"]
                    )
                    
                    if success_new:
                        self.logger.info(output_new)
                    else:
                        self.logger.warning("无法获取新配置")
                    
                    # 4. 测试SSH连接
                    self.logger.info("\n测试SSH连接...")
                    success_test, output_test = self.deployment_manager.run_command(
                        "ssh",
                        ["-T", "git@github.com"]
                    )
                    
                    if success_test:
                        self.logger.success("✅ SSH连接成功")
                        self.logger.info(output_test)
                    else:
                        self.logger.warning("⚠️ SSH连接测试失败")
                        self.logger.info("可能需要设置SSH密钥:")
                        self.logger.info("  1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email\"")
                        self.logger.info("  2. 添加公钥到GitHub")
                        self.logger.info("  3. 启动ssh-agent: eval \"$(ssh-agent -s)\"")
                        self.logger.info("  4. 添加私钥: ssh-add ~/.ssh/id_ed25519")
                    
                    # 5. 询问是否立即推送
                    self.logger.info("\n💡 建议:")
                    self.logger.info("  现在可以使用'手动推送Git'按钮进行推送")
                    self.logger.info("  或稍后执行: git push origin master")
                    
                else:
                    self.logger.error(f"❌ 切换到SSH失败: {output_switch}")
                    
            except Exception as e:
                self.logger.error(f"切换到SSH过程中出现异常: {str(e)}")
        
        thread = threading.Thread(target=_switch_ssh)
        thread.daemon = True
        thread.start()
    
    def clear_npm_cache(self):
        """清除npm缓存"""
        self.logger.info("正在清除npm缓存...")
        
        import threading
        
        def _clear_cache():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.npm_path,
                    ["cache", "clean", "--force"]
                )
                
                if success:
                    self.logger.success("✅ npm缓存清除成功")
                    self.logger.info(output)
                else:
                    self.logger.error(f"❌ npm缓存清除失败: {output}")
                    
            except Exception as e:
                self.logger.error(f"清除npm缓存异常: {str(e)}")
        
        thread = threading.Thread(target=_clear_cache)
        thread.daemon = True
        thread.start()
    
    def check_config(self):
        """检查配置"""
        self.logger.info("正在检查配置...")
        
        try:
            # 使用主程序的config，而不是deployment_manager的config
            config = self.config
            
            self.logger.info("当前配置:")
            self.logger.info(f"项目路径: {config.get('project_path', '未设置')}")
            self.logger.info(f"docs文件夹: {config.get('docs_folder', '未设置')}")
            self.logger.info(f"npm路径: {config.get('npm_path', '未设置')}")
            self.logger.info(f"git路径: {config.get('git_path', '未设置')}")
            self.logger.info(f"侧边栏路径: {config.get('sidebars_path', '未设置')}")
            
            # 检查路径是否存在
            import os
            project_path = config.get('project_path', '')
            if project_path and os.path.exists(project_path):
                self.logger.success("✅ 项目路径存在")
                
                # 检查关键路径（相对于项目路径）
                project_dir = Path(project_path)
                
                # docs文件夹
                docs_folder_rel = config.get('docs_folder', '')
                if docs_folder_rel:
                    docs_folder_abs = project_dir / docs_folder_rel
                    if docs_folder_abs.exists():
                        self.logger.success(f"✅ docs文件夹存在: {docs_folder_abs}")
                    else:
                        self.logger.error(f"❌ docs文件夹不存在: {docs_folder_abs}")
                        self.logger.info(f"  相对路径: {docs_folder_rel}")
                else:
                    self.logger.error("❌ docs文件夹未设置")
                
                # 侧边栏文件
                sidebars_path_rel = config.get('sidebars_path', '')
                if sidebars_path_rel:
                    sidebars_path_abs = project_dir / sidebars_path_rel
                    if sidebars_path_abs.exists():
                        self.logger.success(f"✅ 侧边栏文件存在: {sidebars_path_abs}")
                        self.logger.info(f"  说明: 这是Docusaurus的侧边栏配置文件，用于自动生成文档导航")
                    else:
                        self.logger.error(f"❌ 侧边栏文件不存在: {sidebars_path_abs}")
                        self.logger.info(f"  相对路径: {sidebars_path_rel}")
                        self.logger.info(f"  说明: 这是Docusaurus的侧边栏配置文件，程序会自动创建")
                else:
                    self.logger.error("❌ 侧边栏文件未设置")
                
                # 检查文件夹分类配置
                folder_config = config.get('folder_classification', {})
                if folder_config:
                    self.logger.info("\n文件夹分类配置:")
                    reverse_folders = folder_config.get('reverse_order_folders', [])
                    if reverse_folders:
                        self.logger.info(f"倒序排序文件夹: {', '.join(reverse_folders)}")
                    else:
                        self.logger.warning("⚠️ 未配置倒序排序文件夹")
                    
                    sort_by_prefix = folder_config.get('sort_by_number_prefix', True)
                    self.logger.info(f"按数字前缀排序: {'是' if sort_by_prefix else '否'}")
                    
                    clean_prefix = folder_config.get('clean_number_prefix', True)
                    self.logger.info(f"清理数字前缀: {'是' if clean_prefix else '否'}")
                else:
                    self.logger.warning("⚠️ 未配置文件夹分类设置")
                
            else:
                self.logger.error(f"❌ 项目路径不存在: {project_path}")
                
        except Exception as e:
            self.logger.error(f"检查配置异常: {str(e)}")
    
    # ========== 部署流程控制方法 ==========
    
    def start_deployment_flow(self):
        """开始部署流程"""
        self.deployment_started = True
        self.deployment_step = 0
        
        # 禁用开始按钮，启用结束按钮
        self.btn_start_deploy.config(state="disabled")
        self.btn_end_deploy.config(state="normal")
        
        # 启用第一个部署步骤
        self.enable_deployment_step(0)
        
        self.logger.info("部署流程已开始，请按顺序执行步骤")
        self.logger.info("步骤1: 刷新文件结构 → 步骤2: 生成侧边栏 → 步骤3: 本地构建测试 → 步骤4: 本地预览 → 步骤5: 自动部署")
    
    def end_deployment_flow(self):
        """结束部署流程"""
        self.deployment_started = False
        
        # 启用开始按钮，禁用结束按钮
        self.btn_start_deploy.config(state="normal")
        self.btn_end_deploy.config(state="disabled")
        
        # 禁用所有步骤按钮
        for i in range(len(self.deployment_buttons)):
            self.disable_deployment_step(i)
        
        self.logger.info("部署流程已结束")
    
    def enable_deployment_step(self, step_index):
        """启用指定步骤的按钮"""
        if 0 <= step_index < len(self.deployment_buttons):
            button_name = self.deployment_buttons[step_index][0]
            button = getattr(self, f"btn_{button_name.replace(' ', '_')}")
            button.config(state="normal")
    
    def disable_deployment_step(self, step_index):
        """禁用指定步骤的按钮"""
        if 0 <= step_index < len(self.deployment_buttons):
            button_name = self.deployment_buttons[step_index][0]
            button = getattr(self, f"btn_{button_name.replace(' ', '_')}")
            button.config(state="disabled")
    
    def next_deployment_step(self):
        """进入下一个部署步骤"""
        if self.deployment_started and self.deployment_step < len(self.deployment_buttons) - 1:
            # 禁用当前步骤
            self.disable_deployment_step(self.deployment_step)
            
            # 启用下一个步骤
            self.deployment_step += 1
            self.enable_deployment_step(self.deployment_step)
            
            self.logger.info(f"已解锁步骤 {self.deployment_step+1}: {self.deployment_buttons[self.deployment_step][0]}")
    
    def update_button_state(self, button_name, state):
        """更新按钮状态"""
        # 获取按钮对象
        button_attr_name = button_name.replace(' ', '_')
        button = getattr(self, f"btn_{button_attr_name}")
        
        colors = {
            "normal": ("SystemButtonFace", "black"),
            "running": ("yellow", "black"),
            "success": ("green", "white"),
            "error": ("red", "white")
        }
        
        bg_color, fg_color = colors.get(state, colors["normal"])
        
        # 更新按钮颜色
        button.config(background=bg_color, foreground=fg_color)
        
        # 如果是成功状态，解锁下一个步骤
        if state == "success" and self.deployment_started:
            # 找到当前按钮的索引
            for i, (name, _, _) in enumerate(self.deployment_buttons):
                if name == button_name:
                    # 如果是自动部署成功，2秒后结束流程
                    if button_name == "自动部署":
                        self.root.after(2000, self.end_deployment_flow)
                    else:
                        # 解锁下一个步骤
                        self.root.after(1000, self.next_deployment_step)
                    break
            
            # 3秒后恢复颜色
            self.root.after(3000, lambda: button.config(
                background=colors["normal"][0],
                foreground=colors["normal"][1]
            ))
        
        # 如果是错误状态，3秒后恢复颜色
        elif state == "error":
            self.root.after(3000, lambda: button.config(
                background=colors["normal"][0],
                foreground=colors["normal"][1]
            ))

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()