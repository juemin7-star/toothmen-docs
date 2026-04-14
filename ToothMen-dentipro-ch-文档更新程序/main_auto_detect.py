#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.16 - 完整工作流版
功能：文件自动检测 + 自动化部署工作流 + 完整构建流程
按照数字前缀文件结构自动生成分类侧边栏
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
        self.root.title("ToothMen-DentiPro-中文文档管理系统 v3.16 - 完整工作流版")
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
        
        # 创建UI
        self.create_ui()
        
        # 初始状态
        self.update_status("就绪")
        
        # 自动检测文件夹结构
        self.auto_detect_and_update()
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="ToothMen-DentiPro 中文文档管理系统 v3.16",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 项目信息
        info_frame = ttk.LabelFrame(main_frame, text="项目信息", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(info_frame, text="项目路径:").grid(row=0, column=0, sticky=tk.W)
        self.project_path_label = ttk.Label(info_frame, text=str(self.project_path))
        self.project_path_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="文档文件夹:").grid(row=1, column=0, sticky=tk.W)
        self.docs_path_label = ttk.Label(info_frame, text=str(self.docs_folder))
        self.docs_path_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # 第一行按钮
        button_row1 = ttk.Frame(control_frame)
        button_row1.pack(fill=tk.X, pady=(0, 5))
        
        self.auto_detect_btn = ttk.Button(
            button_row1, 
            text="🔄 自动检测文件夹结构", 
            command=self.auto_detect_and_update,
            width=25
        )
        self.auto_detect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.scan_btn = ttk.Button(
            button_row1, 
            text="🔍 扫描文档结构", 
            command=self.scan_docs_structure,
            width=20
        )
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.update_sidebar_btn = ttk.Button(
            button_row1, 
            text="📋 更新侧边栏", 
            command=self.update_sidebars,
            width=20
        )
        self.update_sidebar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 第二行按钮
        button_row2 = ttk.Frame(control_frame)
        button_row2.pack(fill=tk.X, pady=(0, 5))
        
        self.build_btn = ttk.Button(
            button_row2, 
            text="🏗️  构建网站", 
            command=self.build_website,
            width=20
        )
        self.build_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.serve_btn = ttk.Button(
            button_row2, 
            text="🚀 启动本地服务器", 
            command=self.serve_local,
            width=20
        )
        self.serve_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.full_deploy_btn = ttk.Button(
            button_row2, 
            text="⚡ 一键部署", 
            command=self.full_deployment,
            width=20
        )
        self.full_deploy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 第三行按钮
        button_row3 = ttk.Frame(control_frame)
        button_row3.pack(fill=tk.X)
        
        self.complete_workflow_btn = ttk.Button(
            button_row3,
            text="🚀 完整工作流（推荐）",
            command=self.complete_workflow,
            width=25
        )
        self.complete_workflow_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_docs_btn = ttk.Button(
            button_row3, 
            text="📂 打开文档文件夹", 
            command=self.open_docs_folder,
            width=20
        )
        self.open_docs_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_project_btn = ttk.Button(
            button_row3, 
            text="📁 打开项目文件夹", 
            command=self.open_project_folder,
            width=20
        )
        self.open_project_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_cache_btn = ttk.Button(
            button_row3, 
            text="🗑️  清除缓存", 
            command=self.clear_cache,
            width=20
        )
        self.clear_cache_btn.pack(side=tk.LEFT)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            width=100, 
            height=20,
            font=("Consolas", 10)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 文件夹结构显示
        structure_frame = ttk.LabelFrame(main_frame, text="检测到的文件夹结构", padding="10")
        structure_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        structure_frame.columnconfigure(0, weight=1)
        structure_frame.rowconfigure(0, weight=1)
        
        self.structure_text = scrolledtext.ScrolledText(
            structure_frame, 
            width=100, 
            height=15,
            font=("Consolas", 10)
        )
        self.structure_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始显示文件夹结构
        self.display_folder_structure()
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = level_colors.get(level, "black")
        
        # 插入带颜色的文本
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # 更新状态
        if level in ["SUCCESS", "ERROR"]:
            self.update_status(message, level)
    
    def update_status(self, message, level="INFO"):
        """更新状态栏"""
        colors = {
            "INFO": "green",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = colors.get(level, "green")
        self.status_label.config(text=message, foreground=color)
    
    def auto_detect_and_update(self):
        """自动检测文件夹结构并更新所有配置"""
        def _auto_detect():
            self.log("🔄 开始自动检测文件夹结构...", "INFO")
            
            try:
                # 调用自动检测方法
                self.deployment_manager.auto_detect_folders()
                
                # 显示检测结果
                self.display_folder_structure()
                
                self.log("✅ 文件夹结构自动检测完成", "SUCCESS")
                self.log("📋 已自动更新排序配置和导航栏配置", "INFO")
                
            except Exception as e:
                self.log(f"❌ 自动检测失败: {str(e)}", "ERROR")
        
        # 在新线程中执行
        thread = threading.Thread(target=_auto_detect)
        thread.daemon = True
        thread.start()
    
    def complete_workflow(self):
        """完整工作流：清理缓存 + 自动检测 + 构建网站"""
        def _complete_workflow():
            self.log("🏗️  开始完整工作流...", "INFO")
            self.log("=" * 60, "INFO")
            
            try:
                # 步骤1: 清理缓存
                self.log("📋 步骤1: 清理缓存", "INFO")
                success, message = self.deployment_manager.clean_cache(thorough=True)
                if success:
                    self.log(f"✅ {message}", "SUCCESS")
                else:
                    self.log(f"⚠️  {message}", "WARNING")
                
                # 步骤2: 自动检测文件夹结构
                self.log("📋 步骤2: 自动检测文件夹结构", "INFO")
                self.deployment_manager.auto_detect_folders(clean_cache_before=False, clean_cache_after=False)
                
                # 步骤3: 构建网站
                self.log("📋 步骤3: 构建网站", "INFO")
                success, message = self.deployment_manager.build_website(
                    clean_cache_before=False,  # 已经在步骤1清理过了
                    clean_cache_after=True,
                    serve_after_build=True,
                    port=3000
                )
                
                if success:
                    self.log(f"✅ {message}", "SUCCESS")
                    self.log("🎉 完整工作流执行完成！", "SUCCESS")
                    
                    # 显示构建结果
                    self.log("=" * 60, "INFO")
                    self.log("📊 工作流执行结果:", "INFO")
                    self.log("  ✅ 缓存已彻底清理", "INFO")
                    self.log("  ✅ 文件夹结构已自动检测", "INFO")
                    self.log("  ✅ 配置文件已更新", "INFO")
                    self.log("  ✅ 网站已成功构建", "INFO")
                    self.log(f"  ✅ 服务器已启动: http://localhost:3000", "INFO")
                    self.log("=" * 60, "INFO")
                else:
                    self.log(f"❌ {message}", "ERROR")
                    self.log("⚠️  完整工作流执行失败", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ 完整工作流执行失败: {str(e)}", "ERROR")
        
        # 在新线程中执行
        thread = threading.Thread(target=_complete_workflow)
        thread.daemon = True
        thread.start()
    
    def display_folder_structure(self):
        """显示文件夹结构"""
        try:
            # 清空文本
            self.structure_text.delete(1.0, tk.END)
            
            # 获取文件夹结构
            structure = self.deployment_manager.scan_folder_structure()
            
            if not structure:
                self.structure_text.insert(tk.END, "📁 未检测到任何文件夹\n")
                return
            
            # 显示文件夹结构
            self.structure_text.insert(tk.END, "📁 检测到的文件夹结构:\n")
            self.structure_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for folder, files in structure.items():
                self.structure_text.insert(tk.END, f"📂 {folder}/\n")
                
                if files:
                    for file in files:
                        self.structure_text.insert(tk.END, f"  📄 {file}\n")
                else:
                    self.structure_text.insert(tk.END, f"  📄 (空文件夹)\n")
                
                self.structure_text.insert(tk.END, "\n")
            
            # 显示导航栏配置
            self.structure_text.insert(tk.END, "🔗 导航栏配置:\n")
            self.structure_text.insert(tk.END, "=" * 50 + "\n\n")
            
            # 读取导航栏配置
            config_path = self.project_path / "docusaurus.config.js"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找导航栏配置
                import re
                pattern = r'items:\s*\[(.*?)\]'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    items_content = match.group(1)
                    # 提取docId
                    doc_id_pattern = r"docId:\s*'([^']+)'"
                    doc_ids = re.findall(doc_id_pattern, items_content)
                    
                    for doc_id in doc_ids:
                        self.structure_text.insert(tk.END, f"  📍 {doc_id}\n")
                else:
                    self.structure_text.insert(tk.END, "  (未找到导航栏配置)\n")
            else:
                self.structure_text.insert(tk.END, "  (配置文件不存在)\n")
            
        except Exception as e:
            self.structure_text.insert(tk.END, f"❌ 显示文件夹结构失败: {str(e)}\n")
    
    def scan_docs_structure(self):
        """扫描文档结构"""
        def _scan():
            self.log("🔍 开始扫描文档结构...", "INFO")
            
            try:
                structure = self.deployment_manager.scan_folder_structure()
                
                if structure:
                    self.log(f"✅ 扫描完成，找到 {len(structure)} 个文件夹", "SUCCESS")
                    
                    # 显示详细结构
                    for folder, files in structure.items():
                        self.log(f"📂 {folder}/ ({len(files)} 个文件)", "INFO")
                else:
                    self.log("📁 docs文件夹为空", "WARNING")
                
                # 更新显示
                self.display_folder_structure()
                
            except Exception as e:
                self.log(f"❌ 扫描失败: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_scan)
        thread.daemon = True
        thread.start()
    
    def update_sidebars(self):
        """更新侧边栏"""
        def _update():
            self.log("📋 开始更新侧边栏...", "INFO")
            
            try:
                success, message = self.deployment_manager.update_sidebars()
                
                if success:
                    self.log(f"✅ {message}", "SUCCESS")
                else:
                    self.log(f"❌ {message}", "ERROR")
                
            except Exception as e:
                self.log(f"❌ 更新侧边栏失败: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_update)
        thread.daemon = True
        thread.start()
    
    def build_website(self):
        """构建网站"""
        def _build():
            self.log("🏗️  开始构建网站...", "INFO")
            
            try:
                success, output = self.deployment_manager.local_build_test()
                
                if success:
                    self.log(f"✅ 构建成功: {output}", "SUCCESS")
                else:
                    self.log(f"❌ 构建失败: {output}", "ERROR")
                
            except Exception as e:
                self.log(f"❌ 构建失败: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_build)
        thread.daemon = True
        thread.start()
    
    def serve_local(self):
        """启动本地服务器"""
        def _serve():
            self.log("🚀 启动本地服务器...", "INFO")
            
            try:
                success, output = self.deployment_manager.serve_local()
                
                if success:
                    self.log(f"✅ 服务器启动成功: {output}", "SUCCESS")
                else:
                    self.log(f"❌ 服务器启动失败: {output}", "ERROR")
                
            except Exception as e:
                self.log(f"❌ 服务器启动失败: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_serve)
        thread.daemon = True
        thread.start()
    
    def full_deployment(self):
        """一键部署"""
        def _deploy():
            self.log("⚡ 开始一键部署...", "INFO")
            
            try:
                # 1. 自动检测文件夹结构
                self.log("🔄 自动检测文件夹结构...", "INFO")
                self.deployment_manager.auto_detect_folders()
                
                # 2. 更新侧边栏
                self.log("📋 更新侧边栏...", "INFO")
                success1, message1 = self.deployment_manager.update_sidebars()
                if not success1:
                    self.log(f"❌ 侧边栏更新失败: {message1}", "ERROR")
                    return
                
                # 3. 构建网站
                self.log("🏗️  构建网站...", "INFO")
                success2, message2 = self.deployment_manager.local_build_test()
                if not success2:
                    self.log(f"❌ 构建失败: {message2}", "ERROR")
                    return
                
                # 4. 启动服务器
                self.log("🚀 启动本地服务器...", "INFO")
                success3, message3 = self.deployment_manager.serve_local()
                if not success3:
                    self.log(f"❌ 服务器启动失败: {message3}", "ERROR")
                    return
                
                self.log("✅ 一键部署完成！", "SUCCESS")
                self.log(f"📊 部署结果: 侧边栏={success1}, 构建={success2}, 服务器={success3}", "INFO")
                
                # 更新显示
                self.display_folder_structure()
                
            except Exception as e:
                self.log(f"❌ 一键部署失败: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_deploy)
        thread.daemon = True
        thread.start()
    
    def open_docs_folder(self):
        """打开文档文件夹"""
        try:
            import os
            import subprocess
            
            docs_path = str(self.docs_folder)
            self.log(f"正在打开文档文件夹: {docs_path}", "INFO")
            
            if os.path.exists(docs_path):
                subprocess.run(["explorer", docs_path], shell=True)
                self.log("✅ 已打开文档文件夹", "SUCCESS")
            else:
                self.log("❌ 文档文件夹不存在", "ERROR")
                
        except Exception as e:
            self.log(f"❌ 打开文档文件夹失败: {str(e)}", "ERROR")
    
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
                self.log("❌ 项目文件夹不存在", "ERROR")
                
        except Exception as e:
            self.log(f"❌ 打开项目文件夹失败: {str(e)}", "ERROR")
    
    def clear_cache(self):
        """清除缓存"""
        def _clear_cache():
            self.log("🗑️  开始清除缓存...", "INFO")
            
            try:
                # 清除Docusaurus缓存
                cache_path = self.project_path / ".docusaurus"
                build_path = self.project_path / "build"
                
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                    self.log(f"✅ 已清除Docusaurus缓存: {cache_path}", "SUCCESS")
                
                if build_path.exists():
                    shutil.rmtree(build_path)
                    self.log(f"✅ 已清除构建目录: {build_path}", "SUCCESS")
                
                if not cache_path.exists() and not build_path.exists():
                    self.log("✅ 缓存清除完成", "SUCCESS")
                else:
                    self.log("⚠️  部分缓存可能未完全清除", "WARNING")
                    
            except Exception as e:
                self.log(f"❌ 清除缓存失败: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=_clear_cache)
        thread.daemon = True
        thread.start()

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()