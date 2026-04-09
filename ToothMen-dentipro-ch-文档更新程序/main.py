#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 - 主程序
功能：双文件夹文件管理 + 自动化部署工作流
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import json
import threading
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# 导入自定义模块
from file_manager import FileManager
from deployment_manager import DeploymentManager
from logger import Logger
from mdx_checker import MDXChecker

class ToothMenDocsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v1.0")
        self.root.geometry("1400x1000")
        
        # 设置图标
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # 项目路径
        self.project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
        self.test_folder = self.project_path / "docs-测试中转"
        self.prod_folder = self.project_path / "docs"
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 创建测试中转文件夹（如果不存在）
        self.test_folder.mkdir(exist_ok=True)
        
        # 初始化管理器
        self.file_manager = FileManager(self.test_folder, self.prod_folder)
        self.deployment_manager = DeploymentManager(self.project_path)
        self.logger = Logger()
        
        # 加载配置
        self.config = self.load_config()
        
        # 创建UI
        self.create_widgets()
        
        # 初始加载文件列表
        self.refresh_file_lists()
        
        # 启动文件监控
        self.start_file_monitoring()
        
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
                "test_folder": str(self.test_folder),
                "prod_folder": str(self.prod_folder),
                "sidebars_path": str(self.sidebars_path),
                "npm_path": "npm",
                "git_path": r"C:\Program Files\Git\cmd\git.exe",
                "auto_refresh": True,
                "log_level": "INFO"
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重 - 让日志区域占用更多空间
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # 标题行
        main_frame.rowconfigure(1, weight=1)  # 文件管理区域
        main_frame.rowconfigure(2, weight=0)  # 部署工作流区域
        main_frame.rowconfigure(3, weight=2)  # 日志区域（更多权重）
        
        # 创建顶部标题
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 创建文件管理区域
        self.create_file_management_area(main_frame)
        
        # 创建部署工作流区域
        self.create_deployment_area(main_frame)
        
        # 创建日志区域
        self.create_log_area(main_frame)
        
    def create_file_management_area(self, parent):
        """创建文件管理区域"""
        # 文件管理框架
        file_frame = ttk.LabelFrame(parent, text="文件管理", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=2)  # 左侧文件夹（变窄）
        file_frame.columnconfigure(1, weight=0)  # 按钮框（固定宽度）
        file_frame.columnconfigure(2, weight=3)  # 右侧文件夹（保持原宽度）
        file_frame.rowconfigure(0, weight=1)
        
        # 左侧：测试中转文件夹（变窄）
        left_frame = ttk.Frame(file_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # 左侧标题和按钮
        left_header = ttk.Frame(left_frame)
        left_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(left_header, text="测试中转文件夹", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(left_header)
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="新建", width=8, command=self.create_new_file,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="删除", width=8, command=self.delete_selected_file,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="重命名", width=8, command=self.rename_selected_file,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="刷新", width=8, command=self.refresh_file_lists,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        
        # 左侧文件列表
        left_list_frame = ttk.Frame(left_frame)
        left_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_list_frame.columnconfigure(0, weight=1)
        left_list_frame.rowconfigure(0, weight=1)
        
        self.left_listbox = tk.Listbox(left_list_frame, selectmode=tk.SINGLE, 
                                      font=("Consolas", 10), height=15, width=30)  # 设置固定宽度
        self.left_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        left_scrollbar = ttk.Scrollbar(left_list_frame, orient=tk.VERTICAL, 
                                      command=self.left_listbox.yview)
        left_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.left_listbox.config(yscrollcommand=left_scrollbar.set)
        
        # 绑定双击事件
        self.left_listbox.bind('<Double-Button-1>', self.open_file_editor)
        
        # 中间：按钮框（与左右文件框高度中央对齐）
        button_box = ttk.LabelFrame(file_frame, text="文件操作", padding="10")
        button_box.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10)
        
        # 使用网格布局确保按钮垂直居中
        button_box.rowconfigure(0, weight=1)
        button_box.rowconfigure(1, weight=0)
        button_box.rowconfigure(2, weight=0)
        button_box.rowconfigure(3, weight=0)
        button_box.rowconfigure(4, weight=0)
        button_box.rowconfigure(5, weight=1)
        
        # 上移按钮
        tk.Button(button_box, text="↑", width=5,
                 command=self.move_up,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).grid(row=1, column=0, pady=5)
        
        # 下移按钮
        tk.Button(button_box, text="↓", width=5,
                 command=self.move_down,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).grid(row=2, column=0, pady=5)
        
        # 分隔线
        ttk.Separator(button_box, orient='horizontal').grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 右移按钮
        tk.Button(button_box, text="→", width=5, 
                 command=self.move_to_prod,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).grid(row=4, column=0, pady=5)
        
        # 左移按钮
        tk.Button(button_box, text="←", width=5, 
                 command=self.move_to_test,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).grid(row=5, column=0, pady=5)
        
        # 右侧：生产文件夹
        right_frame = ttk.Frame(file_frame)
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 右侧标题
        right_header = ttk.Frame(right_frame)
        right_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(right_header, text="生产文件夹", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # 右侧文件列表（支持拖拽排序）
        right_list_frame = ttk.Frame(right_frame)
        right_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_list_frame.columnconfigure(0, weight=1)
        right_list_frame.rowconfigure(0, weight=1)
        
        self.right_listbox = tk.Listbox(right_list_frame, selectmode=tk.SINGLE,
                                       font=("Consolas", 10), height=15, width=40)  # 设置固定宽度
        self.right_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        right_scrollbar = ttk.Scrollbar(right_list_frame, orient=tk.VERTICAL,
                                       command=self.right_listbox.yview)
        right_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.right_listbox.config(yscrollcommand=right_scrollbar.set)
        
        # 绑定双击事件
        self.right_listbox.bind('<Double-Button-1>', self.open_file_editor)
        
        # 绑定拖拽事件（用于排序）
        self.right_listbox.bind('<ButtonPress-1>', self.on_drag_start)
        self.right_listbox.bind('<B1-Motion>', self.on_drag_motion)
        self.right_listbox.bind('<ButtonRelease-1>', self.on_drag_release)
        
    def create_deployment_area(self, parent):
        """创建部署工作流区域"""
        # 部署框架
        deploy_frame = ttk.LabelFrame(parent, text="部署工作流", padding="10")
        deploy_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ========== 第一行：独立功能按钮 ==========
        top_control_frame = ttk.Frame(deploy_frame)
        top_control_frame.grid(row=0, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # MDX检测按钮（独立，一直可用）
        self.btn_mdx_check = tk.Button(top_control_frame, text="🔍 检测MDX语法&更新侧边栏", 
                                      command=self.check_mdx_and_update_sidebars, width=29,
                                      bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_mdx_check.pack(side=tk.LEFT, padx=8)
        
        # 开始部署流程按钮
        self.btn_start = tk.Button(top_control_frame, text="▶ 开始部署流程", 
                                  command=self.start_deployment_flow, width=15,
                                  bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_start.pack(side=tk.LEFT, padx=8)
        
        # 结束流程按钮
        self.btn_end = tk.Button(top_control_frame, text="■ 结束流程", 
                                command=self.end_deployment_flow, width=15, state="disabled",
                                bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_end.pack(side=tk.LEFT, padx=8)
        
        # 验证部署按钮（独立，一直可用）
        self.btn_verify = tk.Button(top_control_frame, text="🌐 验证部署", 
                                   command=self.verify_deployment, width=15,
                                   bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_verify.pack(side=tk.LEFT, padx=8)
        
        # 分隔线
        ttk.Separator(deploy_frame, orient='horizontal').grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=10)
        
        # ========== 第二行：部署流程按钮（点击开始后激活） ==========
        # 部署步骤按钮（点击"开始部署流程"后激活）
        self.deployment_buttons = [
            ("本地构建测试", self.local_build_test, "执行npm run build测试构建"),
            ("本地预览", self.local_preview, "启动本地开发服务器预览"),
            ("确认预览", self.confirm_preview, "手动确认本地预览成功"),
            ("自动部署", self.auto_deploy, "执行Git推送和Cloudflare部署"),
        ]
        
        # 创建部署步骤按钮
        for i, (text, command, tooltip) in enumerate(self.deployment_buttons):
            # 所有部署按钮默认禁用，点击"开始部署流程"后激活
            btn = tk.Button(deploy_frame, text=text, command=command, width=15, state="disabled",
                          bg="SystemButtonFace", fg="black", relief="raised", bd=2)
            # 增加按钮间距，使布局更均匀
            btn.grid(row=2, column=i, padx=8, pady=5)
            
            # 添加工具提示
            self.create_tooltip(btn, tooltip)
            
            # 存储按钮引用以便更新状态
            setattr(self, f"btn_{text.replace(' ', '_')}", btn)
        
        # 初始化部署状态
        self.deployment_step = 0  # 当前步骤索引
        self.deployment_started = False  # 是否开始部署流程
    
    def create_log_area(self, parent):
        """创建日志区域"""
        # 日志框架
        log_frame = ttk.LabelFrame(parent, text="执行日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=("Consolas", 9),
                                                 height=35)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        tk.Button(log_control_frame, text="清空日志", 
                 command=self.clear_log,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        tk.Button(log_control_frame, text="保存日志", 
                 command=self.save_log,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        tk.Button(log_control_frame, text="复制日志", 
                 command=self.copy_log,
                 bg="SystemButtonFace", fg="black", relief="raised", bd=2).pack(side=tk.LEFT, padx=2)
        
        # 调试面板框架
        debug_frame = ttk.LabelFrame(parent, text="🔧 调试工具", padding="10")
        debug_frame.grid(row=3, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
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
            ("📁 打开项目文件夹", self.open_project_folder),
            ("⚙️ 检查配置", self.check_config),
            ("📋 复制错误信息", self.copy_error_info),
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
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    # ========== 文件管理方法 ==========
    
    def refresh_file_lists(self):
        """刷新文件列表"""
        try:
            # 清空列表
            self.left_listbox.delete(0, tk.END)
            self.right_listbox.delete(0, tk.END)
            
            # 获取文件列表
            test_files = self.file_manager.get_test_files()
            prod_files = self.file_manager.get_prod_files()
            
            # 添加到列表
            for file in test_files:
                self.left_listbox.insert(tk.END, file.name)
            
            for file in prod_files:
                self.right_listbox.insert(tk.END, file.name)
            
            self.log("文件列表已刷新", "INFO")
            
        except Exception as e:
            self.log(f"刷新文件列表失败: {str(e)}", "ERROR")
    
    def create_new_file(self):
        """创建新文件"""
        # 获取文件名
        filename = tk.simpledialog.askstring("新建文件", "请输入文件名（不含扩展名）:")
        if not filename:
            return
        
        # 确保以.mdx结尾
        if not filename.endswith('.mdx'):
            filename += '.mdx'
        
        # 创建文件
        try:
            file_path = self.test_folder / filename
            
            if file_path.exists():
                messagebox.showerror("错误", f"文件 {filename} 已存在！")
                return
            
            # 创建带有frontmatter的模板文件
            template = f"""---
title: {filename.replace('.mdx', '')}
description: 文档描述
sidebar_position: 1
---

# {filename.replace('.mdx', '')}

开始编写您的文档内容...

## 章节标题

文档内容...
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            self.log(f"已创建文件: {filename}", "SUCCESS")
            self.refresh_file_lists()
            
            # 自动打开编辑
            self.open_file(file_path)
            
        except Exception as e:
            self.log(f"创建文件失败: {str(e)}", "ERROR")
    
    def delete_selected_file(self):
        """删除选中的文件"""
        # 检查选中了哪个列表
        selected_left = self.left_listbox.curselection()
        selected_right = self.right_listbox.curselection()
        
        if selected_left:
            # 删除测试文件
            filename = self.left_listbox.get(selected_left[0])
            file_path = self.test_folder / filename
            
            if messagebox.askyesno("确认删除", f"确定要删除文件 {filename} 吗？"):
                try:
                    file_path.unlink()
                    self.log(f"已删除文件: {filename}", "SUCCESS")
                    self.refresh_file_lists()
                except Exception as e:
                    self.log(f"删除文件失败: {str(e)}", "ERROR")
        
        elif selected_right:
            # 不能直接删除生产文件
            messagebox.showwarning("警告", "生产文件夹中的文件不能直接删除！请先移动到测试文件夹。")
    
    def rename_selected_file(self):
        """重命名选中的文件"""
        selected_left = self.left_listbox.curselection()
        
        if not selected_left:
            messagebox.showinfo("提示", "请先在测试文件夹中选择要重命名的文件")
            return
        
        old_name = self.left_listbox.get(selected_left[0])
        old_path = self.test_folder / old_name
        
        new_name = tk.simpledialog.askstring("重命名文件", 
                                           f"请输入新文件名（当前: {old_name}）:")
        if not new_name:
            return
        
        # 确保以.mdx结尾
        if not new_name.endswith('.mdx'):
            new_name += '.mdx'
        
        new_path = self.test_folder / new_name
        
        try:
            if new_path.exists():
                messagebox.showerror("错误", f"文件 {new_name} 已存在！")
                return
            
            old_path.rename(new_path)
            self.log(f"已重命名: {old_name} → {new_name}", "SUCCESS")
            self.refresh_file_lists()
            
        except Exception as e:
            self.log(f"重命名失败: {str(e)}", "ERROR")
    
    def move_to_prod(self):
        """将文件从测试移动到生产"""
        selected_left = self.left_listbox.curselection()
        
        if not selected_left:
            messagebox.showinfo("提示", "请先在测试文件夹中选择要移动的文件")
            return
        
        filename = self.left_listbox.get(selected_left[0])
        src_path = self.test_folder / filename
        dst_path = self.prod_folder / filename
        
        try:
            # 移动文件
            shutil.move(str(src_path), str(dst_path))
            self.log(f"已移动文件到生产: {filename}", "SUCCESS")
            self.refresh_file_lists()
            
        except Exception as e:
            self.log(f"移动文件失败: {str(e)}", "ERROR")
    
    def move_up(self):
        """将选中的文件上移一位"""
        selected = self.right_listbox.curselection()
        
        if not selected:
            messagebox.showinfo("提示", "请先在生产文件夹中选择要上移的文件")
            return
        
        index = selected[0]
        if index == 0:
            messagebox.showinfo("提示", "文件已在最顶部，无法上移")
            return
        
        try:
            # 获取当前列表
            items = list(self.right_listbox.get(0, tk.END))
            
            # 交换位置
            items[index], items[index-1] = items[index-1], items[index]
            
            # 更新列表
            self.right_listbox.delete(0, tk.END)
            for item in items:
                self.right_listbox.insert(tk.END, item)
            
            # 重新选择移动后的项目
            self.right_listbox.selection_set(index-1)
            
            # 保存新的顺序
            self.save_file_order()
            
            self.log(f"文件上移成功: {items[index]}", "SUCCESS")
            
        except Exception as e:
            self.log(f"文件上移失败: {str(e)}", "ERROR")
    
    def move_down(self):
        """将选中的文件下移一位"""
        selected = self.right_listbox.curselection()
        
        if not selected:
            messagebox.showinfo("提示", "请先在生产文件夹中选择要下移的文件")
            return
        
        index = selected[0]
        total_items = self.right_listbox.size()
        
        if index == total_items - 1:
            messagebox.showinfo("提示", "文件已在最底部，无法下移")
            return
        
        try:
            # 获取当前列表
            items = list(self.right_listbox.get(0, tk.END))
            
            # 交换位置
            items[index], items[index+1] = items[index+1], items[index]
            
            # 更新列表
            self.right_listbox.delete(0, tk.END)
            for item in items:
                self.right_listbox.insert(tk.END, item)
            
            # 重新选择移动后的项目
            self.right_listbox.selection_set(index+1)
            
            # 保存新的顺序
            self.save_file_order()
            
            self.log(f"文件下移成功: {items[index]}", "SUCCESS")
            
        except Exception as e:
            self.log(f"文件下移失败: {str(e)}", "ERROR")
    
    def move_to_test(self):
        """将文件从生产移动到测试"""
        selected_right = self.right_listbox.curselection()
        
        if not selected_right:
            messagebox.showinfo("提示", "请先在生产文件夹中选择要移动的文件")
            return
        
        filename = self.right_listbox.get(selected_right[0])
        src_path = self.prod_folder / filename
        dst_path = self.test_folder / filename
        
        try:
            # 移动文件
            shutil.move(str(src_path), str(dst_path))
            self.log(f"已移动文件到测试: {filename}", "SUCCESS")
            self.refresh_file_lists()
            
        except Exception as e:
            self.log(f"移动文件失败: {str(e)}", "ERROR")
    
    def open_file_editor(self, event):
        """打开文件编辑器"""
        # 确定是哪个列表
        widget = event.widget
        
        if widget == self.left_listbox:
            selected = self.left_listbox.curselection()
            if selected:
                filename = self.left_listbox.get(selected[0])
                file_path = self.test_folder / filename
                self.open_file(file_path)
        
        elif widget == self.right_listbox:
            selected = self.right_listbox.curselection()
            if selected:
                filename = self.right_listbox.get(selected[0])
                file_path = self.prod_folder / filename
                self.open_file(file_path)
    
    def open_file(self, file_path):
        """用系统默认程序打开文件"""
        try:
            os.startfile(str(file_path))
            self.log(f"已打开文件: {file_path.name}", "INFO")
        except Exception as e:
            self.log(f"打开文件失败: {str(e)}", "ERROR")
    
    # ========== 拖拽排序方法 ==========
    
    def on_drag_start(self, event):
        """开始拖拽"""
        widget = event.widget
        self.drag_start_index = widget.nearest(event.y)
        widget.selection_clear(0, tk.END)
        widget.selection_set(self.drag_start_index)
    
    def on_drag_motion(self, event):
        """拖拽移动"""
        widget = event.widget
        index = widget.nearest(event.y)
        
        if index != self.drag_start_index:
            # 交换项目
            items = list(widget.get(0, tk.END))
            items[self.drag_start_index], items[index] = items[index], items[self.drag_start_index]
            
            # 更新列表
            widget.delete(0, tk.END)
            for item in items:
                widget.insert(tk.END, item)
            
            widget.selection_clear(0, tk.END)
            widget.selection_set(index)
            self.drag_start_index = index
    
    def on_drag_release(self, event):
        """拖拽释放"""
        # 保存新的顺序
        self.save_file_order()
    
    def save_file_order(self):
        """保存文件顺序"""
        try:
            # 获取当前顺序
            items = list(self.right_listbox.get(0, tk.END))
            
            # 更新文件管理器中的顺序
            self.file_manager.update_prod_order(items)
            
            self.log("文件顺序已保存", "INFO")
            
        except Exception as e:
            self.log(f"保存文件顺序失败: {str(e)}", "ERROR")
    
    # ========== 部署工作流方法 ==========
    
    def check_mdx_syntax(self):
        """检测MDX语法"""
        try:
            # 更新按钮状态为运行中
            self.update_button_state("🔍 检测MDX语法", "running")
            self.log("[MDX] 开始检测MDX文件语法...", "INFO")
            
            # 创建MDX检测器
            mdx_checker = MDXChecker(self.prod_folder)
            
            # 执行检测
            results = mdx_checker.check_all_mdx_files()
            
            # 生成报告
            report = mdx_checker.format_report(results)
            
            # 记录报告
            self.log(report, "INFO")
            
            if results:
                self.log("[WARNING] 检测到MDX语法问题，建议修复后再更新侧边栏", "WARNING")
                # 更新按钮状态为错误
                self.update_button_state("🔍 检测MDX语法", "error")
                
                # 提供修复建议
                for file_path, issues in results.items():
                    suggestions = mdx_checker.get_fix_suggestions(issues)
                    for suggestion in suggestions:
                        self.log(f"[SUGGESTION] {suggestion}", "INFO")
                
                # 询问是否继续
                response = messagebox.askyesno(
                    "MDX语法检测结果",
                    f"检测到 {len(results)} 个文件存在语法问题。\n\n是否继续更新侧边栏？\n\n建议：修复问题后再继续。"
                )
                
                if response:
                    self.log("[INFO] 用户选择继续更新侧边栏", "INFO")
                    # 重置按钮状态
                    self.update_button_state("🔍 检测MDX语法", "normal")
                    self.update_sidebars(skip_check=True)
                else:
                    self.log("[INFO] 用户选择先修复MDX语法问题", "INFO")
                    # 重置按钮状态
                    self.update_button_state("🔍 检测MDX语法", "normal")
            else:
                self.log("[SUCCESS] 所有MDX文件语法检查通过，可以安全更新侧边栏", "SUCCESS")
                # 更新按钮状态为成功
                self.update_button_state("🔍 检测MDX语法", "success")
                # 询问用户是否继续更新侧边栏
                response = messagebox.askyesno(
                    "MDX语法检测通过",
                    "所有MDX文件语法检查通过，可以安全更新侧边栏。\n\n是否立即更新侧边栏？"
                )
                
                if response:
                    self.log("[INFO] 用户选择立即更新侧边栏", "INFO")
                    self.update_sidebars(skip_check=True)
                else:
                    self.log("[INFO] 用户选择稍后更新侧边栏", "INFO")
                    # 重置按钮状态
                    self.update_button_state("🔍 检测MDX语法", "normal")
                
        except Exception as e:
            self.log(f"[ERROR] MDX语法检测失败: {str(e)}", "ERROR")
            # 更新按钮状态为错误
            self.update_button_state("🔍 检测MDX语法&更新侧边栏", "error")
    
    def check_mdx_and_update_sidebars(self):
        """检测MDX语法并自动更新侧边栏"""
        try:
            # 更新按钮状态为运行中
            self.update_button_state("🔍 检测MDX语法&更新侧边栏", "running")
            self.log("[MDX] 开始检测MDX文件语法并更新侧边栏...", "INFO")
            
            # 创建MDX检测器
            mdx_checker = MDXChecker(self.prod_folder)
            
            # 执行检测
            results = mdx_checker.check_all_mdx_files()
            
            # 生成报告
            report = mdx_checker.format_report(results)
            
            # 记录报告
            self.log(report, "INFO")
            
            if results:
                self.log("[ERROR] 检测到MDX语法问题，停止更新侧边栏", "ERROR")
                # 更新按钮状态为错误
                self.update_button_state("🔍 检测MDX语法&更新侧边栏", "error")
                
                # 提供修复建议
                for file_path, issues in results.items():
                    suggestions = mdx_checker.get_fix_suggestions(issues)
                    for suggestion in suggestions:
                        self.log(f"[SUGGESTION] {suggestion}", "INFO")
                
                # 显示错误消息
                messagebox.showerror(
                    "MDX语法检测失败",
                    f"检测到 {len(results)} 个文件存在语法问题。\n\n请先修复MDX语法问题，然后再尝试更新侧边栏。"
                )
                
                # 重置按钮状态
                self.update_button_state("🔍 检测MDX语法&更新侧边栏", "normal")
            else:
                self.log("[SUCCESS] 所有MDX文件语法检查通过，开始更新侧边栏...", "SUCCESS")
                
                # 自动更新侧边栏
                self._update_sidebars_directly()
                
        except Exception as e:
            self.log(f"[ERROR] MDX语法检测并更新侧边栏失败: {str(e)}", "ERROR")
            # 更新按钮状态为错误
            self.update_button_state("🔍 检测MDX语法&更新侧边栏", "error")
    
    def _update_sidebars_directly(self):
        """直接更新侧边栏（不进行语法检测）"""
        try:
            # 在后台线程中执行，传递None让部署管理器自动获取实际文件
            thread = threading.Thread(target=self._update_sidebars_thread, args=(None,))
            thread.daemon = True
            thread.start()
            
            # 更新按钮状态
            self.update_button_state("🔍 检测MDX语法&更新侧边栏", "running")
            
        except Exception as e:
            self.log(f"更新侧边栏失败: {str(e)}", "ERROR")
            self.update_button_state("🔍 检测MDX语法&更新侧边栏", "error")
    
    def update_sidebars(self, skip_check=False):
        """
        更新侧边栏（已合并到检测MDX语法&更新侧边栏按钮）
        
        Args:
            skip_check: 是否跳过MDX语法检测（默认False）
        """
        try:
            # 显示提示信息，引导用户使用合并按钮
            self.log("[INFO] '更新侧边栏'功能已合并到'🔍 检测MDX语法&更新侧边栏'按钮", "INFO")
            self.log("[INFO] 请使用'🔍 检测MDX语法&更新侧边栏'按钮进行完整流程", "INFO")
            
            # 询问用户是否要使用合并按钮
            response = messagebox.askyesno(
                "功能已合并",
                "'更新侧边栏'功能已合并到'🔍 检测MDX语法&更新侧边栏'按钮。\n\n是否立即使用合并按钮执行完整流程？"
            )
            
            if response:
                self.log("[INFO] 用户选择使用合并按钮", "INFO")
                self.check_mdx_and_update_sidebars()
            else:
                self.log("[INFO] 用户取消操作", "INFO")
                
        except Exception as e:
            self.log(f"更新侧边栏失败: {str(e)}", "ERROR")
    
    def _update_sidebars_thread(self, prod_files):
        """更新侧边栏的线程函数"""
        try:
            success, message = self.deployment_manager.update_sidebars(prod_files)
            
            if success:
                self.log(message, "SUCCESS")
                # 更新合并按钮的状态
                self.update_button_state("🔍 检测MDX语法&更新侧边栏", "success")
            else:
                self.log(message, "ERROR")
                # 更新合并按钮的状态
                self.update_button_state("🔍 检测MDX语法&更新侧边栏", "error")
                
        except Exception as e:
            self.log(f"侧边栏更新异常: {str(e)}", "ERROR")
            # 更新合并按钮的状态
            self.update_button_state("🔍 检测MDX语法&更新侧边栏", "error")
    
    def local_build_test(self):
        """本地构建测试"""
        try:
            thread = threading.Thread(target=self._local_build_test_thread)
            thread.daemon = True
            thread.start()
            
            self.update_button_state("本地构建测试", "running")
            
        except Exception as e:
            self.log(f"启动构建测试失败: {str(e)}", "ERROR")
            self.update_button_state("本地构建测试", "error")
    
    def _local_build_test_thread(self):
        """本地构建测试的线程函数"""
        try:
            # 显示构建过程开始
            self.log("正在执行本地构建测试，请稍后...", "INFO")
            self.log("步骤1: 清除缓存...", "INFO")
            
            success, output = self.deployment_manager.local_build_test()
            
            if success:
                self.log("本地构建测试成功", "SUCCESS")
                self.update_button_state("本地构建测试", "success")
            else:
                self.log(f"本地构建测试失败:\n{output}", "ERROR")
                self.update_button_state("本地构建测试", "error")
                
        except Exception as e:
            self.log(f"构建测试异常: {str(e)}", "ERROR")
            self.update_button_state("本地构建测试", "error")
    
    def local_preview(self):
        """本地预览"""
        try:
            thread = threading.Thread(target=self._local_preview_thread)
            thread.daemon = True
            thread.start()
            
            self.update_button_state("本地预览", "running")
            
        except Exception as e:
            self.log(f"启动本地预览失败: {str(e)}", "ERROR")
            self.update_button_state("本地预览", "error")
    
    def _local_preview_thread(self):
        """本地预览的线程函数"""
        try:
            success, output = self.deployment_manager.local_preview()
            
            if success:
                self.log(output, "SUCCESS")
                self.update_button_state("本地预览", "success")
                
                # 延迟3秒后自动打开浏览器
                self.log("服务器已启动，3秒后自动打开浏览器...", "INFO")
                self.root.after(3000, self.open_local_preview)
                
            else:
                self.log(f"本地预览启动失败:\n{output}", "ERROR")
                self.update_button_state("本地预览", "error")
                
        except Exception as e:
            self.log(f"本地预览异常: {str(e)}", "ERROR")
            self.update_button_state("本地预览", "error")
    
    def auto_deploy(self):
        """自动部署"""
        try:
            thread = threading.Thread(target=self._auto_deploy_thread)
            thread.daemon = True
            thread.start()
            
            self.update_button_state("自动部署", "running")
            
        except Exception as e:
            self.log(f"启动自动部署失败: {str(e)}", "ERROR")
            self.update_button_state("自动部署", "error")
    
    def _auto_deploy_thread(self):
        """自动部署的线程函数"""
        try:
            success, output = self.deployment_manager.auto_deploy()
            
            if success:
                self.log("自动部署成功", "SUCCESS")
                self.update_button_state("自动部署", "success")
            else:
                self.log(f"自动部署失败:\n{output}", "ERROR")
                self.update_button_state("自动部署", "error")
                
        except Exception as e:
            self.log(f"自动部署异常: {str(e)}", "ERROR")
            self.update_button_state("自动部署", "error")
    
    def verify_deployment(self):
        """验证部署结果（打开公网文档网站）"""
        try:
            # 更新按钮状态为运行中
            self.btn_verify.config(bg="yellow", fg="black", state="normal")
            
            # 打开公网文档网站
            import webbrowser
            website_url = "https://docs.toothmen.com"
            webbrowser.open(website_url)
            
            self.log(f"已打开公网文档网站: {website_url}", "SUCCESS")
            self.log("⚠️ 重要提示：Cloudflare缓存说明", "WARNING")
            self.log("1. Cloudflare CDN会缓存内容15-30分钟", "INFO")
            self.log("2. 您可能看到旧版本，这是正常的", "INFO")
            self.log("3. 等待15-30分钟后刷新浏览器即可看到新内容", "INFO")
            self.log("4. 或者手动清除Cloudflare缓存（需要账户权限）", "INFO")
            self.log("5. 当前部署已成功，缓存会自动刷新", "SUCCESS")
            
            # 更新按钮状态为成功
            self.btn_verify.config(bg="green", fg="white", state="normal")
            
            # 2秒后恢复原状
            self.root.after(2000, lambda: self.btn_verify.config(
                bg="SystemButtonFace", fg="black", state="normal"))
            
        except Exception as e:
            self.log(f"验证部署失败: {str(e)}", "ERROR")
            # 更新按钮状态为错误
            self.btn_verify.config(bg="red", fg="white", state="normal")
            
            # 2秒后恢复原状
            self.root.after(2000, lambda: self.btn_verify.config(
                bg="SystemButtonFace", fg="black", state="normal"))
    
    def open_local_preview(self):
        """自动打开本地预览页面"""
        try:
            import webbrowser
            # 打开主页，而不是具体的文档链接
            url = "http://localhost:3000"
            webbrowser.open(url)
            
            self.log(f"已自动打开浏览器访问: {url}", "SUCCESS")
            self.log("注意：如果显示404，请清除浏览器缓存或使用无痕模式", "INFO")
            
        except Exception as e:
            self.log(f"自动打开浏览器失败: {str(e)}", "ERROR")
            self.log("请手动访问 http://localhost:3000", "INFO")
    
    # ==================== 调试工具方法 ====================
    
    def test_network_connection(self):
        """测试网络连接"""
        self.log("正在测试网络连接...", "INFO")
        
        import subprocess
        import threading
        
        def _test_network():
            try:
                # 测试ping GitHub
                self.log("测试ping github.com...", "INFO")
                result = subprocess.run(
                    ["ping", "-n", "4", "github.com"],
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
                
                if result.returncode == 0:
                    self.log("✅ Ping测试成功", "SUCCESS")
                    # 提取关键信息
                    for line in result.stdout.split('\n'):
                        if "数据包:" in line or "Packets:" in line:
                            self.log(f"网络状态: {line.strip()}", "INFO")
                        if "平均 =" in line or "Average =" in line:
                            self.log(f"网络延迟: {line.strip()}", "INFO")
                else:
                    self.log("❌ Ping测试失败", "ERROR")
                    self.log(f"错误信息: {result.stderr}", "ERROR")
                
                # 测试HTTPS访问
                self.log("测试HTTPS访问...", "INFO")
                import urllib.request
                try:
                    response = urllib.request.urlopen("https://github.com", timeout=10)
                    self.log(f"✅ HTTPS访问成功 (状态码: {response.status})", "SUCCESS")
                except Exception as e:
                    self.log(f"❌ HTTPS访问失败: {str(e)}", "ERROR")
                    
            except Exception as e:
                self.log(f"网络测试异常: {str(e)}", "ERROR")
        
        # 在新线程中执行网络测试
        thread = threading.Thread(target=_test_network)
        thread.daemon = True
        thread.start()
    
    def check_git_status(self):
        """检查Git状态"""
        self.log("正在检查Git状态...", "INFO")
        
        import threading
        
        def _check_git():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["status", "--short"]
                )
                
                if success:
                    if output.strip():
                        self.log("Git状态:", "INFO")
                        self.log(output, "INFO")
                    else:
                        self.log("✅ 工作区干净，没有未提交的更改", "SUCCESS")
                else:
                    self.log(f"❌ Git状态检查失败: {output}", "ERROR")
                    
            except Exception as e:
                self.log(f"Git状态检查异常: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_check_git)
        thread.daemon = True
        thread.start()
    
    def show_git_log(self):
        """查看Git日志"""
        self.log("正在获取Git提交历史...", "INFO")
        
        import threading
        
        def _show_log():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-10"]
                )
                
                if success:
                    self.log("最近10次提交:", "INFO")
                    self.log(output, "INFO")
                else:
                    self.log(f"❌ 获取Git日志失败: {output}", "ERROR")
                    
            except Exception as e:
                self.log(f"获取Git日志异常: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_show_log)
        thread.daemon = True
        thread.start()
    
    def manual_git_push(self):
        """手动推送Git"""
        self.log("正在手动推送Git...", "INFO")
        
        import threading
        
        def _manual_push():
            try:
                # 先添加所有更改
                success1, output1 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["add", "."]
                )
                
                if not success1:
                    self.log(f"❌ Git添加失败: {output1}", "ERROR")
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
                        self.log("⚠️ 没有需要提交的更改", "WARNING")
                    else:
                        self.log(f"❌ Git提交失败: {output2}", "ERROR")
                        return
                
                # 推送
                success3, output3 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["push", "origin", "master"]
                )
                
                if success3:
                    self.log("✅ 手动推送成功", "SUCCESS")
                    self.log(output3, "INFO")
                else:
                    self.log(f"❌ 手动推送失败: {output3}", "ERROR")
                    
            except Exception as e:
                self.log(f"手动推送异常: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_manual_push)
        thread.daemon = True
        thread.start()
    
    def diagnose_git_connection(self):
        """诊断Git连接问题"""
        self.log("🔧 开始Git连接诊断...", "INFO")
        
        import threading
        
        def _diagnose():
            try:
                self.log("=" * 60, "INFO")
                self.log("Git连接问题诊断报告", "INFO")
                self.log("=" * 60, "INFO")
                
                # 1. 测试网络连接
                self.log("\n1. 测试网络连接...", "INFO")
                success_ping, output_ping = self.deployment_manager.run_command(
                    "ping",
                    ["-n", "4", "github.com"]
                )
                
                if success_ping:
                    self.log("✅ Ping测试成功", "SUCCESS")
                    # 提取延迟信息
                    if "平均" in output_ping:
                        for line in output_ping.split('\n'):
                            if "平均" in line:
                                self.log(f"网络延迟: {line.strip()}", "INFO")
                else:
                    self.log("❌ Ping测试失败", "ERROR")
                    self.log("可能原因: 网络断开、DNS问题、防火墙阻止", "WARNING")
                
                # 2. 测试HTTPS连接
                self.log("\n2. 测试HTTPS连接...", "INFO")
                try:
                    import urllib.request
                    import urllib.error
                    import ssl
                    
                    # 创建不验证SSL的上下文（仅用于测试）
                    context = ssl._create_unverified_context()
                    req = urllib.request.Request("https://github.com", method="HEAD")
                    
                    try:
                        response = urllib.request.urlopen(req, timeout=10, context=context)
                        self.log(f"✅ HTTPS连接成功 (状态码: {response.status})", "SUCCESS")
                    except urllib.error.URLError as e:
                        self.log(f"❌ HTTPS连接失败: {str(e)}", "ERROR")
                except Exception as e:
                    self.log(f"HTTPS测试异常: {str(e)}", "ERROR")
                
                # 3. 检查Git配置
                self.log("\n3. 检查Git配置...", "INFO")
                
                # 检查远程仓库
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.log("远程仓库配置:", "INFO")
                    self.log(output_remote, "INFO")
                else:
                    self.log("❌ 无法获取远程仓库配置", "ERROR")
                
                # 检查代理设置
                success_proxy, output_proxy = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["config", "--global", "http.proxy"]
                )
                
                if success_proxy and output_proxy.strip():
                    self.log(f"⚠️ 检测到Git代理设置: {output_proxy.strip()}", "WARNING")
                else:
                    self.log("✅ 无Git代理设置", "SUCCESS")
                
                # 4. 测试Git连接
                self.log("\n4. 测试Git连接...", "INFO")
                success_git, output_git = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["ls-remote", "https://github.com/juemin7-star/toothmen-docs.git", "--heads"]
                )
                
                if success_git:
                    self.log("✅ Git连接成功", "SUCCESS")
                else:
                    self.log("❌ Git连接失败", "ERROR")
                    self.log(f"错误详情: {output_git}", "ERROR")
                    
                    # 分析错误类型
                    error_lower = output_git.lower()
                    if "permission denied" in error_lower or "authentication failed" in error_lower:
                        self.log("\n🔐 检测到认证问题:", "WARNING")
                        self.log("  1. 检查SSH密钥配置", "INFO")
                        self.log("  2. 检查GitHub Token是否有效", "INFO")
                        self.log("  3. 检查远程仓库权限", "INFO")
                    elif "connection" in error_lower or "timeout" in error_lower or "could not connect" in error_lower:
                        self.log("\n🌐 检测到网络连接问题:", "WARNING")
                        self.log("  1. 检查网络连接", "INFO")
                        self.log("  2. 检查防火墙设置", "INFO")
                        self.log("  3. 尝试使用VPN或切换网络", "INFO")
                    elif "proxy" in error_lower:
                        self.log("\n🔄 检测到代理问题:", "WARNING")
                        self.log("  清除代理: git config --global --unset http.proxy", "INFO")
                
                # 5. 检查本地提交状态
                self.log("\n5. 检查本地提交状态...", "INFO")
                
                # 获取最后提交
                success_log, output_log = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-1"]
                )
                
                if success_log:
                    self.log(f"最后提交: {output_log.strip()}", "INFO")
                else:
                    self.log("无法获取提交信息", "WARNING")
                
                # 检查未推送的提交
                success_unpushed, output_unpushed = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "origin/master..HEAD", "--oneline"]
                )
                
                if success_unpushed and output_unpushed.strip():
                    self.log("⚠️ 有未推送的提交:", "WARNING")
                    self.log(output_unpushed, "INFO")
                else:
                    self.log("✅ 所有提交已推送或没有新提交", "SUCCESS")
                
                # 6. 提供解决方案
                self.log("\n" + "=" * 60, "INFO")
                self.log("💡 解决方案建议:", "INFO")
                self.log("=" * 60, "INFO")
                
                self.log("\n🔹 如果HTTPS连接失败:", "INFO")
                self.log("  1. 切换到SSH方式（点击'切换到SSH'按钮）", "INFO")
                self.log("  2. 检查防火墙设置", "INFO")
                self.log("  3. 清除代理: git config --global --unset http.proxy", "INFO")
                self.log("  4. 尝试使用VPN或手机热点", "INFO")
                
                self.log("\n🔹 如果认证失败:", "INFO")
                self.log("  1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email\"", "INFO")
                self.log("  2. 添加公钥到GitHub", "INFO")
                self.log("  3. 测试SSH连接: ssh -T git@github.com", "INFO")
                
                self.log("\n🔹 立即操作:", "INFO")
                self.log("  1. 使用'切换到SSH'按钮", "INFO")
                self.log("  2. 使用'手动推送Git'按钮", "INFO")
                self.log("  3. 检查网络连接后重试", "INFO")
                
                self.log("\n✅ 诊断完成！", "SUCCESS")
                
            except Exception as e:
                self.log(f"诊断过程中出现异常: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_diagnose)
        thread.daemon = True
        thread.start()
    
    def switch_to_ssh(self):
        """切换到SSH方式"""
        self.log("⚡ 正在切换到SSH方式...", "INFO")
        
        import threading
        
        def _switch_ssh():
            try:
                # 1. 显示当前配置
                self.log("当前远程仓库配置:", "INFO")
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.log(output_remote, "INFO")
                else:
                    self.log("无法获取远程仓库配置", "ERROR")
                    return
                
                # 2. 切换到SSH
                self.log("\n正在修改远程URL为SSH...", "INFO")
                success_switch, output_switch = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "set-url", "origin", "git@github.com:juemin7-star/toothmen-docs.git"]
                )
                
                if success_switch:
                    self.log("✅ 已切换到SSH方式", "SUCCESS")
                    
                    # 3. 显示新配置
                    self.log("\n新的远程仓库配置:", "INFO")
                    success_new, output_new = self.deployment_manager.run_command(
                        self.deployment_manager.git_path,
                        ["remote", "-v"]
                    )
                    
                    if success_new:
                        self.log(output_new, "INFO")
                    else:
                        self.log("无法获取新配置", "WARNING")
                    
                    # 4. 测试SSH连接
                    self.log("\n测试SSH连接...", "INFO")
                    success_test, output_test = self.deployment_manager.run_command(
                        "ssh",
                        ["-T", "git@github.com"]
                    )
                    
                    if success_test:
                        self.log("✅ SSH连接成功", "SUCCESS")
                        self.log(output_test, "INFO")
                    else:
                        self.log("⚠️ SSH连接测试失败", "WARNING")
                        self.log("可能需要设置SSH密钥:", "INFO")
                        self.log("  1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email\"", "INFO")
                        self.log("  2. 添加公钥到GitHub", "INFO")
                        self.log("  3. 启动ssh-agent: eval \"$(ssh-agent -s)\"", "INFO")
                        self.log("  4. 添加私钥: ssh-add ~/.ssh/id_ed25519", "INFO")
                    
                    # 5. 询问是否立即推送
                    self.log("\n💡 建议:", "INFO")
                    self.log("  现在可以使用'手动推送Git'按钮进行推送", "INFO")
                    self.log("  或稍后执行: git push origin master", "INFO")
                    
                else:
                    self.log(f"❌ 切换到SSH失败: {output_switch}", "ERROR")
                    
            except Exception as e:
                self.log(f"切换到SSH过程中出现异常: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_switch_ssh)
        thread.daemon = True
        thread.start()
    
    def clear_npm_cache(self):
        """清除npm缓存"""
        self.log("正在清除npm缓存...", "INFO")
        
        import threading
        
        def _clear_cache():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.npm_path,
                    ["cache", "clean", "--force"]
                )
                
                if success:
                    self.log("✅ npm缓存清除成功", "SUCCESS")
                    self.log(output, "INFO")
                else:
                    self.log(f"❌ npm缓存清除失败: {output}", "ERROR")
                    
            except Exception as e:
                self.log(f"清除npm缓存异常: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_clear_cache)
        thread.daemon = True
        thread.start()
    
    def open_project_folder(self):
        """打开项目文件夹"""
        try:
            import os
            import subprocess
            
            project_path = str(self.deployment_manager.project_path)
            self.log(f"正在打开项目文件夹: {project_path}", "INFO")
            
            if os.path.exists(project_path):
                subprocess.run(["explorer", project_path], shell=True)
                self.log("✅ 已打开项目文件夹", "SUCCESS")
            else:
                self.log(f"❌ 文件夹不存在: {project_path}", "ERROR")
                
        except Exception as e:
            self.log(f"打开文件夹异常: {str(e)}", "ERROR")
    
    def check_config(self):
        """检查配置"""
        self.log("正在检查配置...", "INFO")
        
        try:
            config = self.deployment_manager.config
            
            self.log("当前配置:", "INFO")
            self.log(f"项目路径: {config.get('project_path', '未设置')}", "INFO")
            self.log(f"测试文件夹: {config.get('test_folder', '未设置')}", "INFO")
            self.log(f"生产文件夹: {config.get('production_folder', '未设置')}", "INFO")
            self.log(f"npm路径: {config.get('npm_path', '未设置')}", "INFO")
            self.log(f"git路径: {config.get('git_path', '未设置')}", "INFO")
            
            # 检查路径是否存在
            import os
            project_path = config.get('project_path', '')
            if project_path and os.path.exists(project_path):
                self.log("✅ 项目路径存在", "SUCCESS")
            else:
                self.log("❌ 项目路径不存在或未设置", "ERROR")
                
        except Exception as e:
            self.log(f"检查配置异常: {str(e)}", "ERROR")
    
    def copy_error_info(self):
        """复制错误信息到剪贴板"""
        try:
            import tkinter as tk
            
            # 获取最后10行日志
            log_content = self.log_text.get("end-10l", "end")
            
            if log_content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(log_content)
                self.log("✅ 已复制最后10行日志到剪贴板", "SUCCESS")
            else:
                self.log("⚠️ 日志为空，没有可复制的内容", "WARNING")
                
        except Exception as e:
            self.log(f"复制错误信息异常: {str(e)}", "ERROR")
    
    def confirm_preview(self):
        """确认本地预览成功（用户手动确认，不检查服务器）"""
        try:
            self.update_button_state("确认预览", "running")
            
            # 用户手动确认，总是成功
            self.log("本地预览已手动确认成功", "SUCCESS")
            self.update_button_state("确认预览", "success")
                
        except Exception as e:
            self.log(f"确认预览异常: {str(e)}", "ERROR")
            self.update_button_state("确认预览", "error")
    
    def start_deployment_flow(self):
        """开始部署流程"""
        self.deployment_started = True
        self.deployment_step = 0
        
        # 禁用开始按钮，启用结束按钮
        self.btn_start.config(state="disabled")
        self.btn_end.config(state="normal")
        
        # 启用第一个步骤按钮
        self.enable_deployment_step(0)
        
        self.log("部署流程已开始，请按顺序执行步骤", "INFO")
    
    def end_deployment_flow(self):
        """结束部署流程"""
        self.deployment_started = False
        
        # 启用开始按钮，禁用结束按钮
        self.btn_start.config(state="normal")
        self.btn_end.config(state="disabled")
        
        # 禁用所有步骤按钮
        for i in range(len(self.deployment_buttons)):
            self.disable_deployment_step(i)
        
        self.log("部署流程已结束", "INFO")
    
    def enable_deployment_step(self, step_index):
        """启用指定步骤的按钮"""
        if step_index < len(self.deployment_buttons):
            button_name = self.deployment_buttons[step_index][0]
            button = getattr(self, f"btn_{button_name.replace(' ', '_')}")
            button.config(state="normal")
    
    def disable_deployment_step(self, step_index):
        """禁用指定步骤的按钮"""
        if step_index < len(self.deployment_buttons):
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
            
            self.log(f"已解锁步骤 {self.deployment_step+1}: {self.deployment_buttons[self.deployment_step][0]}", "INFO")
    
    def update_button_state(self, button_name, state):
        """更新按钮状态"""
        # 特殊处理MDX检测按钮
        if button_name == "🔍 检测MDX语法&更新侧边栏":
            button = self.btn_mdx_check
        else:
            # 处理其他按钮名称，移除特殊字符
            button_attr_name = button_name.replace(' ', '_')
            button = getattr(self, f"btn_{button_attr_name}")
        
        colors = {
            "normal": ("SystemButtonFace", "black"),
            "running": ("yellow", "black"),
            "success": ("green", "white"),
            "error": ("red", "white")
        }
        
        bg_color, fg_color = colors.get(state, colors["normal"])
        
        self.root.after(0, lambda: button.config(
            background=bg_color,
            foreground=fg_color
        ))
        
        # 如果是成功状态，解锁下一个步骤（MDX检测按钮除外）
        if state == "success" and button_name != "🔍 检测MDX语法&更新侧边栏":
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
    
    # ========== 日志方法 ==========
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        
        # 添加到日志文本框
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        
        # 根据级别设置颜色
        colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = colors.get(level, "black")
        
        # 设置最后一行颜色
        start_index = f"{self.log_text.index('end-2l')}"
        end_index = f"{self.log_text.index('end-1l')}"
        
        self.log_text.tag_add(level, start_index, end_index)
        self.log_text.tag_config(level, foreground=color)
        
        # 也输出到控制台
        print(formatted_message)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("日志已清空", "INFO")
    
    def save_log(self):
        """保存日志到文件"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"日志已保存到: {filename}", "SUCCESS")
            except Exception as e:
                self.log(f"保存日志失败: {str(e)}", "ERROR")
    
    def copy_log(self):
        """复制日志到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get(1.0, tk.END))
        self.log("日志已复制到剪贴板", "SUCCESS")
    
    # ========== 文件监控 ==========
    
    def start_file_monitoring(self):
        """启动文件监控"""
        # 使用定时器定期检查文件变化
        self.check_file_changes()
    
    def check_file_changes(self):
        """检查文件变化"""
        try:
            # 检查文件数量变化
            current_test_count = len(list(self.test_folder.glob("*.mdx")))
            current_prod_count = len(list(self.prod_folder.glob("*.mdx")))
            
            # 如果数量变化，刷新列表
            if (hasattr(self, 'last_test_count') and 
                current_test_count != self.last_test_count):
                self.refresh_file_lists()
            
            if (hasattr(self, 'last_prod_count') and 
                current_prod_count != self.last_prod_count):
                self.refresh_file_lists()
            
            # 保存当前计数
            self.last_test_count = current_test_count
            self.last_prod_count = current_prod_count
            
        except Exception as e:
            self.log(f"文件监控错误: {str(e)}", "ERROR")
        
        # 5秒后再次检查
        self.root.after(5000, self.check_file_changes)

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()