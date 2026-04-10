#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 - 简单版本
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import sys
import json
import threading
import subprocess
import shutil
import re
from datetime import datetime
from pathlib import Path

# 导入自定义模块
from deployment_manager_new import DeploymentManager
from logger import Logger
from mdx_checker import MDXChecker

class ToothMenDocsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v2.2")
        self.root.geometry("1400x1000")
        
        # 项目路径
        self.project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
        self.docs_folder = self.project_path / "docs"
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 确保docs文件夹存在
        self.docs_folder.mkdir(exist_ok=True)
        
        # 初始化管理器
        self.deployment_manager = DeploymentManager(self.project_path)
        self.logger = Logger()
        self.mdx_checker = MDXChecker(self.docs_folder)
        
        # 设置日志文本框
        self.log_text = None
        
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
        
        # 创建UI
        self.create_ui()
        
        # 初始刷新文件夹结构
        self.refresh_folder_structure()
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)
        
        # 顶部：标题和按钮区域
        self.create_top_area(main_frame)
        
        # 中部：文件夹结构显示
        self.create_folder_structure_area(main_frame)
        
        # 底部：日志区域
        self.create_log_area(main_frame)
    
    def create_top_area(self, parent):
        """创建顶部区域"""
        top_frame = ttk.Frame(parent)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 标题
        title_label = ttk.Label(top_frame, text="ToothMen文档管理系统", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # 按钮框架
        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=0, column=1, sticky=tk.E)
        
        # 检测MDX语法按钮
        self.check_mdx_btn = ttk.Button(button_frame, text="检测MDX语法", command=self.check_mdx_syntax)
        self.check_mdx_btn.grid(row=0, column=0, padx=5)
        
        # 部署流程按钮
        self.deploy_start_btn = ttk.Button(button_frame, text="开始部署", command=self.start_deployment)
        self.deploy_start_btn.grid(row=0, column=1, padx=5)
        
        self.deploy_end_btn = ttk.Button(button_frame, text="结束流程", command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=2, padx=5)
        
        # 验证部署按钮
        self.verify_deploy_btn = ttk.Button(button_frame, text="验证部署", command=self.verify_deployment)
        self.verify_deploy_btn.grid(row=0, column=3, padx=5)
        
        # 部署步骤按钮
        self.step_buttons = []
        for i, step in enumerate(self.deployment_steps):
            btn = ttk.Button(button_frame, text=step, command=lambda s=step: self.execute_step(s), state=tk.DISABLED)
            btn.grid(row=1, column=i, padx=5, pady=(5, 0))
            self.step_buttons.append(btn)
    
    def create_folder_structure_area(self, parent):
        """创建文件夹结构显示区域"""
        frame = ttk.LabelFrame(parent, text="📁 文档文件夹结构", padding="10")
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        self.tree = ttk.Treeview(frame, columns=("type", "path"), show="tree", height=15)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 配置列
        self.tree.column("#0", width=400)
        self.tree.column("type", width=100)
        self.tree.column("path", width=300)
        
        # 添加标题
        self.tree.heading("#0", text="文件/文件夹")
        self.tree.heading("type", text="类型")
        self.tree.heading("path", text="路径")
    
    def create_log_area(self, parent):
        """创建日志区域"""
        frame = ttk.LabelFrame(parent, text="📝 操作日志", padding="10")
        frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # 创建日志文本框
        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置标签
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
    
    def log_message(self, message, level="info"):
        """记录日志消息"""
        if self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"
            
            self.log_text.insert(tk.END, log_line, level)
            self.log_text.see(tk.END)
            self.log_text.update()
    
    def refresh_folder_structure(self):
        """刷新文件夹结构显示"""
        try:
            # 清空树
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            total_folders = 0
            total_files = 0
            
            # 添加根节点
            root_text = "📂 docs文件夹"
            self.tree.insert("", 0, text=root_text, values=("根目录", ""), open=True)
            
            # 获取所有文件夹
            folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    folders.append(item.name)
            
            # 按数字前缀排序
            sorted_folders = self.sort_by_number_prefix(folders)
            
            for folder_name in sorted_folders:
                total_folders += 1
                folder_path = self.docs_folder / folder_name
                folder_id = self.tree.insert("", tk.END, text=f"📁 {folder_name}", values=("文件夹", str(folder_path)), open=True)
                
                # 获取文件夹内的MDX文件
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                
                # 判断是否需要倒序排序
                is_reverse = self.should_reverse_order(folder_name)
                
                # 按规则排序文件
                sorted_files = self.sort_files_by_rule(mdx_files, reverse=is_reverse)
                
                for file_name in sorted_files:
                    total_files += 1
                    file_path = folder_path / file_name
                    self.tree.insert(folder_id, tk.END, text=f"📄 {file_name}", values=("MDX文件", str(file_path)))
            
            # 更新根节点文本
            self.tree.item(self.tree.get_children()[0], text=f"📂 docs文件夹 (共{total_folders}个分类，{total_files}个MDX文件)")
            
            self.log_message(f"文件夹结构已刷新，共{total_folders}个分类，{total_files}个MDX文件", "success")
            
        except Exception as e:
            self.log_message(f"刷新文件夹结构失败: {str(e)}", "error")
    
    def sort_by_number_prefix(self, items):
        """按数字前缀排序"""
        def extract_sort_key(item):
            import re
            match = re.match(r'^(\d+)[\-\.]?(.*)', item)
            if match:
                num = int(match.group(1))
                name = match.group(2)
                return (num, name)
            return (float('inf'), item)
        
        return sorted(items, key=extract_sort_key)
    
    def should_reverse_order(self, folder_name):
        """判断是否需要倒序排序"""
        reverse_folders = ["补丁更新日志", "bugfixlog", "3-bugfixlog"]
        clean_name = self.clean_name(folder_name)
        return clean_name in reverse_folders
    
    def sort_files_by_rule(self, files, reverse=False):
        """按规则排序文件"""
        def extract_sort_key(item):
            import re
            match = re.match(r'^(\d+)[\-\.]?(.*)', item)
            if match:
                num = int(match.group(1))
                name = match.group(2)
                return (num, name)
            return (float('inf'), item)
        
        sorted_files = sorted(files, key=extract_sort_key, reverse=reverse)
        return sorted_files
    
    def clean_name(self, name):
        """清理名称"""
        if name.endswith('.mdx'):
            name = name[:-4]
        
        import re
        name = re.sub(r'^\d+\-', '', name)
        
        return name
    
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
                        if result:
                            self.log_message(f"  ✓ {folder.name}\\{file.name}", "success")
                            success_count += 1
                        else:
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
        self.deploy_start_btn.config(state=tk.DISABLED)
        self.deploy_end_btn.config(state=tk.NORMAL)
        
        # 启用第一个步骤按钮
        if self.step_buttons:
            self.step_buttons[0].config(state=tk.NORMAL)
        
        self.log_message("部署流程已开始，请按顺序执行步骤")
        self.log_message("步骤1: 刷新文件结构 → 步骤2: 生成侧边栏 → 步骤3: 本地构建测试 → 步骤4: 本地预览 → 步骤5: 自动部署")
    
    def end_deployment(self):
        """结束部署流程"""
        self.deployment_started = False
        self.current_step = 0
        self.deploy_start_btn.config(state=tk.NORMAL)
        self.deploy_end_btn.config(state=tk.DISABLED)
        
        # 禁用所有步骤按钮
        for btn in self.step_buttons:
            btn.config(state=tk.DISABLED)
        
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
            self.step_buttons[self.current_step].config(state=tk.NORMAL)
    
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
                self.step_buttons[step_index].config(state=tk.DISABLED)
                self.log_message(f"已解锁步骤 {self.current_step + 1}: {self.deployment_steps[self.current_step]}")
                
        except Exception as e:
            self.log_message(f"生成侧边栏失败: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("生成侧边栏")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
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
                    self.step_buttons[step_index].config(state=tk.DISABLED)
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
                    self.step_buttons[step_index].config(state=tk.NORMAL)
                    
        except Exception as e:
            self.log_message(f"本地构建测试异常: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("本地构建测试")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
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
                    self.step_buttons[step_index].config(state=tk.DISABLED)
                    self.log_message(f"已解锁步骤 {self.current_step + 1}: {self.deployment_steps[self.current_step]}")
            else:
                self.log_message("启动本地预览失败", "error")
                self.log_message("启动本地预览失败，请查看日志", "error")
                
                # 如果是在部署流程中，更新按钮状态
                if self.deployment_started:
                    step_index = self.deployment_steps.index("本地预览")
                    self.step_buttons[step_index].config(state=tk.NORMAL)
                    
        except Exception as e:
            self.log_message(f"启动本地预览异常: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("本地预览")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
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
                    self.step_buttons[step_index].config(state=tk.DISABLED)
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
                    self.step_buttons[step_index].config(state=tk.NORMAL)
                    
        except Exception as e:
            self.log_message(f"自动部署异常: {str(e)}", "error")
            
            # 如果是在部署流程中，更新按钮状态
            if self.deployment_started:
                step_index = self.deployment_steps.index("自动部署")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
    def verify_deployment(self):
        """验证部署"""
        self.log_message("开始验证部署...")
        
        try:
            import webbrowser
            webbrowser.open("https://docs.toothmen.com")
            self.log_message("已打开部署网站: https://docs.toothmen.com", "success")
            
        except Exception as e:
            self.log_message(f"验证部署失败: {str(e)}", "error")

def main():
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()