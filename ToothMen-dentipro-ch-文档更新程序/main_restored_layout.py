#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen文档管理工具 v3.22
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
        self.root.title("ToothMen-DentiPro-中文版·文档管理系统 v3.22")
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
        self.tool_path = self.project_path / "ToothMen-dentipro-ch-文档更新程序"
        self.docs_folder = self.project_path / "docs"  # 直接监控docs文件夹
        self.sidebars_path = self.project_path / "sidebars.js"
        self.sort_config_path = self.tool_path / "sort_config.json"
        
        # 确保docs文件夹存在
        self.docs_folder.mkdir(exist_ok=True)
        
        # 初始化按钮列表（确保在create_widgets之前初始化）
        self.step_buttons = []
        self.deployment_steps = ["保存顺序", "生成侧边栏", "本地构建测试", "本地预览", "在线部署"]
        
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
                "保存顺序",
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
                    'docId': 'install/index',
                    'position': 'left',
                    'label': '总文档中心',
                },
                {
                    'type': 'doc',
                    'docId': 'changelog/index',
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

  markdown: {{
    hooks: {{
      onBrokenMarkdownLinks: 'warn',
    }},
  }},

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
        
        # 启动docs递归监控（自动检测所有子文件夹变化）
        self.start_recursive_docs_monitoring()
        
        # 记录日志
        self.log("✅ 程序初始化完成", "success")
    
    def start_recursive_docs_monitoring(self):
        """启动docs目录递归监控"""
        try:
            self._docs_snapshot = self._build_docs_snapshot()
            self._docs_monitor_interval_ms = 2000  # 2秒轮询一次
            self.root.after(self._docs_monitor_interval_ms, self.check_recursive_docs_changes)
            self.log("👀 已启动docs递归监控（含所有子文件夹）", "info")
        except Exception as e:
            self.log(f"⚠️  启动docs递归监控失败: {str(e)}", "warning")
    
    def _build_docs_snapshot(self):
        """
        构建docs目录递归快照
        仅跟踪目录与文档文件（.md/.mdx），用于检测结构和内容变化
        """
        snapshot = {}
        if not self.docs_folder.exists():
            return snapshot
        
        for path in self.docs_folder.rglob("*"):
            try:
                if path.is_dir():
                    rel = str(path.relative_to(self.docs_folder)).replace("\\", "/")
                    snapshot[f"dir:{rel}"] = path.stat().st_mtime
                elif path.is_file() and (path.suffix.lower() in {".md", ".mdx"}):
                    rel = str(path.relative_to(self.docs_folder)).replace("\\", "/")
                    stat = path.stat()
                    snapshot[f"file:{rel}"] = (stat.st_mtime, stat.st_size)
            except FileNotFoundError:
                # 轮询过程中路径可能被删除，忽略即可
                continue
            except PermissionError:
                continue
        
        return snapshot
    
    def check_recursive_docs_changes(self):
        """递归检测docs目录变化，变化后自动刷新树结构"""
        try:
            current_snapshot = self._build_docs_snapshot()
            if not hasattr(self, "_docs_snapshot"):
                self._docs_snapshot = current_snapshot
            elif current_snapshot != self._docs_snapshot:
                self._docs_snapshot = current_snapshot
                self.refresh_folder_structure()
                self.log("🔄 检测到docs子目录变化，已自动刷新", "info")
        except Exception as e:
            self.log(f"⚠️  docs递归监控异常: {str(e)}", "warning")
        finally:
            interval = getattr(self, "_docs_monitor_interval_ms", 2000)
            self.root.after(interval, self.check_recursive_docs_changes)
    
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
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-中文版·文档管理系统 v3.22", 
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
        
        # 独立按钮：刷新文件结构（不参与流程步骤）
        self.btn_refresh_structure = tk.Button(
            sort_frame, text="🔄 刷新文件结构", command=self.refresh_folder_structure, width=14
        )
        self.btn_refresh_structure.pack(pady=(8, 8))
        
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
        
        # 右侧“保存排序”按钮已按需求移除（仅保留流程里的“保存顺序”步骤）
        self.btn_save_sort = None
        
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
        
        # 检测MDX语法按钮（第一行第一个）
        self.check_mdx_btn = ttk.Button(row1_frame, text="检测MDX语法", command=self.check_mdx_syntax)
        self.check_mdx_btn.grid(row=0, column=0, padx=5)
        
        # 开始流程按钮（第一行第二个）- 启用下面的按钮
        self.start_workflow_btn = ttk.Button(row1_frame, text="开始流程", command=self.start_workflow)
        self.start_workflow_btn.grid(row=0, column=1, padx=5)
        
        # 结束流程按钮（第一行第三个）
        self.deploy_end_btn = ttk.Button(row1_frame, text="结束流程", command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=2, padx=5)
        
        # 验证部署按钮（第一行第四个）
        self.verify_deploy_btn = ttk.Button(row1_frame, text="验证部署", command=self.verify_deployment)
        self.verify_deploy_btn.grid(row=0, column=3, padx=5)
        
        # 第二行：部署步骤按钮
        row2_frame = ttk.Frame(control_frame)
        row2_frame.grid(row=1, column=0, sticky=tk.W)
        
        # 创建部署步骤按钮
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
            try:
                self.log("🧹 开始清理缓存...", "info")
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
            sort_config_path = self.sort_config_path
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
                
                # 获取文件夹内的直接文件和子文件夹
                direct_files = []
                child_folders = []
                for entry in folder_path.iterdir():
                    if entry.is_file() and (entry.name.endswith('.mdx') or entry.name.endswith('.md')):
                        direct_files.append(entry.name)
                    elif entry.is_dir():
                        # 仅显示包含MDX/MD文件的子文件夹（如 2025/2026）
                        has_docs = any(
                            sub.is_file() and (sub.name.endswith('.mdx') or sub.name.endswith('.md'))
                            for sub in entry.iterdir()
                        )
                        if has_docs:
                            child_folders.append(entry.name)
                
                # 按照排序配置文件中的顺序显示子项（子文件夹 + 文件）
                sorted_items = []
                if sort_config_path.exists():
                    # 获取配置文件中的文件顺序
                    config_files = sort_config.get("files", {}).get(folder_name, [])
                    
                    # 先添加配置文件指定的子项（优先子文件夹，其次文件）
                    for item_name in config_files:
                        item_path = folder_path / item_name
                        if item_path.exists() and item_path.is_dir() and item_name in child_folders:
                            sorted_items.append(item_name)
                            continue
                        
                        possible_files = [f"{item_name}.mdx", f"{item_name}.md", item_name]
                        for possible_file in possible_files:
                            file_path = folder_path / possible_file
                            if file_path.exists() and file_path.is_file():
                                sorted_items.append(possible_file)
                                break
                    
                    # 再添加未配置的子文件夹
                    for subfolder_name in sorted(child_folders):
                        if subfolder_name not in sorted_items:
                            sorted_items.append(subfolder_name)
                    
                    # 再添加未配置的文件
                    for file_name in sorted(direct_files):
                        if file_name not in sorted_items:
                            sorted_items.append(file_name)
                else:
                    # 没有配置文件，先子文件夹后文件
                    sorted_items = sorted(child_folders) + sorted(direct_files)
                
                # 添加文件夹到树
                folder_item = self.tree.insert("", "end", text=f"📂 {folder_name}/", values=("文件夹", str(len(sorted_items))))
                
                # 添加子项到树（支持子文件夹和文件）
                for item_name in sorted_items:
                    item_path = folder_path / item_name
                    if item_path.exists() and item_path.is_dir():
                        # 子文件夹节点
                        subfolder_item = self.tree.insert(
                            folder_item, "end", text=f"📂 {item_name}/", values=("子文件夹", "")
                        )
                        # 显示子文件夹内文档（用于可视化确认与排序保存）
                        sub_files = []
                        for sub_file in item_path.iterdir():
                            if sub_file.is_file() and (sub_file.name.endswith('.mdx') or sub_file.name.endswith('.md')):
                                sub_files.append(sub_file.name)
                        
                        # 子文件夹内文件顺序按 sort_config 的 folder/subfolder 键读取
                        subfolder_key = f"{folder_name}/{item_name}"
                        sorted_sub_files = []
                        config_sub_files = sort_config.get("files", {}).get(subfolder_key, []) if sort_config_path.exists() else []
                        for sub_file_base in config_sub_files:
                            possible_sub_files = [f"{sub_file_base}.mdx", f"{sub_file_base}.md", sub_file_base]
                            for psf in possible_sub_files:
                                psf_path = item_path / psf
                                if psf_path.exists() and psf_path.is_file():
                                    sorted_sub_files.append(psf)
                                    break
                        for sub_file_name in sorted(sub_files):
                            if sub_file_name not in sorted_sub_files:
                                sorted_sub_files.append(sub_file_name)
                        
                        for sub_file_name in sorted_sub_files:
                            if sub_file_name.endswith('.mdx'):
                                icon = "📄"
                                file_type = "MDX文件"
                            else:
                                icon = "📝"
                                file_type = "MD文件"
                            self.tree.insert(subfolder_item, "end", text=f"{icon} {sub_file_name}", values=(file_type, "1"))
                    elif item_name.endswith('.mdx'):
                        icon = "📄"
                        file_type = "MDX文件"
                        self.tree.insert(folder_item, "end", text=f"{icon} {item_name}", values=(file_type, "1"))
                    elif item_name.endswith('.md'):
                        icon = "📝"
                        file_type = "MD文件"
                        self.tree.insert(folder_item, "end", text=f"{icon} {item_name}", values=(file_type, "1"))
            
            self.log(f"✅ 文件夹结构已刷新，共检测到 {total_folders} 个文件夹", "success")
            
            # 使用set_button_state方法设置按钮状态
            self.set_button_state(self.btn_save_sort, "normal")
            self.set_button_state(self.btn_folder_up, "disabled")
            self.set_button_state(self.btn_folder_down, "disabled")
            self.set_button_state(self.btn_file_up, "disabled")
            self.set_button_state(self.btn_file_down, "disabled")
            
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
        # 设置按钮为执行中状态
        self.set_button_state(self.start_workflow_btn, "executing")
        
        def _start_workflow():
            try:
                self.log("🔓 开始流程：启用第一个部署步骤按钮", "info")
                self.log("📋 请按顺序点击下面的按钮：", "info")
                self.log("  1. 保存顺序", "info")
                self.log("  2. 生成侧边栏", "info")
                self.log("  3. 本地构建测试", "info")
                self.log("  4. 本地预览", "info")
                self.log("  5. 在线部署", "info")
                
                # 调试信息：检查step_buttons状态
                self.log(f"🔍 调试：step_buttons数量 = {len(self.step_buttons) if self.step_buttons else 0}", "debug")
                
                # 启用第一个部署步骤按钮
                if self.step_buttons and len(self.step_buttons) > 0:
                    self.log(f"🔍 调试：正在启用按钮 '{self.deployment_steps[0]}'", "debug")
                    self.set_button_state(self.step_buttons[0], "normal")
                    # 检查按钮状态
                    btn_state = self.step_buttons[0]["state"]
                    self.log(f"🔍 调试：按钮状态 = {btn_state}", "debug")
                else:
                    self.log("❌ 错误：step_buttons列表为空或无效", "error")
                    self.set_button_state(self.start_workflow_btn, "error")
                    # 1秒后恢复为正常状态
                    self.root.after(1000, lambda: self.set_button_state(self.start_workflow_btn, "normal"))
                    return
                
                # 禁用开始流程按钮，启用结束流程按钮
                self.set_button_state(self.start_workflow_btn, "disabled")
                self.set_button_state(self.deploy_end_btn, "normal")
                
                self.log(f"✅ 第一个步骤按钮已启用，请点击'{self.deployment_steps[0]}'开始", "success")
                self.set_button_state(self.start_workflow_btn, "success")
                # 1秒后恢复为禁用状态（保持禁用）
                self.root.after(1000, lambda: self.set_button_state(self.start_workflow_btn, "disabled"))
                
            except Exception as e:
                self.log(f"❌ 开始流程失败: {str(e)}", "error")
                self.set_button_state(self.start_workflow_btn, "error")
                # 1秒后恢复为正常状态
                self.root.after(1000, lambda: self.set_button_state(self.start_workflow_btn, "normal"))
        
        # 在新线程中执行
        thread = threading.Thread(target=_start_workflow)
        thread.daemon = True
        thread.start()
    

    
    def end_deployment(self):
        """结束部署流程"""
        # 设置按钮为执行中状态
        self.set_button_state(self.deploy_end_btn, "executing")
        
        def _end_deployment():
            try:
                self.set_button_state(self.deploy_end_btn, "disabled")
                self.set_button_state(self.start_workflow_btn, "normal")  # 重新启用开始流程按钮
                
                # 重置当前步骤索引
                self.current_step_index = None
                
                # 禁用所有步骤按钮
                for btn in self.step_buttons:
                    self.set_button_state(btn, "disabled")
                
                self.log("🛑 部署流程已结束，所有按钮已重置", "info")
                self.set_button_state(self.deploy_end_btn, "success")
                # 1秒后恢复为禁用状态（保持禁用）
                self.root.after(1000, lambda: self.set_button_state(self.deploy_end_btn, "disabled"))
                
            except Exception as e:
                self.log(f"❌ 结束流程失败: {str(e)}", "error")
                self.set_button_state(self.deploy_end_btn, "error")
                # 1秒后恢复为禁用状态
                self.root.after(1000, lambda: self.set_button_state(self.deploy_end_btn, "disabled"))
        
        # 在新线程中执行
        thread = threading.Thread(target=_end_deployment)
        thread.daemon = True
        thread.start()
    
    def execute_step(self, step):
        """执行部署步骤"""
        # 记录当前步骤索引
        step_index = self.deployment_steps.index(step)
        self.current_step_index = step_index
        
        # 设置当前按钮为执行中状态
        if step_index < len(self.step_buttons):
            self.set_button_state(self.step_buttons[step_index], "executing")
        
        self.log(f"▶️  执行步骤: {step}", "info")
        
        # 根据步骤执行相应操作
        if step == "保存顺序":
            success = self.save_sort_config()
            if success:
                # 默认自动执行清理缓存，并记录过程与结果
                self.log("🧹 保存顺序后自动清理缓存...", "info")
                try:
                    cache_success, cache_message = self.deployment_manager.clean_cache(thorough=True)
                    if cache_success:
                        self.log(f"✅ 自动清理缓存完成: {cache_message}", "success")
                    else:
                        self.log(f"⚠️  自动清理缓存失败: {cache_message}", "warning")
                except Exception as e:
                    self.log(f"⚠️  自动清理缓存异常: {str(e)}", "warning")
                self.enable_next_step()
            else:
                if self.current_step_index < len(self.step_buttons):
                    self.set_button_state(self.step_buttons[self.current_step_index], "error")
                    self.root.after(1000, lambda idx=self.current_step_index: self.set_button_state(self.step_buttons[idx], "disabled"))
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
            # 设置当前按钮为成功状态
            if self.current_step_index < len(self.step_buttons):
                self.set_button_state(self.step_buttons[self.current_step_index], "success")
                # 1秒后恢复为禁用状态
                self.root.after(1000, lambda idx=self.current_step_index: self.set_button_state(self.step_buttons[idx], "disabled"))
            
            # 启用下一个按钮
            next_index = self.current_step_index + 1
            if next_index < len(self.step_buttons):
                self.set_button_state(self.step_buttons[next_index], "normal")
                self.log(f"✅ 步骤完成，已启用下一个按钮: {self.deployment_steps[next_index]}", "success")
            else:
                self.log("✅ 所有部署步骤已完成", "success")
        else:
            self.log("⚠️  无法找到当前步骤索引", "warning")
    
    def generate_sidebar(self):
        """生成侧边栏"""
        def _generate_sidebar():
            try:
                self.log("📋 开始生成侧边栏...", "info")
                self.deployment_manager.update_sidebars()
                self.log("✅ 侧边栏生成完成", "success")
                # 完成后启用下一个步骤
                self.root.after(0, self.enable_next_step)
            except Exception as e:
                self.log(f"❌ 生成侧边栏失败: {str(e)}", "error")
                # 设置按钮为错误状态
                if hasattr(self, 'current_step_index') and self.current_step_index is not None:
                    if self.current_step_index < len(self.step_buttons):
                        self.set_button_state(self.step_buttons[self.current_step_index], "error")
                        # 1秒后恢复为禁用状态
                        self.root.after(1000, lambda idx=self.current_step_index: self.set_button_state(self.step_buttons[idx], "disabled"))
        
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
                success, message = self.deployment_manager.local_preview(prefer_fresh=True)
                if success:
                    self.log(f"✅ {message}", "success")
                    try:
                        import webbrowser
                        preview_url = getattr(self.deployment_manager, "preview_url", "http://localhost:3000")
                        webbrowser.open(preview_url)
                        self.log(f"🌐 已自动打开本地预览页面: {preview_url}", "success")
                    except Exception as e:
                        self.log(f"⚠️  自动打开浏览器失败，请手动访问本地预览地址 ({str(e)})", "warning")
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
                
                # 步骤2.5: 默认排除打包大文件，避免推送失败（仅取消暂存，不删除本地文件）
                self.log("📋 步骤2.5: 排除dist/build大文件（默认策略）", "info")
                skip_paths = [
                    "ToothMen-dentipro-ch-文档更新程序/dist",
                    "ToothMen-dentipro-ch-文档更新程序/build",
                ]
                for skip_path in skip_paths:
                    success_skip, output_skip = self.deployment_manager.run_command(
                        self.deployment_manager.git_path, ["reset", "HEAD", "--", skip_path]
                    )
                    if success_skip:
                        self.log(f"✅ 已从本次提交排除: {skip_path}", "success")
                    else:
                        # 目录不存在或未跟踪时可能失败，不影响主流程
                        self.log(f"ℹ️  跳过排除（可能无变更）: {skip_path}", "info")
                
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
                
                # 推送策略：仅使用HTTPS（失败不再自动切换SSH）
                push_success = False
                push_output = ""
                push_error = ""
                https_url = "https://github.com/juemin7-star/toothmen-docs.git"
                
                # 先确保远程使用HTTPS（更适配当前网络环境）
                self.log("🌐 推送策略：仅HTTPS（失败不再自动切SSH）", "info")
                success_set_https, output_set_https = self.deployment_manager.run_command(
                    self.deployment_manager.git_path, ["remote", "set-url", "origin", https_url]
                )
                if success_set_https:
                    self.log("✅ 已切换远程为HTTPS", "success")
                else:
                    self.log(f"⚠️  切换HTTPS失败，继续尝试推送: {output_set_https}", "warning")
                
                # 阶段A：HTTPS推送（最多2次）
                for attempt in range(2):
                    if attempt > 0:
                        self.log(f"🔄 HTTPS第{attempt+1}次尝试推送...", "info")
                        import time
                        time.sleep(2)
                    
                    success_master, output_master = self.deployment_manager.run_command(
                        self.deployment_manager.git_path, ["push", "origin", "master"]
                    )
                    if success_master:
                        self.log("✅ 已通过HTTPS推送到远程仓库 (master分支)", "success")
                        push_success = True
                        push_output = output_master
                        break
                    
                    push_error = output_master
                    error_lower = output_master.lower()
                    if "src refspec master does not match any" in error_lower or "remote ref does not exist" in error_lower:
                        self.log("⚠️  master分支推送失败，尝试main分支（HTTPS）...", "warning")
                        success_main, output_main = self.deployment_manager.run_command(
                            self.deployment_manager.git_path, ["push", "origin", "main"]
                        )
                        if success_main:
                            self.log("✅ 已通过HTTPS推送到远程仓库 (main分支)", "success")
                            push_success = True
                            push_output = output_main
                            break
                        push_error = output_main
                
                if not push_success:
                    self.log("❌ 推送失败（HTTPS未成功）", "error")
                    self.log("ℹ️  可能的原因：", "info")
                    self.log("  1. 网络连接问题（443端口受限或超时）", "info")
                    self.log("  2. GitHub认证问题（需使用PAT）", "info")
                    self.log("  3. 仓库权限问题", "info")
                    self.log("  4. 防火墙或代理设置问题", "info")
                    self.log("ℹ️  请手动执行以下命令测试：", "info")
                    self.log(f'  cd "{self.project_path}"', "info")
                    self.log('  git remote set-url origin https://github.com/juemin7-star/toothmen-docs.git', "info")
                    self.log('  git push origin master', "info")
                    self.log("ℹ️  认证建议：GitHub 登录请使用 PAT（个人访问令牌）而非账号密码", "info")
                    self.log("ℹ️  网络建议：检查代理/防火墙或更换网络后重试 HTTPS 推送", "info")
                    if push_error:
                        self.log(f"🔍 最后一次推送错误: {push_error[:300]}", "warning")
                    
                    # 保存提交信息到文件，方便用户手动推送
                    try:
                        import json
                        
                        # 创建手动推送说明文件
                        manual_push_file = self.project_path / "手动推送说明.txt"
                        manual_content = f"""# 📋 手动推送说明

## 🔧 问题描述
自动推送失败，当前策略仅使用HTTPS，可能是网络或认证问题。

## 📊 当前状态
- 所有更改已添加到暂存区
- 更改已提交到本地仓库
- 提交信息: {commit_message}

## 🎯 手动推送步骤

### 方法1: 使用Git Bash手动推送
1. 打开Git Bash
2. 执行以下命令:
   ```
   cd "{self.project_path}"
   git push origin master
   ```

### 方法2: 使用GitHub Desktop
1. 打开GitHub Desktop
2. 选择此仓库: {self.project_path}
3. 点击"Push origin"按钮

### 认证说明（重要）
- 推送到GitHub时，请使用 **PAT（个人访问令牌）** 作为密码
- 不要使用GitHub账户登录密码

## 🔍 网络诊断
如果仍然失败，请检查:
1. 网络连接是否正常
2. 防火墙是否阻止了GitHub
3. 是否使用了代理（需要配置Git代理）
4. 尝试使用VPN

## 📅 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                        
                        with open(manual_push_file, "w", encoding="utf-8") as f:
                            f.write(manual_content)
                        
                        self.log(f"📄 已生成手动推送说明文件: {manual_push_file}", "info")
                        self.log("ℹ️  请按照文件中的说明手动完成推送", "info")
                        
                    except Exception as e:
                        self.log(f"⚠️  无法生成手动推送说明文件: {str(e)}", "warning")
                    
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
                docs_home_url = f"{cloudflare_url}/docs"
                
                # 1. 先尝试打开网站
                self.log(f"1. 正在打开Cloudflare网站: {docs_home_url}", "info")
                try:
                    webbrowser.open(docs_home_url)
                    self.log("✅ 已打开浏览器访问网站", "success")
                except Exception as e:
                    self.log(f"⚠️  无法自动打开浏览器: {str(e)}", "warning")
                    self.log(f"ℹ️  请手动访问: {docs_home_url}", "info")
                
                # 2. 检查网站是否可访问
                self.log("\n2. 检查网站是否可访问...", "info")
                
                # 创建不验证SSL的上下文（仅用于测试）
                context = ssl._create_unverified_context()
                
                # 仅检查稳定入口URL，避免旧链接/中文路径导致误报
                possible_urls = [
                    "https://docs.toothmen.com/",
                    "https://docs.toothmen.com",
                    "https://docs.toothmen.com/docs"
                ]
                
                site_accessible = False
                accessible_url = ""
                status_code = 0
                
                for url in possible_urls:
                    try:
                        req = urllib.request.Request(
                            url,
                            method="GET",
                            headers={"User-Agent": "ToothMenDocsManager/verify"}
                        )
                        response = urllib.request.urlopen(req, timeout=10, context=context)
                        site_accessible = True
                        accessible_url = url
                        status_code = response.status
                        break
                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            # 404可能是路由尚未就绪或缓存未刷新
                            self.log(f"⚠️  网站返回404: {url}", "warning")
                            continue
                        elif e.code == 403:
                            # 403通常表示可达但受保护/暂时限制，视为可连通
                            self.log(f"⚠️  网站返回403: {url} (Cloudflare构建中或访问限制)", "warning")
                            site_accessible = True
                            accessible_url = url
                            status_code = e.code
                            break
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
                self.log(f"❌ 部署验证失败: {str(e)}", "error")
        
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
    
    # ========== 按钮状态管理方法 ==========
    
    def set_button_state(self, button, state):
        """设置按钮状态（简化版，只支持normal和disabled）
        state: "normal", "disabled"
        """
        if button is None:
            return
        if state == "normal":
            button.config(state=tk.NORMAL)
        elif state == "disabled":
            button.config(state=tk.DISABLED)
    
    def reset_button_states(self):
        """重置所有按钮状态为正常"""
        # 重置排序按钮
        self.set_button_state(self.btn_folder_up, "disabled")
        self.set_button_state(self.btn_folder_down, "disabled")
        self.set_button_state(self.btn_file_up, "disabled")
        self.set_button_state(self.btn_file_down, "disabled")
        self.set_button_state(self.btn_save_sort, "disabled")
        
        # 重置控制按钮
        self.set_button_state(self.check_mdx_btn, "normal")
        self.set_button_state(self.start_workflow_btn, "normal")
        self.set_button_state(self.deploy_end_btn, "disabled")
        self.set_button_state(self.verify_deploy_btn, "normal")
        self.set_button_state(self.btn_refresh_structure, "normal")
        
        # 重置部署步骤按钮
        if hasattr(self, 'step_buttons') and self.step_buttons:
            for btn in self.step_buttons:
                self.set_button_state(btn, "disabled")
    
    # ========== 排序按钮方法 ==========
    def _is_folder_item(self, item_id):
        """判断树节点是否为文件夹节点。优先看类型列，图标仅做兜底。"""
        item_values = self.tree.item(item_id, "values")
        item_text = self.tree.item(item_id, "text")
        item_type = item_values[0] if item_values else ""
        return item_type == "文件夹" or item_text.startswith("📂")
    
    def _is_file_item(self, item_id):
        """判断树节点是否为文件节点。优先看类型列，图标仅做兜底。"""
        item_values = self.tree.item(item_id, "values")
        item_text = self.tree.item(item_id, "text")
        item_type = item_values[0] if item_values else ""
        return (
            item_type in ("MDX文件", "MD文件", "子文件夹")
            or item_text.startswith("📄")
            or item_text.startswith("📝")
        )
    
    def on_tree_selection(self, event):
        """树选择事件，用于启用/禁用排序按钮"""
        selection = self.tree.selection()
        if not selection:
            # 没有选择任何项目，禁用所有排序按钮
            self.set_button_state(self.btn_folder_up, "disabled")
            self.set_button_state(self.btn_folder_down, "disabled")
            self.set_button_state(self.btn_file_up, "disabled")
            self.set_button_state(self.btn_file_down, "disabled")
            self.set_button_state(self.btn_save_sort, "disabled")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        
        # 根据选择的项目类型启用相应的按钮
        if self._is_folder_item(item_id):
            # 选择了文件夹，启用文件夹排序按钮，禁用文件排序按钮
            self.set_button_state(self.btn_folder_up, "normal")
            self.set_button_state(self.btn_folder_down, "normal")
            self.set_button_state(self.btn_file_up, "disabled")
            self.set_button_state(self.btn_file_down, "disabled")
            self.set_button_state(self.btn_save_sort, "normal")
        elif self._is_file_item(item_id):
            # 选择了文件，启用文件排序按钮，禁用文件夹排序按钮
            self.set_button_state(self.btn_folder_up, "disabled")
            self.set_button_state(self.btn_folder_down, "disabled")
            self.set_button_state(self.btn_file_up, "normal")
            self.set_button_state(self.btn_file_down, "normal")
            self.set_button_state(self.btn_save_sort, "normal")
        else:
            # 其他情况，禁用所有按钮
            self.set_button_state(self.btn_folder_up, "disabled")
            self.set_button_state(self.btn_folder_down, "disabled")
            self.set_button_state(self.btn_file_up, "disabled")
            self.set_button_state(self.btn_file_down, "disabled")
            self.set_button_state(self.btn_save_sort, "disabled")
    
    def move_folder_up(self):
        """上移文件夹"""
        try:
            selection = self.tree.selection()
            if not selection:
                self.log("⚠️  请先选择一个文件夹", "warning")
                return
            
            item_id = selection[0]
            item_text = self.tree.item(item_id, "text")
            
            if not self._is_folder_item(item_id):
                self.log("⚠️  请选择一个文件夹（📂 开头的项目）", "warning")
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
        except Exception as e:
            self.log(f"❌ 上移文件夹失败: {str(e)}", "error")
    
    def move_folder_down(self):
        """下移文件夹"""
        try:
            selection = self.tree.selection()
            if not selection:
                self.log("⚠️  请先选择一个文件夹", "warning")
                return
            
            item_id = selection[0]
            item_text = self.tree.item(item_id, "text")
            
            if not self._is_folder_item(item_id):
                self.log("⚠️  请选择一个文件夹（📂 开头的项目）", "warning")
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
        except Exception as e:
            self.log(f"❌ 下移文件夹失败: {str(e)}", "error")
    
    def move_file_up(self):
        """上移文件"""
        try:
            selection = self.tree.selection()
            if not selection:
                self.log("⚠️  请先选择一个文件", "warning")
                return
            
            item_id = selection[0]
            item_text = self.tree.item(item_id, "text")
            
            if not self._is_file_item(item_id):
                self.log("⚠️  请选择可排序子项（📂 子文件夹 / 📄 / 📝）", "warning")
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
        except Exception as e:
            self.log(f"❌ 上移文件失败: {str(e)}", "error")
    
    def move_file_down(self):
        """下移文件"""
        try:
            selection = self.tree.selection()
            if not selection:
                self.log("⚠️  请先选择一个文件", "warning")
                return
            
            item_id = selection[0]
            item_text = self.tree.item(item_id, "text")
            
            if not self._is_file_item(item_id):
                self.log("⚠️  请选择可排序子项（📂 子文件夹 / 📄 / 📝）", "warning")
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
        except Exception as e:
            self.log(f"❌ 下移文件失败: {str(e)}", "error")
    
    def save_sort_config(self):
        """保存排序配置"""
        success = False
        try:
            # 读取现有的排序配置
            sort_config_path = self.sort_config_path
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
                if self._is_folder_item(item_id):
                    # 提取文件夹名称（去掉图标和斜杠）
                    folder_name = item_text.replace("📂 ", "").replace("/", "")
                    sort_config["folders"].append(folder_name)
                    
                    # 保存文件夹内的文件顺序
                    file_items = self.tree.get_children(item_id)
                    file_names = []
                    for file_id in file_items:
                        file_text = self.tree.item(file_id, "text")
                        if self._is_file_item(file_id):
                            item_name = file_text.split(" ", 1)[1].rstrip("/")
                            # 子文件夹：原样保存（如 2025）
                            if self.tree.item(file_id, "values")[0] == "子文件夹":
                                file_names.append(item_name)
                                
                                # 同时保存子文件夹内文件顺序到 folder/subfolder 键
                                sub_key = f"{folder_name}/{item_name}"
                                sub_children = self.tree.get_children(file_id)
                                sub_names = []
                                for sub_id in sub_children:
                                    if self._is_file_item(sub_id):
                                        sub_text = self.tree.item(sub_id, "text")
                                        sub_name = sub_text.split(" ", 1)[1]
                                        if sub_name.endswith('.mdx'):
                                            sub_name = sub_name[:-4]
                                        elif sub_name.endswith('.md'):
                                            sub_name = sub_name[:-3]
                                        sub_names.append(sub_name)
                                if sub_names:
                                    sort_config["files"][sub_key] = sub_names
                            else:
                                # 文件：去扩展名后保存
                                if item_name.endswith('.mdx'):
                                    item_name = item_name[:-4]
                                elif item_name.endswith('.md'):
                                    item_name = item_name[:-3]
                                file_names.append(item_name)
                    
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
            success = True
                
        except Exception as e:
            self.log(f"❌ 保存排序配置失败: {str(e)}", "error")
        return success

def main():
    """主函数"""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
