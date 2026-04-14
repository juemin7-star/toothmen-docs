#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.16 - 恢复原始布局版
功能：文件夹分类管理 + 自动化部署工作流 + 完整构建流程
按照数字前缀文件夹结构自动生成分类侧边栏
包含缓存清理功能
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
import time
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
        
        # 立即显示窗口，避免闪烁
        self.root.update_idletasks()
        
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
        
        # 显示加载提示
        self.loading_label = ttk.Label(self.root, text="正在初始化程序，请稍候...", 
                                      font=("Arial", 12))
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update()
        
        # 创建UI（先创建界面，后初始化耗时的组件）
        self.create_widgets()
        
        # 在后台线程中初始化耗时的组件
        thread = threading.Thread(target=self.delayed_init, daemon=True)
        thread.start()
    
    def delayed_init(self):
        """延迟初始化耗时的组件"""
        try:
            # 第一步：检查并修复 docusaurus.config.js 配置文件
            self.check_and_fix_docusaurus_config()
            
            # 第二步：初始化管理器（这里可能会耗时）
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
                "在线部署"
            ]
            self.current_step = 0
            
            # 在主线程中完成初始化
            self.root.after(0, self.finish_init)
            
        except Exception as e:
            # 在主线程中显示错误
            self.root.after(0, lambda: self.show_init_error(str(e)))
    
    def check_and_fix_docusaurus_config(self):
        """检查并修复 docusaurus.config.js 配置文件"""
        config_path = self.project_path / "docusaurus.config.js"
        
        if not config_path.exists():
            self.log(f"⚠️  配置文件不存在: {config_path}", "warning")
            return
        
        try:
            # 读取文件内容
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否是MDX格式（包含YAML frontmatter）
            if content.strip().startswith('---'):
                self.log("⚠️  检测到 docusaurus.config.js 被写入了MDX内容", "warning")
                self.log("🔄 正在恢复为正确的JavaScript配置...", "info")
                
                # 创建正确的JavaScript配置
                fixed_content = self.create_correct_docusaurus_config()
                
                # 备份原文件
                backup_path = config_path.with_suffix('.js.mdx_backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"📁 已备份原文件到: {backup_path}", "info")
                
                # 写入修复后的文件
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self.log("✅ 配置文件已从MDX格式修复为JavaScript格式", "success")
                return True
            
            # 检查是否是有效的JavaScript
            if not self.is_valid_javascript_config(content):
                self.log("⚠️  检测到 docusaurus.config.js 格式可能有问题", "warning")
                self.log("🔄 正在修复JavaScript配置...", "info")
                
                # 尝试修复
                fixed_content = self.fix_javascript_config(content)
                
                # 备份原文件
                backup_path = config_path.with_suffix('.js.invalid_backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"📁 已备份原文件到: {backup_path}", "info")
                
                # 写入修复后的文件
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self.log("✅ 配置文件已修复为有效的JavaScript格式", "success")
                return True
            
            self.log("✅ docusaurus.config.js 配置文件正常", "success")
            return False
            
        except Exception as e:
            self.log(f"❌ 检查配置文件失败: {str(e)}", "error")
            return False
    
    def is_valid_javascript_config(self, content):
        """检查是否是有效的JavaScript配置"""
        # 检查是否包含基本的JavaScript结构
        checks = [
            ('const config =', '缺少 config 定义'),
            ('module.exports = config', '缺少 module.exports'),
            ('title:', '缺少 title 配置'),
            ('presets:', '缺少 presets 配置'),
        ]
        
        for check_str, error_msg in checks:
            if check_str not in content:
                self.log(f"❌ {error_msg}", "debug")
                return False
        
        return True
    
    def fix_javascript_config(self, content):
        """修复JavaScript配置"""
        # 尝试从原内容中提取有用的部分
        import re
        
        navbar_items = []
        
        # 查找 items: [ ... ] 部分
        pattern = r'items:\s*\[(.*?)\]'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            items_content = match.group(1)
            # 提取每个项目
            item_pattern = r'\{[^}]*type:\s*[\'\"](doc|search)[\'\"][^}]*\}'
            items = re.findall(item_pattern, items_content, re.DOTALL)
            
            for item in items:
                # 提取标签和文档ID
                label_match = re.search(r'label:\s*[\'\"]([^\'\"]+)[\'\"]', item)
                doc_id_match = re.search(r'docId:\s*[\'\"]([^\'\"]+)[\'\"]', item)
                type_match = re.search(r'type:\s*[\'\"]([^\'\"]+)[\'\"]', item)
                position_match = re.search(r'position:\s*[\'\"]([^\'\"]+)[\'\"]', item)
                
                if label_match and type_match:
                    item_data = {
                        'type': type_match.group(1),
                        'label': label_match.group(1),
                    }
                    
                    if doc_id_match:
                        item_data['docId'] = doc_id_match.group(1)
                    
                    if position_match:
                        item_data['position'] = position_match.group(1)
                    
                    navbar_items.append(item_data)
        
        # 创建新的配置
        fixed_content = self.create_correct_docusaurus_config(navbar_items)
        
        return fixed_content
    
    def create_correct_docusaurus_config(self, navbar_items=None):
        """创建正确的JavaScript配置"""
        if navbar_items is None:
            navbar_items = [
                {
                    'type': 'doc',
                    'docId': 'Denti-Pro安装总教程/main-program-installation-guide',
                    'position': 'left',
                    'label': '总文档中心',
                },
                {
                    'type': 'doc',
                    'docId': 'Denti-Pro更新日志/changelog-index',
                    'position': 'left',
                    'label': '更新日志',
                },
                {
                    'type': 'search',
                    'position': 'right',
                },
            ]
        
        # 构建导航栏项目字符串
        items_lines = []
        for item in navbar_items:
            if item['type'] == 'doc':
                items_lines.append(f"""          {{
            type: 'doc',
            docId: '{item['docId']}',
            position: '{item['position']}',
            label: '{item['label']}',
          }},""")
            elif item['type'] == 'search':
                items_lines.append(f"""          {{
            type: 'search',
            position: '{item['position']}',
          }},""")
        
        items_content = "\n".join(items_lines)
        
        config = f"""// @ts-check
// `@ts-check` 启用TypeScript类型检查（可选）

/** @type {{import('@docusaurus/types').Config}} */
const config = {{
  title: 'ToothMen文档系统',
  tagline: 'ToothMen官方说明文档',
  favicon: 'img/favicon.ico',

  // 设置生产环境的URL
  url: 'https://your-docusaurus-site.example.com',
  // 设置基础URL路径（如果部署在子路径下）
  baseUrl: '/',

  // GitHub pages部署配置
  organizationName: 'toothmen', // 通常是你的GitHub用户名
  projectName: 'toothmen-docs', // 通常是你的仓库名

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // 即使你使用国际化的英文网站，也可以保留这个配置
  i18n: {{
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  }},

  presets: [
    [
      'classic',
      /** @type {{import('@docusaurus/preset-classic').Options}} */
      ({{
        docs: {{
          sidebarPath: require.resolve('./sidebars.js'),
          // 如果需要，可以取消注释下面的配置
          // routeBasePath: '/', // 将docs设置为根路径
          // editUrl: 'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        }},
        blog: false, // 禁用博客功能
        theme: {{
          customCss: require.resolve('./src/css/custom.css'),
        }},
      }}),
    ],
  ],

  themeConfig:
    /** @type {{import('@docusaurus/preset-classic').ThemeConfig}} */
    ({{
      // 替换为你的项目社交链接
      navbar: {{
        title: 'ToothMen文档',
        logo: {{
          alt: 'ToothMen Logo',
          src: 'img/logo.svg',
        }},
        items: [
{items_content}
        ],
      }},
      footer: {{
        style: 'dark',
        links: [
          {{
            title: '文档',
            items: [
              {{
                label: '文档首页',
                to: '/docs',
              }},
            ],
          }},
        ],
        copyright: `Copyright © ${{new Date().getFullYear()}} ToothMen. Built with Docusaurus.`,
      }},
    }}),

  plugins: [
    // 本地搜索插件
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      {{
        hashed: true,
        language: ["en", "zh"],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      }},
    ],
  ],
}};

module.exports = config;"""
        
        return config
    
    def finish_init(self):
        """完成初始化"""
        # 隐藏加载提示
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()
        
        # 刷新文件夹结构
        self.refresh_folder_structure()
        
        # 记录日志
        self.log("✅ 程序初始化完成", "success")
    
    def show_init_error(self, error_msg):
        """显示初始化错误"""
        if hasattr(self, 'loading_label'):
            self.loading_label.destroy()
        
        messagebox.showerror("初始化错误", f"程序初始化失败:\n{error_msg}")
        self.log(f"❌ 初始化失败: {error_msg}", "error")
        
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
        
        # 第一行：主要功能按钮
        row1_frame = ttk.Frame(control_frame)
        row1_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 清理缓存按钮（第一行第一个）
        self.clean_cache_btn = ttk.Button(row1_frame, text="🧹 清理缓存", command=self.clean_cache)
        self.clean_cache_btn.grid(row=0, column=0, padx=5)
        
        # 检测MDX语法按钮（第一行第二个）
        self.check_mdx_btn = ttk.Button(row1_frame, text="检测MDX语法", command=self.check_mdx_syntax)
        self.check_mdx_btn.grid(row=0, column=1, padx=5)
        
        # 开始流程按钮（第一行第三个）- 启用下面的按钮
        self.start_workflow_btn = ttk.Button(row1_frame, text="开始流程", command=self.start_workflow)
        self.start_workflow_btn.grid(row=0, column=2, padx=5)
        
        # 结束流程按钮（第一行第四个）
        self.deploy_end_btn = ttk.Button(row1_frame, text="结束流程", command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=3, padx=5)
        
        # 验证部署按钮（第一行第五个）- 位置调整（删除开始部署按钮）
        self.verify_deploy_btn = ttk.Button(row1_frame, text="验证部署", command=self.verify_deployment)
        self.verify_deploy_btn.grid(row=0, column=4, padx=5)
        
        # 第二行：部署步骤按钮
        row2_frame = ttk.Frame(control_frame)
        row2_frame.grid(row=1, column=0, sticky=tk.W)
        
        # 部署步骤按钮（使用默认步骤）
        if not hasattr(self, 'deployment_steps'):
            self.deployment_steps = ["刷新文件结构", "生成侧边栏", "本地构建测试", "本地预览", "在线部署"]
        
        if not hasattr(self, 'step_buttons'):
            self.step_buttons = []
        
        # 如果step_buttons为空，创建按钮
        if len(self.step_buttons) == 0:
            for i, step in enumerate(self.deployment_steps):
                btn = ttk.Button(row2_frame, text=step, command=lambda s=step: self.execute_step(s), state=tk.DISABLED)
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
            
            # 启用保存排序按钮
            self.btn_save_sort.config(state=tk.NORMAL)
            
            # 初始禁用所有排序按钮（等待用户选择）
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
    
    def start_workflow(self):
        """开始流程 - 启用第一个部署步骤按钮（顺序执行模式）"""
        self.log("🔓 开始流程：启用第一个部署步骤按钮", "info")
        self.log("📋 请按顺序点击下面的按钮：", "info")
        self.log("  1. 刷新文件结构", "info")
        self.log("  2. 生成侧边栏", "info")
        self.log("  3. 本地构建测试", "info")
        self.log("  4. 本地预览", "info")
        self.log("  5. 在线部署", "info")
        
        # 调试信息：检查step_buttons状态
        self.log(f"🔍 调试：step_buttons数量 = {len(self.step_buttons) if self.step_buttons else 0}", "debug")
        
        # 启用第一个部署步骤按钮（刷新文件结构）
        if self.step_buttons and len(self.step_buttons) > 0:
            self.log(f"🔍 调试：正在启用按钮 '{self.deployment_steps[0]}'", "debug")
            self.step_buttons[0].config(state=tk.NORMAL)
            # 检查按钮状态
            btn_state = self.step_buttons[0]["state"]
            self.log(f"🔍 调试：按钮状态 = {btn_state}", "debug")
        else:
            self.log("❌ 错误：step_buttons列表为空或无效", "error")
            return
        
        # 禁用开始流程按钮，启用结束流程按钮
        self.start_workflow_btn.config(state=tk.DISABLED)
        self.deploy_end_btn.config(state=tk.NORMAL)
        
        self.log("✅ 第一个步骤按钮已启用，请点击'刷新文件结构'开始", "success")
    

    
    def end_deployment(self):
        """结束部署流程"""
        self.deploy_end_btn.config(state=tk.DISABLED)
        self.start_workflow_btn.config(state=tk.NORMAL)  # 重新启用开始流程按钮
        
        # 重置当前步骤索引
        self.current_step_index = None
        
        # 禁用所有步骤按钮
        for btn in self.step_buttons:
            btn.config(state=tk.DISABLED)
        
        self.log("🛑 部署流程已结束，所有按钮已重置", "info")
    
    def execute_step(self, step):
        """执行部署步骤"""
        self.log(f"▶️  执行步骤: {step}", "info")
        
        # 记录当前步骤索引
        step_index = self.deployment_steps.index(step)
        self.current_step_index = step_index
        
        # 根据步骤执行相应操作
        if step == "刷新文件结构":
            self.refresh_folder_structure()
            # 立即启用下一个按钮（因为refresh_folder_structure是同步的）
            self.enable_next_step()
        elif step == "生成侧边栏":
            self.generate_sidebar()
        elif step == "本地构建测试":
            self.local_build_test()
        elif step == "本地预览":
            self.local_preview()
        elif step == "在线部署":
            self.online_deploy()
    
    def enable_next_step(self):
        """启用下一个步骤按钮"""
        if hasattr(self, 'current_step_index') and self.current_step_index is not None:
            # 禁用当前按钮
            self.step_buttons[self.current_step_index].config(state=tk.DISABLED)
            
            # 启用下一个按钮
            next_index = self.current_step_index + 1
            if next_index < len(self.step_buttons):
                self.step_buttons[next_index].config(state=tk.NORMAL)
                self.log(f"✅ 步骤完成，已启用下一个按钮: {self.deployment_steps[next_index]}", "success")
            else:
                self.log("✅ 所有部署步骤已完成", "success")
        else:
            self.log("⚠️  无法找到当前步骤索引", "warning")
    
    def generate_sidebar(self):
        """生成侧边栏"""
        def _generate_sidebar():
            self.log("📋 开始生成侧边栏...", "info")
            try:
                self.deployment_manager.update_sidebars()
                self.log("✅ 侧边栏生成完成", "success")
                # 完成后启用下一个步骤
                self.root.after(0, self.enable_next_step)
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
                    # 完成后启用下一个步骤
                    self.root.after(0, self.enable_next_step)
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
                success, message = self.deployment_manager.local_preview()
                if success:
                    self.log(f"✅ {message}", "success")
                    # 完成后启用下一个步骤
                    self.root.after(0, self.enable_next_step)
                else:
                    self.log(f"❌ {message}", "error")
            except Exception as e:
                self.log(f"❌ 启动本地预览失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_local_preview)
        thread.daemon = True
        thread.start()
    
    def online_deploy(self):
        """在线部署 - 执行服务端部署工作"""
        def _online_deploy():
            self.log("🌐 开始在线部署...", "info")
            self.log("=" * 60, "info")
            
            try:
                # 步骤0: 检查并清理Git锁文件
                self.log("📋 步骤0: 检查Git锁文件", "info")
                lock_file = self.project_path / ".git" / "index.lock"
                if lock_file.exists():
                    self.log(f"⚠️  发现Git锁文件: {lock_file}", "warning")
                    try:
                        lock_file.unlink()
                        self.log("✅ 已清理Git锁文件", "success")
                    except Exception as e:
                        self.log(f"❌ 无法清理Git锁文件: {str(e)}", "error")
                        self.log("ℹ️  请手动删除锁文件后重试", "info")
                        return
                
                # 步骤1: 检查Git状态
                self.log("📋 步骤1: 检查Git状态", "info")
                success1, output1 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path, ["status", "--short"]
                )
                if success1:
                    self.log("✅ Git状态正常", "success")
                    if output1.strip():
                        self.log(f"📊 Git状态:\n{output1}", "info")
                    else:
                        self.log("📊 Git状态: 没有未提交的更改", "info")
                else:
                    self.log(f"❌ Git状态检查失败: {output1}", "error")
                    return
                
                # 步骤2: 添加所有更改
                self.log("📋 步骤2: 添加所有更改", "info")
                success2, output2 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path, ["add", "."]
                )
                if success2:
                    self.log("✅ 已添加所有更改", "success")
                else:
                    self.log(f"❌ 添加更改失败: {output2}", "error")
                    return
                
                # 步骤3: 提交更改
                self.log("📋 步骤3: 提交更改", "info")
                commit_message = f"自动部署更新 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                success3, output3 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path, ["commit", "-m", commit_message]
                )
                if success3:
                    self.log(f"✅ 已提交更改: {commit_message}", "success")
                else:
                    # 检查是否是"没有更改可提交"的情况
                    error_lower = output3.lower()
                    if "nothing to commit" in error_lower or "working tree clean" in error_lower:
                        self.log("ℹ️  没有需要提交的更改，继续执行推送", "info")
                        # 继续执行，不返回
                    else:
                        self.log(f"❌ 提交更改失败: {output3}", "error")
                        return
                
                # 步骤4: 推送到远程仓库（带重试机制）
                self.log("📋 步骤4: 推送到远程仓库", "info")
                
                # 先检查网络连接（使用Git命令测试，更准确）
                self.log("🔍 检查网络连接...", "info")
                
                # 方案1: 使用Git命令测试连接（最准确）
                self.log("1. 使用Git命令测试连接...", "info")
                success_git_test, output_git_test = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["ls-remote", "https://github.com/juemin7-star/toothmen-docs.git", "HEAD"],
                    timeout=15  # 15秒超时
                )
                
                if success_git_test:
                    self.log("✅ Git连接测试成功", "success")
                    git_connection_ok = True
                else:
                    self.log(f"❌ Git连接测试失败: {output_git_test[:100]}...", "error")
                    git_connection_ok = False
                
                # 方案2: 使用socket测试（备用）
                self.log("2. 使用socket测试端口连接...", "info")
                import socket
                
                connections_to_check = [
                    ("github.com", 443),  # HTTPS
                    ("github.com", 22),   # SSH
                ]
                
                socket_connection_ok = False
                for host, port in connections_to_check:
                    try:
                        socket.create_connection((host, port), timeout=10)
                        self.log(f"✅ 可以连接到 {host}:{port}", "success")
                        socket_connection_ok = True
                        break
                    except Exception as e:
                        self.log(f"⚠️  无法连接到 {host}:{port}: {str(e)}", "warning")
                
                # 综合判断
                if not git_connection_ok and not socket_connection_ok:
                    self.log("❌ 网络连接失败", "error")
                    self.log("ℹ️  请检查网络连接后重试", "info")
                    return
                elif git_connection_ok:
                    self.log("✅ 网络连接正常（Git测试通过）", "success")
                elif socket_connection_ok:
                    self.log("⚠️  网络连接可能有问题（Git测试失败，但socket测试通过）", "warning")
                    self.log("ℹ️  可能是Git配置问题或网络限制", "info")
                    # 继续尝试，但记录警告
                
                # 尝试推送（最多重试3次）
                max_retries = 3
                push_success = False
                push_output = ""
                
                for attempt in range(max_retries):
                    if attempt > 0:
                        self.log(f"🔄 第{attempt+1}次重试推送...", "info")
                        import time
                        time.sleep(2)  # 等待2秒后重试
                    
                    # 先尝试推送到master分支
                    success_master, output_master = self.deployment_manager.run_command(
                        self.deployment_manager.git_path, ["push", "origin", "master"]
                    )
                    
                    if success_master:
                        self.log("✅ 已推送到远程仓库 (master分支)", "success")
                        push_success = True
                        push_output = output_master
                        break
                    else:
                        # 检查错误类型
                        error_lower = output_master.lower()
                        
                        # 1. SSH主机密钥验证失败
                        if "host key verification failed" in error_lower:
                            self.log(f"🔑 SSH主机密钥验证失败 (尝试 {attempt+1}/{max_retries})", "warning")
                            self.log("ℹ️  正在尝试修复SSH主机密钥...", "info")
                            
                            # 尝试清除SSH已知主机
                            try:
                                import subprocess
                                # 清除github.com的SSH主机密钥
                                subprocess.run(["ssh-keygen", "-R", "github.com"], 
                                             capture_output=True, text=True, shell=True)
                                self.log("✅ 已清除SSH主机密钥", "success")
                            except Exception as e:
                                self.log(f"⚠️  无法清除SSH主机密钥: {str(e)}", "warning")
                            
                            # 不要切换到HTTPS方式！坚持使用SSH
                            self.log("ℹ️  坚持使用SSH方式（443端口可能被阻止）", "info")
                            
                            # 尝试手动接受SSH主机密钥
                            try:
                                import subprocess
                                # 使用StrictHostKeyChecking=no强制接受主机密钥
                                subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "-T", "git@github.com"], 
                                             capture_output=True, text=True, shell=True, timeout=10)
                                self.log("✅ 已接受SSH主机密钥", "success")
                            except Exception as e:
                                self.log(f"⚠️  无法接受SSH主机密钥: {str(e)}", "warning")
                            
                            # 重新尝试SSH推送
                            self.log("ℹ️  重新尝试SSH推送...", "info")
                            continue
                        
                        # 2. 网络连接问题（特别是443端口连接失败）
                        elif "unable to access" in error_lower or "connection" in error_lower or "port 443" in error_lower or "timed out" in error_lower:
                            self.log(f"⚠️  网络连接问题 (尝试 {attempt+1}/{max_retries}): {output_master[:100]}...", "warning")
                            
                            # 分析具体错误
                            if "port 443" in error_lower:
                                self.log("🔍 错误分析: 443端口连接失败", "info")
                                self.log("ℹ️  可能原因: 防火墙阻止、网络代理、SSL证书问题", "info")
                                
                                # 如果是第一次尝试，尝试切换到SSH方式
                                if attempt == 0:
                                    self.log("🔑 尝试切换到SSH方式...", "info")
                                    success_ssh, output_ssh = self.deployment_manager.run_command(
                                        self.deployment_manager.git_path,
                                        ["remote", "set-url", "origin", "git@github.com:juemin7-star/toothmen-docs.git"]
                                    )
                                    
                                    if success_ssh:
                                        self.log("✅ 已切换到SSH方式", "success")
                                        # 重新尝试推送
                                        continue
                                    else:
                                        self.log(f"❌ 切换到SSH失败: {output_ssh}", "error")
                            
                            elif "timed out" in error_lower:
                                self.log("🔍 错误分析: 连接超时", "info")
                                self.log("ℹ️  可能原因: 网络不稳定、服务器响应慢、网络限制", "info")
                                self.log("ℹ️  建议: 等待后重试或检查网络连接", "info")
                            
                            # 等待后重试
                            import time
                            wait_time = (attempt + 1) * 3  # 递增等待时间
                            self.log(f"⏳ 等待 {wait_time} 秒后重试...", "info")
                            time.sleep(wait_time)
                            
                            continue
                        
                        # 3. 其他错误，尝试main分支
                        else:
                            self.log("⚠️  master分支推送失败，尝试main分支...", "warning")
                            success_main, output_main = self.deployment_manager.run_command(
                                self.deployment_manager.git_path, ["push", "origin", "main"]
                            )
                            
                            if success_main:
                                self.log("✅ 已推送到远程仓库 (main分支)", "success")
                                push_success = True
                                push_output = output_main
                                break
                            else:
                                self.log(f"❌ 推送失败 (尝试 {attempt+1}/{max_retries}): {output_main[:100]}...", "error")
                
                if not push_success:
                    self.log("❌ 推送失败，已重试3次", "error")
                    self.log("ℹ️  可能的原因：", "info")
                    self.log("  1. 网络连接问题", "info")
                    self.log("  2. GitHub认证问题", "info")
                    self.log("  3. 仓库权限问题", "info")
                    self.log("ℹ️  请手动执行以下命令测试：", "info")
                    self.log(f'  cd "{self.project_path}"', "info")
                    self.log('  git push origin master', "info")
                    return
                
                self.log("=" * 60, "info")
                self.log("🎉 在线部署完成！", "success")
                self.log("📊 执行结果:", "info")
                self.log("  ✅ Git锁文件检查完成", "info")
                self.log("  ✅ Git状态检查完成", "info")
                self.log("  ✅ 所有更改已添加", "info")
                self.log("  ✅ 更改已提交", "info")
                self.log("  ✅ 已推送到远程仓库", "info")
                self.log("=" * 60, "info")
                
                # 完成后启用下一个步骤（如果有的话）
                self.root.after(0, self.enable_next_step)
                
            except Exception as e:
                self.log(f"❌ 在线部署失败: {str(e)}", "error")
        
        # 在新线程中执行
        thread = threading.Thread(target=_online_deploy)
        thread.daemon = True
        thread.start()
    
    def verify_deployment(self):
        """验证部署 - 直接打开Cloudflare网站"""
        self.log("🔍 开始验证部署...", "info")
        
        def _verify_deployment():
            try:
                import webbrowser
                import urllib.request
                import urllib.error
                import ssl
                
                # Cloudflare网站地址
                cloudflare_url = "https://docs.toothmen.com"
                
                # 1. 先尝试打开网站
                self.log(f"1. 正在打开Cloudflare网站: {cloudflare_url}", "info")
                try:
                    webbrowser.open(cloudflare_url)
                    self.log("✅ 已打开浏览器访问网站", "success")
                except Exception as e:
                    self.log(f"⚠️  无法自动打开浏览器: {str(e)}", "warning")
                    self.log(f"ℹ️  请手动访问: {cloudflare_url}", "info")
                
                # 2. 检查网站是否可访问
                self.log("\n2. 检查网站是否可访问...", "info")
                
                # 创建不验证SSL的上下文（仅用于测试）
                context = ssl._create_unverified_context()
                
                # 尝试多个可能的URL（Cloudflare相关）
                possible_urls = [
                    "https://docs.toothmen.com/",
                    "https://docs.toothmen.com",
                    "https://docs.toothmen.com/docs/NEW-26040801-补丁",
                    "https://docs.toothmen.com/docs/NEW-260400901-补丁"
                ]
                
                site_accessible = False
                accessible_url = ""
                status_code = 0
                
                for url in possible_urls:
                    try:
                        req = urllib.request.Request(url, method="HEAD")
                        response = urllib.request.urlopen(req, timeout=10, context=context)
                        site_accessible = True
                        accessible_url = url
                        status_code = response.status
                        break
                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            # 404是正常的，Cloudflare可能还在部署中
                            self.log(f"⚠️  网站返回404: {url}", "warning")
                            continue
                        elif e.code == 403:
                            # 403也是正常的，Cloudflare可能还在构建或有限制
                            self.log(f"⚠️  网站返回403: {url} (Cloudflare构建中或访问限制)", "warning")
                            continue
                        else:
                            # 安全地处理错误信息，避免编码问题
                            error_msg = f"网站HTTP错误 {e.code}: {url}"
                            self.log(error_msg, "error")
                            continue
                    except urllib.error.URLError as e:
                        # 安全地处理URL错误，避免编码问题
                        error_msg = f"URL错误: {str(e.reason) if e.reason else str(e)}"
                        self.log(error_msg, "warning")
                        continue
                
                if site_accessible:
                    self.log(f"✅ 网站可访问 (状态码: {status_code}): {accessible_url}", "success")
                else:
                    self.log("❌ 网站无法访问", "error")
                    self.log("ℹ️  可能原因:", "info")
                    self.log("  1. Cloudflare部署中（通常需要5-30分钟）", "info")
                    self.log("  2. 检查Cloudflare Pages设置", "info")
                    self.log("  3. 检查DNS配置是否正确", "info")
                    self.log("  4. 等待几分钟后重试验证", "info")
                
                # 3. 检查Cloudflare Pages状态
                self.log("\n3. 检查Cloudflare Pages状态...", "info")
                self.log("ℹ️  Cloudflare Pages管理页面:", "info")
                self.log("  1. 访问: https://dash.cloudflare.com/", "info")
                self.log("  2. 选择toothmen-docs项目", "info")
                self.log("  3. 查看构建日志和部署状态", "info")
                self.log("ℹ️  部署状态可以在Cloudflare仪表板查看", "info")
                
                # 4. 检查最新提交
                self.log("\n4. 检查最新提交...", "info")
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-1"]
                )
                
                if success:
                    self.log(f"✅ 最新提交: {output.strip()}", "success")
                else:
                    self.log(f"❌ 无法获取最新提交: {output}", "error")
                
                # 5. 检查部署状态
                self.log("\n5. 检查部署状态...", "info")
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["status"]
                )
                
                if success:
                    if "Your branch is up to date" in output:
                        self.log("✅ 分支已同步到远程", "success")
                    else:
                        self.log("⚠️  分支未同步到远程", "warning")
                        self.log("ℹ️  可能需要手动推送", "info")
                else:
                    self.log(f"❌ 无法检查部署状态: {output}", "error")
                
                self.log("\n✅ 部署验证完成", "success")
                self.log(f"🌐 网站地址: {cloudflare_url}", "info")
                self.log("📱 请手动访问网站确认更新效果", "info")
                
            except Exception as e:
                # 安全地处理异常，避免编码问题
                try:
                    error_msg = str(e)
                    # 如果是编码错误，提供更友好的信息
                    if "'ascii' codec" in error_msg:
                        self.log("❌ 部署验证失败: 编码错误（可能是中文字符处理问题）", "error")
                        self.log("ℹ️  网站可能正在构建中，请稍后手动访问确认", "info")
                    else:
                        self.log(f"❌ 部署验证失败: {error_msg}", "error")
                except:
                    self.log("❌ 部署验证失败: 未知错误", "error")
        
        thread = threading.Thread(target=_verify_deployment)
        thread.daemon = True
        thread.start()
    
    # ========== 调试工具方法 ==========
    
    def test_network_connection(self):
        """测试网络连接"""
        self.log("🌐 测试网络连接...", "info")
        
        def _test_network():
            try:
                # 1. 测试Ping
                self.log("1. 测试Ping...", "info")
                success_ping, output_ping = self.deployment_manager.run_command(
                    "ping",
                    ["-n", "4", "github.com"]
                )
                
                if success_ping:
                    self.log("✅ Ping测试成功", "success")
                    # 提取延迟信息
                    if "平均" in output_ping:
                        for line in output_ping.split('\n'):
                            if "平均" in line:
                                self.log(f"网络延迟: {line.strip()}", "info")
                else:
                    self.log("❌ Ping测试失败", "error")
                    self.log("可能原因: 网络断开、DNS问题、防火墙阻止", "warning")
                
                # 2. 测试HTTPS连接
                self.log("\n2. 测试HTTPS连接...", "info")
                try:
                    import urllib.request
                    import urllib.error
                    import ssl
                    
                    # 创建不验证SSL的上下文（仅用于测试）
                    context = ssl._create_unverified_context()
                    req = urllib.request.Request("https://github.com", method="HEAD")
                    
                    try:
                        response = urllib.request.urlopen(req, timeout=10, context=context)
                        self.log(f"✅ HTTPS连接成功 (状态码: {response.status})", "success")
                    except urllib.error.URLError as e:
                        self.log(f"❌ HTTPS连接失败: {str(e)}", "error")
                except Exception as e:
                    self.log(f"HTTPS测试异常: {str(e)}", "error")
                
                # 3. 检查Git配置
                self.log("\n3. 检查Git配置...", "info")
                
                # 检查远程仓库
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.log("远程仓库配置:", "info")
                    self.log(output_remote, "info")
                else:
                    self.log("❌ 无法获取远程仓库配置", "error")
                
                # 检查代理设置
                success_proxy, output_proxy = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["config", "--global", "http.proxy"]
                )
                
                if success_proxy and output_proxy.strip():
                    self.log(f"⚠️ 检测到Git代理设置: {output_proxy.strip()}", "warning")
                else:
                    self.log("✅ 无Git代理设置", "success")
                
                # 4. 测试Git连接
                self.log("\n4. 测试Git连接...", "info")
                success_git, output_git = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["ls-remote", "https://github.com/juemin7-star/toothmen-docs.git", "--heads"]
                )
                
                if success_git:
                    self.log("✅ Git连接成功", "success")
                else:
                    self.log("❌ Git连接失败", "error")
                    self.log(f"错误详情: {output_git}", "error")
                    
                    # 分析错误类型
                    error_lower = output_git.lower()
                    if "permission denied" in error_lower or "authentication failed" in error_lower:
                        self.log("\n🔐 检测到认证问题:", "warning")
                        self.log("  1. 检查SSH密钥配置", "info")
                        self.log("  2. 检查GitHub Token是否有效", "info")
                        self.log("  3. 检查远程仓库权限", "info")
                    elif "connection" in error_lower or "timeout" in error_lower or "could not connect" in error_lower:
                        self.log("\n🌐 检测到网络连接问题:", "warning")
                        self.log("  1. 检查网络连接", "info")
                        self.log("  2. 检查防火墙设置", "info")
                        self.log("  3. 尝试使用VPN或切换网络", "info")
                    elif "proxy" in error_lower:
                        self.log("\n🔄 检测到代理问题:", "warning")
                        self.log("  清除代理: git config --global --unset http.proxy", "info")
                
                # 5. 检查本地提交状态
                self.log("\n5. 检查本地提交状态...", "info")
                
                # 获取最后提交
                success_log, output_log = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-1"]
                )
                
                if success_log:
                    self.log(f"最后提交: {output_log.strip()}", "info")
                else:
                    self.log("无法获取提交信息", "warning")
                
                # 检查未推送的提交
                success_unpushed, output_unpushed = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "origin/master..HEAD", "--oneline"]
                )
                
                if success_unpushed and output_unpushed.strip():
                    self.log("⚠️ 有未推送的提交:", "warning")
                    self.log(output_unpushed, "info")
                else:
                    self.log("✅ 所有提交已推送或没有新提交", "success")
                
                # 6. 提供解决方案
                self.log("\n" + "=" * 60, "info")
                self.log("💡 解决方案建议:", "info")
                self.log("=" * 60, "info")
                
                self.log("\n🔹 如果HTTPS连接失败:", "info")
                self.log("  1. 切换到SSH方式（点击'切换到SSH'按钮）", "info")
                self.log("  2. 检查防火墙设置", "info")
                self.log("  3. 清除代理: git config --global --unset http.proxy", "info")
                self.log("  4. 尝试使用VPN或手机热点", "info")
                
                self.log("\n🔹 如果认证失败:", "info")
                self.log("  1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email\"", "info")
                self.log("  2. 添加公钥到GitHub", "info")
                self.log("  3. 测试SSH连接: ssh -T git@github.com", "info")
                
                self.log("\n🔹 立即操作:", "info")
                self.log("  1. 使用'切换到SSH'按钮", "info")
                self.log("  2. 使用'手动推送Git'按钮", "info")
                self.log("  3. 检查网络连接后重试", "info")
                
                self.log("\n✅ 网络连接测试完成！", "success")
                
            except Exception as e:
                self.log(f"❌ 网络连接测试失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_test_network)
        thread.daemon = True
        thread.start()
    
    def check_git_status(self):
        """检查Git状态"""
        self.log("🔍 检查Git状态...", "info")
        
        def _check_git():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["status", "--short"]
                )
                
                if success:
                    if output.strip():
                        self.log("Git状态:", "info")
                        self.log(output, "info")
                    else:
                        self.log("✅ 工作区干净，没有未提交的更改", "success")
                else:
                    self.log(f"❌ Git状态检查失败: {output}", "error")
                    
            except Exception as e:
                self.log(f"❌ Git状态检查异常: {str(e)}", "error")
        
        thread = threading.Thread(target=_check_git)
        thread.daemon = True
        thread.start()
    
    def show_git_log(self):
        """查看Git日志"""
        self.log("📊 查看Git日志...", "info")
        
        def _show_log():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-10"]
                )
                
                if success:
                    self.log("最近10次提交:", "info")
                    self.log(output, "info")
                else:
                    self.log(f"❌ 获取Git日志失败: {output}", "error")
                    
            except Exception as e:
                self.log(f"❌ 获取Git日志异常: {str(e)}", "error")
        
        thread = threading.Thread(target=_show_log)
        thread.daemon = True
        thread.start()
    
    def manual_git_push(self):
        """手动推送Git"""
        self.log("🔄 手动推送Git...", "info")
        
        def _manual_push():
            try:
                # 先检查是否有未提交的更改
                success_status, output_status = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["status", "--short"]
                )
                
                if success_status and output_status.strip():
                    self.log("检测到未提交的更改:", "info")
                    self.log(output_status, "info")
                    
                    # 询问是否先提交
                    self.log("ℹ️  建议先提交更改再推送", "info")
                
                # 执行推送
                self.log("正在推送到远程仓库...", "info")
                success_push, output_push = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["push", "origin", "master"]
                )
                
                if success_push:
                    self.log("✅ Git推送成功", "success")
                    self.log(output_push, "info")
                else:
                    self.log(f"❌ Git推送失败: {output_push}", "error")
                    
                    # 检查错误类型
                    error_lower = output_push.lower()
                    
                    # 1. SSH主机密钥验证失败
                    if "host key verification failed" in error_lower:
                        self.log("🔑 SSH主机密钥验证失败", "warning")
                        self.log("ℹ️  解决方案:", "info")
                        self.log("  1. 清除SSH主机密钥: ssh-keygen -R github.com", "info")
                        self.log("  2. 切换到HTTPS方式:", "info")
                        self.log("     git remote set-url origin https://github.com/juemin7-star/toothmen-docs.git", "info")
                        self.log("  3. 使用'切换到SSH'按钮修复SSH连接", "info")
                    
                    # 2. 如果master分支失败，尝试main分支
                    elif "src refspec main does not match any" in output_push:
                        self.log("⚠️  master分支推送失败，尝试main分支...", "warning")
                        success_main, output_main = self.deployment_manager.run_command(
                            self.deployment_manager.git_path,
                            ["push", "origin", "main"]
                        )
                        
                        if success_main:
                            self.log("✅ 已推送到远程仓库 (main分支)", "success")
                        else:
                            self.log(f"❌ main分支推送失败: {output_main}", "error")
                    
                    # 3. 其他错误
                    else:
                        self.log("ℹ️  请检查Git配置和网络连接", "info")
                    
            except Exception as e:
                self.log(f"❌ Git推送异常: {str(e)}", "error")
        
        thread = threading.Thread(target=_manual_push)
        thread.daemon = True
        thread.start()
    
    def diagnose_git_connection(self):
        """Git连接诊断"""
        self.log("🔧 Git连接诊断...", "info")
        
        def _diagnose():
            try:
                # 1. 检查Git配置
                self.log("1. 检查Git配置...", "info")
                
                # 检查用户名
                success_user, output_user = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["config", "--global", "user.name"]
                )
                
                if success_user and output_user.strip():
                    self.log(f"✅ Git用户名: {output_user.strip()}", "success")
                else:
                    self.log("❌ Git用户名未设置", "error")
                
                # 检查邮箱
                success_email, output_email = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["config", "--global", "user.email"]
                )
                
                if success_email and output_email.strip():
                    self.log(f"✅ Git邮箱: {output_email.strip()}", "success")
                else:
                    self.log("❌ Git邮箱未设置", "error")
                
                # 2. 检查远程仓库
                self.log("\n2. 检查远程仓库...", "info")
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.log("远程仓库配置:", "info")
                    self.log(output_remote, "info")
                else:
                    self.log("❌ 无法获取远程仓库配置", "error")
                
                # 3. 检查网络连接
                self.log("\n3. 检查网络连接...", "info")
                success_ping, output_ping = self.deployment_manager.run_command(
                    "ping",
                    ["-n", "2", "github.com"]
                )
                
                if success_ping:
                    self.log("✅ 可以连接到GitHub", "success")
                else:
                    self.log("❌ 无法连接到GitHub", "error")
                
                # 4. 测试Git操作
                self.log("\n4. 测试Git操作...", "info")
                success_fetch, output_fetch = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["fetch", "--dry-run"]
                )
                
                if success_fetch:
                    self.log("✅ Git fetch测试成功", "success")
                else:
                    self.log(f"❌ Git fetch测试失败: {output_fetch}", "error")
                
                # 5. 检查认证
                self.log("\n5. 检查认证...", "info")
                success_ls, output_ls = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["ls-remote", "https://github.com/juemin7-star/toothmen-docs.git", "HEAD"]
                )
                
                if success_ls:
                    self.log("✅ Git认证成功", "success")
                else:
                    self.log(f"❌ Git认证失败: {output_ls}", "error")
                    
                    # 分析错误
                    error_lower = output_ls.lower()
                    if "permission denied" in error_lower:
                        self.log("🔐 认证问题: 权限被拒绝", "warning")
                        self.log("  可能原因: SSH密钥问题、Token过期、仓库权限不足", "info")
                    elif "connection" in error_lower:
                        self.log("🌐 网络问题: 连接失败", "warning")
                        self.log("  可能原因: 网络断开、防火墙、代理设置", "info")
                
                # 6. 提供解决方案
                self.log("\n" + "=" * 60, "info")
                self.log("💡 诊断结果和建议:", "info")
                self.log("=" * 60, "info")
                
                self.log("\n🔹 如果认证失败:", "info")
                self.log("  1. 使用'切换到SSH'按钮", "info")
                self.log("  2. 检查GitHub Token或SSH密钥", "info")
                self.log("  3. 重新配置Git认证", "info")
                
                self.log("\n🔹 如果网络连接失败:", "info")
                self.log("  1. 检查网络连接", "info")
                self.log("  2. 检查防火墙设置", "info")
                self.log("  3. 尝试使用VPN", "info")
                
                self.log("\n🔹 如果配置错误:", "info")
                self.log("  1. 检查Git用户名和邮箱", "info")
                self.log("  2. 检查远程仓库URL", "info")
                self.log("  3. 重新配置Git", "info")
                
                self.log("\n✅ Git连接诊断完成！", "success")
                
            except Exception as e:
                self.log(f"❌ Git连接诊断失败: {str(e)}", "error")
        
        thread = threading.Thread(target=_diagnose)
        thread.daemon = True
        thread.start()
    
    def switch_to_ssh(self):
        """切换到SSH"""
        self.log("🔑 切换到SSH...", "info")
        
        def _switch_ssh():
            try:
                # 1. 显示当前配置
                self.log("当前远程仓库配置:", "info")
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.log(output_remote, "info")
                else:
                    self.log("❌ 无法获取远程仓库配置", "error")
                    return
                
                # 2. 切换到SSH
                self.log("\n正在修改远程URL为SSH...", "info")
                success_switch, output_switch = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "set-url", "origin", "git@github.com:juemin7-star/toothmen-docs.git"]
                )
                
                if success_switch:
                    self.log("✅ 已切换到SSH方式", "success")
                    
                    # 3. 显示新配置
                    self.log("\n新的远程仓库配置:", "info")
                    success_new, output_new = self.deployment_manager.run_command(
                        self.deployment_manager.git_path,
                        ["remote", "-v"]
                    )
                    
                    if success_new:
                        self.log(output_new, "info")
                    else:
                        self.log("⚠️ 无法获取新配置", "warning")
                    
                    # 4. 测试SSH连接
                    self.log("\n测试SSH连接...", "info")
                    success_test, output_test = self.deployment_manager.run_command(
                        "ssh",
                        ["-T", "git@github.com"]
                    )
                    
                    if success_test:
                        self.log("✅ SSH连接成功", "success")
                        self.log(output_test, "info")
                    else:
                        self.log("⚠️ SSH连接测试失败", "warning")
                        self.log("可能需要设置SSH密钥:", "info")
                        self.log("  1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email\"", "info")
                        self.log("  2. 添加公钥到GitHub", "info")
                        self.log("  3. 启动ssh-agent: eval \"$(ssh-agent -s)\"", "info")
                        self.log("  4. 添加私钥: ssh-add ~/.ssh/id_ed25519", "info")
                    
                    # 5. 询问是否立即推送
                    self.log("\n💡 建议:", "info")
                    self.log("  现在可以使用'手动推送Git'按钮进行推送", "info")
                    self.log("  或稍后执行: git push origin master", "info")
                    
                else:
                    self.log(f"❌ 切换到SSH失败: {output_switch}", "error")
                    
            except Exception as e:
                self.log(f"❌ 切换到SSH过程中出现异常: {str(e)}", "error")
        
        thread = threading.Thread(target=_switch_ssh)
        thread.daemon = True
        thread.start()
    
    def clear_npm_cache(self):
        """清除npm缓存"""
        def _clear_npm_cache():
            self.log("🧹 清除npm缓存...", "info")
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.npm_path,
                    ["cache", "clean", "--force"]
                )
                
                if success:
                    self.log("✅ npm缓存已清除", "success")
                else:
                    self.log(f"❌ 清除npm缓存失败: {output}", "error")
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