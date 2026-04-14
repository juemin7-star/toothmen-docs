#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署管理模块 - 全新版本
支持文件夹分类逻辑和数字前缀排序
"""

import os
import subprocess
import shutil
import json
import re
from pathlib import Path
import time
from typing import List, Dict, Tuple, Optional

class DeploymentManager:
    def __init__(self, project_path):
        """
        初始化部署管理器
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.docs_folder = self.project_path / "docs"
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 命令路径配置
        self.npm_path = "npm.cmd"  # Windows上使用npm.cmd
        self.git_path = r"C:\Program Files\Git\cmd\git.exe"
        
        # 特殊文件夹配置（需要倒序排序）
        self.reverse_order_folders = ["补丁更新日志", "patch-notes", "更新记录", "changelog"]
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.npm_path = config.get("npm_path", self.npm_path)
                    self.git_path = config.get("git_path", self.git_path)
                    self.reverse_order_folders = config.get("reverse_order_folders", self.reverse_order_folders)
            except:
                pass
        
        # 注意：不再自动检测文件夹结构，避免修改配置文件
        # 自动检测功能由用户手动触发
    
    def clean_cache(self, thorough=False):
        """
        清理Docusaurus缓存
        
        Args:
            thorough: 是否彻底清理（包括build文件夹）
        
        Returns:
            (success, message): 清理结果
        """
        print("🧹 开始清理缓存...")
        
        cache_dirs = [
            ".docusaurus",      # Docusaurus缓存目录
            "node_modules/.cache",  # Node.js缓存
        ]
        
        if thorough:
            cache_dirs.append("build")  # 构建输出目录
        
        cleaned_count = 0
        errors = []
        
        for cache_dir in cache_dirs:
            cache_path = self.project_path / cache_dir
            if cache_path.exists():
                try:
                    if cache_path.is_dir():
                        shutil.rmtree(cache_path)
                        print(f"✅ 已清理: {cache_dir}")
                        cleaned_count += 1
                    else:
                        os.remove(cache_path)
                        print(f"✅ 已删除: {cache_dir}")
                        cleaned_count += 1
                except Exception as e:
                    error_msg = f"清理 {cache_dir} 失败: {e}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
            else:
                print(f"📭 无需清理: {cache_dir} (不存在)")
        
        # 清理npm缓存（可选，如果npm可用）
        try:
            print("🧹 清理npm缓存...")
            # 检查npm是否可用
            result = subprocess.run(
                [self.npm_path, "--version"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
                creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
            )
            if result.returncode == 0:
                # npm可用，清理缓存
                cache_result = subprocess.run(
                    [self.npm_path, "cache", "clean", "--force"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
                )
                if cache_result.returncode == 0:
                    print("✅ npm缓存已清理")
                    cleaned_count += 1
                else:
                    error_msg = f"npm缓存清理失败: {cache_result.stderr}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
            else:
                print("📭 npm不可用，跳过npm缓存清理")
        except Exception as e:
            print(f"📭 npm缓存清理跳过: {e}")
        
        if errors:
            return False, f"清理完成但有错误: {', '.join(errors)}"
        else:
            return True, f"缓存清理完成，清理了 {cleaned_count} 个项目"
    
    def scan_folder_structure(self) -> Dict[str, List[str]]:
        """
        扫描docs文件夹结构
        
        Returns:
            字典：{文件夹名: [文件列表]}
        """
        structure = {}
        
        if not self.docs_folder.exists():
            return structure
        
        # 获取所有一级文件夹
        for item in self.docs_folder.iterdir():
            if item.is_dir():
                folder_name = item.name
                mdx_files = []
                
                # 获取文件夹内的MDX文件
                for file in item.glob("*.mdx"):
                    mdx_files.append(file.name)
                
                structure[folder_name] = mdx_files
        
        return structure
    
    def auto_detect_folders(self, clean_cache_before=True, clean_cache_after=True):
        """
        自动检测文件夹结构并更新配置
        
        Args:
            clean_cache_before: 执行前是否清理缓存
            clean_cache_after: 执行后是否清理缓存
        """
        print("🔍 开始自动检测文件夹结构...")
        
        # 执行前清理缓存
        if clean_cache_before:
            print("🧹 执行前清理缓存...")
            success, message = self.clean_cache(thorough=True)
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️  {message}")
        
        if not self.docs_folder.exists():
            print("❌ docs文件夹不存在")
            return
        
        # 检测文件夹
        detected_folders = []
        for item in self.docs_folder.iterdir():
            if item.is_dir():
                detected_folders.append(item.name)
        
        print(f"✅ 检测到文件夹: {detected_folders}")
        
        # 严格模式：不再自动改写排序配置/导航配置
        # 排序唯一来源：界面“上下移动 + 保存排序”写入的 sort_config.json
        print("ℹ️  严格排序模式：跳过自动写入sort_config与导航配置")
        
        # 更新侧边栏配置
        success, message = self.update_sidebars()
        if success:
            print(f"✅ 侧边栏更新: {message}")
        else:
            print(f"❌ 侧边栏更新失败: {message}")
        
        print("✅ 文件夹结构自动检测完成")
        
        # 执行后清理缓存
        if clean_cache_after:
            print("🧹 执行后清理缓存...")
            success, message = self.clean_cache(thorough=False)  # 不清理build文件夹
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️  {message}")
    
    def build_website(self, clean_cache_before=True, clean_cache_after=True, serve_after_build=False, port=3000):
        """
        构建网站（完整的可重复工作流）
        
        Args:
            clean_cache_before: 构建前是否清理缓存
            clean_cache_after: 构建后是否清理缓存
            serve_after_build: 构建后是否启动服务器
            port: 服务器端口
        
        Returns:
            (success, message): 构建结果
        """
        print("🏗️  开始构建网站（完整工作流）...")
        print("=" * 50)
        
        # 步骤1: 构建前清理缓存
        if clean_cache_before:
            print("📋 步骤1: 构建前清理缓存")
            success, message = self.clean_cache(thorough=True)
            if success:
                print(f"✅ {message}")
            else:
                print(f"⚠️  {message}")
        
        # 步骤2: 严格使用现有排序配置（不再自动检测/覆盖顺序）
        print("📋 步骤2: 使用已保存排序配置（仅上下移动+保存排序生效）")
        sort_config_path = Path(__file__).parent / "sort_config.json"
        if not sort_config_path.exists():
            error_msg = "未找到sort_config.json，请先在界面中完成排序并点击“保存排序”"
            print(f"❌ {error_msg}")
            return False, error_msg
        
        # 步骤3: 执行npm构建
        print("📋 步骤3: 执行npm构建")
        try:
            result = subprocess.run(
                [self.npm_path, "run", "build"],
                capture_output=True,
                encoding='utf-8',
                errors='ignore',
                cwd=self.project_path,
                timeout=300,  # 5分钟超时
                shell=True,  # 使用shell执行
                creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
            )
            
            if result.returncode == 0:
                print("✅ 网站构建成功")
                
                # 步骤4: 构建后清理缓存
                if clean_cache_after:
                    print("📋 步骤4: 构建后清理缓存")
                    success, message = self.clean_cache(thorough=False)
                    if success:
                        print(f"✅ {message}")
                    else:
                        print(f"⚠️  {message}")
                
                # 步骤5: 启动服务器（如果需要）
                if serve_after_build:
                    print(f"📋 步骤5: 启动服务器 (端口: {port})")
                    try:
                        # 使用子进程启动服务器（非阻塞）- 隐藏控制台窗口
                        server_process = subprocess.Popen(
                            ["npx", "docusaurus", "serve", "--port", str(port)],
                            cwd=self.project_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
                        )
                        
                        # 等待服务器启动
                        time.sleep(3)
                        
                        # 检查服务器是否运行
                        if server_process.poll() is None:
                            print(f"✅ 服务器已启动: http://localhost:{port}")
                            return True, f"构建成功，服务器运行在 http://localhost:{port}"
                        else:
                            stdout, stderr = server_process.communicate()
                            return False, f"服务器启动失败: {stderr}"
                    except Exception as e:
                        return False, f"启动服务器失败: {e}"
                
                return True, "网站构建成功"
            else:
                error_msg = f"构建失败: {result.stderr}"
                print(f"❌ {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "构建超时（超过5分钟）"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"执行构建命令失败: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def update_sort_config(self, folders):
        """
        更新排序配置文件
        
        Args:
            folders: 检测到的文件夹列表
        """
        sort_config_path = Path(__file__).parent / "sort_config.json"
        
        # 读取现有配置
        config = {}
        if sort_config_path.exists():
            try:
                with open(sort_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                config = {}
        
        # 更新文件夹列表
        config["folders"] = folders
        
        # 更新文件排序（保持现有的文件顺序）
        if "files" not in config:
            config["files"] = {}
        
        # 为每个文件夹设置默认文件排序
        for folder in folders:
            folder_path = self.docs_folder / folder
            if folder_path.exists():
                # 获取文件夹中的文件
                files = []
                for file_item in folder_path.iterdir():
                    if file_item.is_file() and (file_item.name.endswith('.mdx') or file_item.name.endswith('.md')):
                        files.append(self.clean_name(file_item.name))
                
                # 如果有子文件夹（如年份文件夹）
                subfolders = []
                for sub_item in folder_path.iterdir():
                    if sub_item.is_dir():
                        subfolders.append(sub_item.name)
                
                if subfolders:
                    # 如果有子文件夹，添加到配置
                    config["files"][folder] = subfolders
                    
                    # 为每个子文件夹配置文件排序
                    for subfolder in subfolders:
                        subfolder_path = folder_path / subfolder
                        subfolder_key = f"{folder}/{subfolder}"
                        
                        sub_files = []
                        for file_item in subfolder_path.iterdir():
                            if file_item.is_file() and (file_item.name.endswith('.mdx') or file_item.name.endswith('.md')):
                                sub_files.append(self.clean_name(file_item.name))
                        
                        if sub_files:
                            # 按数字前缀排序（倒序）
                            sub_files_sorted = self.sort_by_number_prefix(sub_files)
                            config["files"][subfolder_key] = sub_files_sorted
                elif files:
                    # 如果没有子文件夹，直接配置文件
                    config["files"][folder] = files
        
        # 写入配置文件
        try:
            with open(sort_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ 已更新排序配置文件: {sort_config_path}")
        except Exception as e:
            print(f"❌ 更新排序配置文件失败: {e}")
    
    def update_navbar_config(self, folders):
        """
        更新导航栏配置
        
        Args:
            folders: 检测到的文件夹列表
        """
        docusaurus_config_path = self.project_path / "docusaurus.config.js"
        
        if not docusaurus_config_path.exists():
            print(f"❌ Docusaurus配置文件不存在: {docusaurus_config_path}")
            return
        
        try:
            # 读取配置文件
            with open(docusaurus_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件是否是MDX格式（包含YAML frontmatter）
            if content.strip().startswith('---'):
                print("⚠️  docusaurus.config.js 是MDX格式，无法更新导航栏配置")
                print("ℹ️  请确保配置文件是JavaScript格式")
                return
            
            # 查找导航栏配置部分
            import re
            
            # 查找 items: [ 开始到 ] 结束的部分
            pattern = r'items:\s*\[(.*?)\]'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                print("❌ 未找到导航栏配置")
                return
            
            items_content = match.group(1)
            
            # 分析文件夹类型，生成导航项
            nav_items = []
            
            # 检测安装教程文件夹
            installation_folders = [f for f in folders if "安装" in f or "installation" in f.lower()]
            if installation_folders:
                installation_folder = installation_folders[0]
                # 查找安装教程的主文档
                main_doc_id = self.find_main_doc_id(installation_folder)
                if main_doc_id:
                    nav_items.append(f"""          {{
            type: 'doc',
            docId: '{main_doc_id}',
            position: 'left',
            label: '总文档中心',
          }},""")
            
            # 检测更新日志文件夹（排除云更新服务说明）
            changelog_folders = [f for f in folders if ("更新" in f and "云更新" not in f) or "changelog" in f.lower()]
            if changelog_folders:
                changelog_folder = changelog_folders[0]
                # 优先查找总览页面 (changelog-index)
                changelog_index_path = self.docs_folder / changelog_folder / "index.md"
                if changelog_index_path.exists():
                    # 读取index.md文件获取文档ID
                    try:
                        with open(changelog_index_path, 'r', encoding='utf-8') as f:
                            index_content = f.read()
                            # 查找id字段
                            import re
                            id_match = re.search(r'id:\s*["\']?([^"\'\s]+)', index_content)
                            if id_match:
                                doc_id = id_match.group(1)
                                nav_items.append(f"""          {{
            type: 'doc',
            docId: '{changelog_folder}/{doc_id}',
            position: 'left',
            label: '更新日志',
          }},""")
                            else:
                                # 如果没有找到id，使用默认的changelog-index
                                nav_items.append(f"""          {{
            type: 'doc',
            docId: '{changelog_folder}/changelog-index',
            position: 'left',
                            label: '更新日志',
          }},""")
                    except Exception as e:
                        print(f"❌ 读取更新日志索引文件失败: {e}")
                        # 使用默认的changelog-index
                        nav_items.append(f"""          {{
            type: 'doc',
            docId: '{changelog_folder}/changelog-index',
            position: 'left',
            label: '更新日志',
          }},""")
                else:
                    # 如果没有总览页面，查找年份索引
                    year_index_id = self.find_year_index_id(changelog_folder)
                    if year_index_id:
                        nav_items.append(f"""          {{
            type: 'doc',
            docId: '{year_index_id}',
            position: 'left',
            label: '更新日志',
          }},""")
            
            # 添加搜索项
            nav_items.append(f"""          {{
            type: 'search',
            position: 'right',
          }},""")
            
            # 构建新的items内容
            new_items_content = "\n".join(nav_items)
            
            # 替换原内容
            new_content = content[:match.start(1)] + new_items_content + content[match.end(1):]
            
            # 写入文件
            with open(docusaurus_config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已更新导航栏配置: {docusaurus_config_path}")
            
            # 同时更新重定向配置
            self.update_redirects_config(folders)
            
        except Exception as e:
            print(f"❌ 更新导航栏配置失败: {e}")
    
    def update_redirects_config(self, folders):
        """
        更新重定向配置
        
        Args:
            folders: 检测到的文件夹列表
        """
        docusaurus_config_path = self.project_path / "docusaurus.config.js"
        
        if not docusaurus_config_path.exists():
            return
        
        try:
            # 读取配置文件
            with open(docusaurus_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # 查找重定向配置部分
            redirects_pattern = r'redirects:\s*\[(.*?)\]'
            match = re.search(redirects_pattern, content, re.DOTALL)
            
            if not match:
                print("⚠️  未找到重定向配置，跳过更新")
                return
            
            print("📋 找到重定向配置，但跳过写入以避免破坏配置文件")
            print("ℹ️  重定向配置已手动维护，不需要自动更新")
            
        except Exception as e:
            print(f"⚠️  检查重定向配置失败: {e}")
    
    def find_main_doc_id(self, folder_name):
        """
        查找文件夹中的主文档ID
        
        Args:
            folder_name: 文件夹名称
        
        Returns:
            主文档ID或None
        """
        folder_path = self.docs_folder / folder_name
        
        if not folder_path.exists():
            return None
        
        # 查找文件夹中的第一个MDX/MD文件
        for file_item in folder_path.iterdir():
            if file_item.is_file() and (file_item.name.endswith('.mdx') or file_item.name.endswith('.md')):
                doc_id = self.get_doc_id_from_mdx(file_item)
                if doc_id:
                    return doc_id
                else:
                    # 如果没有文档ID，生成一个
                    clean_name = self.clean_name(file_item.name)
                    return f"{folder_name}/{clean_name}"
        
        return None
    
    def find_year_index_id(self, folder_name):
        """
        查找更新日志文件夹中的年份索引文档ID
        
        Args:
            folder_name: 更新日志文件夹名称
        
        Returns:
            年份索引文档ID或None
        """
        folder_path = self.docs_folder / folder_name
        
        if not folder_path.exists():
            return None
        
        # 查找年份子文件夹
        for sub_item in folder_path.iterdir():
            if sub_item.is_dir():
                year_folder = sub_item.name
                # 检查年份文件夹中是否有index.md文件
                index_file = sub_item / "index.md"
                if index_file.exists():
                    # 从index.md读取文档ID
                    doc_id = self.get_doc_id_from_mdx(index_file)
                    if doc_id:
                        # 确保文档ID包含完整的路径
                        if not doc_id.startswith(f"{folder_name}/"):
                            doc_id = f"{folder_name}/{doc_id}"
                        return doc_id
                    else:
                        # 如果没有文档ID，生成一个
                        return f"{folder_name}/{year_folder}/{year_folder}"
        
        # 如果没有年份文件夹，查找第一个MDX/MD文件
        for file_item in folder_path.iterdir():
            if file_item.is_file() and (file_item.name.endswith('.mdx') or file_item.name.endswith('.md')):
                doc_id = self.get_doc_id_from_mdx(file_item)
                if doc_id:
                    # 确保文档ID包含完整的路径
                    if not doc_id.startswith(f"{folder_name}/"):
                        doc_id = f"{folder_name}/{doc_id}"
                    return doc_id
                else:
                    clean_name = self.clean_name(file_item.name)
                    return f"{folder_name}/{clean_name}"
        
        return None
    
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
    
    def get_slug_from_mdx(self, file_path: Path) -> str:
        """
        从MDX文件中读取slug
        
        Args:
            file_path: MDX文件路径
        
        Returns:
            slug字符串，如果没有找到返回空字符串
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找slug: 行
            import re
            match = re.search(r'slug:\s*["\']?([^"\'\n]+)["\']?', content)
            if match:
                return match.group(1).strip()
            
            # 如果没有slug，尝试从文件名生成
            return ""
        except Exception as e:
            print(f"读取slug失败 {file_path}: {e}")
            return ""
    
    def get_doc_id_from_mdx(self, file_path: Path) -> str:
        """
        从MDX文件中读取文档ID
        
        Args:
            file_path: MDX文件路径
        
        Returns:
            文档ID字符串，如果没有找到返回空字符串
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找id: 行
            import re
            match = re.search(r'id:\s*["\']?([^"\'\n]+)["\']?', content)
            if match:
                id_value = match.group(1).strip()
                # 如果id包含文件夹信息，直接返回
                if '/' in id_value:
                    return id_value
                # 否则，需要结合文件夹名
                folder_name = file_path.parent.name
                return f"{folder_name}/{id_value}"
            
            return ""
        except Exception as e:
            print(f"读取文档ID失败 {file_path}: {e}")
            return ""
    
    def get_category_label(self, folder_path: Path) -> str:
        """
        获取分类标签 - 优先从 _category_.json 读取，否则使用文件夹名
        
        Args:
            folder_path: 文件夹路径
        
        Returns:
            分类标签
        """
        folder_name = folder_path.name
        
        # 首先尝试从 _category_.json 读取
        category_file = folder_path / "_category_.json"
        if category_file.exists():
            try:
                with open(category_file, 'r', encoding='utf-8') as f:
                    import json
                    category_data = json.load(f)
                    label = category_data.get('label', folder_name)
                    print(f"  从_category_.json读取标签: {label}")
                    return label
            except Exception as e:
                print(f"  读取_category_.json失败: {e}")
        
        # 如果没有 _category_.json，使用默认映射
        label_mapping = {
            "更新日志": "更新日志",
            "云更新服务说明": "云更新服务说明",
            "安装教程": "安装教程",
            "补丁更新日志": "补丁更新日志"
        }
        
        return label_mapping.get(folder_name, folder_name)
    
    def _get_mdx_files_in_folder(self, folder_path: Path) -> list:
        """
        获取文件夹中的MDX/MD文件
        
        Args:
            folder_path: 文件夹路径
        
        Returns:
            文件列表
        """
        files = []
        if folder_path.exists() and folder_path.is_dir():
            for item in folder_path.iterdir():
                if item.is_file() and (item.name.endswith('.mdx') or item.name.endswith('.md')):
                    files.append(item.name)
        return files
    
    def _get_sorted_files_for_folder(self, folder_key: str, all_files: list) -> list:
        """
        根据配置文件获取排序后的文件列表
        
        Args:
            folder_key: 文件夹键（如"更新日志/2026"）
            all_files: 所有文件列表
        
        Returns:
            排序后的文件列表
        """
        # 从配置文件读取排序
        if hasattr(self, 'sort_config') and self.sort_config:
            config_files = self.sort_config.get('files', {}).get(folder_key, [])
            if config_files:
                # 添加扩展名
                config_files_with_ext = []
                for file in config_files:
                    # 根据文件类型添加扩展名
                    if any(f.endswith('.md') for f in all_files):
                        config_files_with_ext.append(f"{file}.md")
                    else:
                        config_files_with_ext.append(f"{file}.mdx")
                
                # 按配置顺序排序
                sorted_files = []
                for config_file in config_files_with_ext:
                    if config_file in all_files:
                        sorted_files.append(config_file)
                        all_files.remove(config_file)
                
                # 添加剩余文件（按字母顺序）
                for file_name in sorted(all_files):
                    sorted_files.append(file_name)
                
                return sorted_files
        
        # 如果没有配置，按字母顺序排序
        return sorted(all_files)
    
    def clean_name(self, name: str) -> str:
        """
        清理名称 - 移除.mdx或.md扩展名
        
        Args:
            name: 原始名称（如"主程序安装说明.mdx"或"2026-04.md"）
        
        Returns:
            清理后的名称（如"主程序安装说明"或"2026-04"）
        """
        # 移除.mdx或.md扩展名
        if name.endswith('.mdx'):
            return name[:-4]
        elif name.endswith('.md'):
            return name[:-3]
        return name
    
    def clean_name_for_url(self, name: str) -> str:
        """
        清理名称用于URL - 移除数字前缀和扩展名，中文转英文
        
        Args:
            name: 原始名称（如"1-程序安装说明.mdx"或"1 -ProgramInstallationInstructions"）
        
        Returns:
            清理后的英文名称（如"program-installation-guide"）
        """
        # 移除.mdx或.md扩展名
        if name.endswith('.mdx'):
            name = name[:-4]
        elif name.endswith('.md'):
            name = name[:-3]
        
        # 移除数字前缀（如"1-"或"1 -"）
        import re
        # 匹配数字开头，后面可能跟空格和连字符
        name = re.sub(r'^\d+\s*\-*\s*', '', name)
        
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
    
    def generate_sidebar_content(self) -> str:
        """
        生成双语侧边栏内容 - 支持中英文文档
        
        Returns:
            侧边栏JavaScript代码
        """
        import json
        
        lines = []
        lines.append("const sidebars = {")
        lines.append("  tutorialSidebar: [")
        
        # 读取排序配置文件
        sort_config_path = Path(__file__).parent / "sort_config.json"
        
        # 获取文件夹列表（按配置或按字母顺序）
        folders = []
        if sort_config_path.exists():
            try:
                with open(sort_config_path, 'r', encoding='utf-8') as f:
                    sort_config = json.load(f)
                folders = sort_config.get("folders", [])
                print(f"从配置文件读取文件夹: {folders}")
            except Exception as e:
                print(f"读取排序配置文件失败: {e}")
                folders = []
        
        # 如果没有从配置文件中获取到文件夹，从文件系统获取
        if not folders:
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    folders.append(item.name)
            folders = sorted(folders)
            print(f"从文件系统获取文件夹: {folders}")
        
        # 为每个文件夹生成侧边栏条目
        for folder_name in folders:
            folder_path = self.docs_folder / folder_name
            
            if not folder_path.exists():
                print(f"文件夹不存在: {folder_path}")
                continue
            
            print(f"处理文件夹: {folder_name}")
            
            # 获取文件夹中的文件和子文件夹 - 支持 .mdx 和 .md 文件
            files_and_folders = []
            for file_item in folder_path.iterdir():
                if file_item.is_file() and (file_item.name.endswith('.mdx') or file_item.name.endswith('.md')):
                    files_and_folders.append(file_item.name)
                elif file_item.is_dir():
                    # 检查子文件夹中是否有MDX/MD文件
                    sub_files = self._get_mdx_files_in_folder(file_item)
                    if sub_files:
                        files_and_folders.append(file_item.name)
            
            print(f"  找到文件和文件夹: {files_and_folders}")
            
            # 按照配置文件中的文件顺序
            sorted_items = []
            if sort_config_path.exists():
                try:
                    with open(sort_config_path, 'r', encoding='utf-8') as f:
                        sort_config = json.load(f)
                    config_files = sort_config.get("files", {}).get(folder_name, [])
                    print(f"  配置文件中的文件顺序: {config_files}")
                    
                    # 先添加配置文件中指定的子项（兼容子文件夹与 .md/.mdx 文件）
                    for config_file in config_files:
                        # 1) 优先按“原样名称”匹配（用于子文件夹，如 2026 / 2025）
                        if config_file in files_and_folders:
                            sorted_items.append(config_file)
                            print(f"    添加配置文件指定的子项: {config_file}")
                            continue
                        
                        # 2) 再按文件扩展名尝试匹配（兼容 .mdx / .md）
                        candidate_files = [f"{config_file}.mdx", f"{config_file}.md"]
                        matched = False
                        for candidate in candidate_files:
                            if candidate in files_and_folders:
                                sorted_items.append(candidate)
                                print(f"    添加配置文件指定的文件: {candidate}")
                                matched = True
                                break
                        if matched:
                            continue
                except Exception as e:
                    print(f"  读取文件配置失败: {e}")
            
            # 再添加其他项目（按字母顺序）
            for item_name in sorted(files_and_folders):
                if item_name not in sorted_items:
                    sorted_items.append(item_name)
                    print(f"    添加其他项目: {item_name}")
            
            if sorted_items:
                # 获取分类标签（优先从 _category_.json 读取）
                category_label = self.get_category_label(folder_path)
                lines.append("    {")
                lines.append(f"      type: 'category',")
                lines.append(f"      label: '{category_label}',")
                lines.append(f"      items: [")
                
                for item_name in sorted_items:
                    item_path = folder_path / item_name
                    print(f"    处理项目: {item_name}")
                    
                    # 检查是否是文件夹
                    if item_path.is_dir():
                        # 处理子文件夹（年份文件夹）
                        subfolder_name = item_name
                        subfolder_path = folder_path / subfolder_name
                        
                        # 获取子文件夹中的文件
                        sub_files = self._get_mdx_files_in_folder(subfolder_path)
                        if sub_files:
                            # 为子文件夹创建嵌套分类
                            lines.append("      {")
                            lines.append(f"        type: 'category',")
                            lines.append(f"        label: '{subfolder_name}年',")
                            lines.append(f"        items: [")
                            
                            # 获取子文件夹的排序配置
                            subfolder_config_key = f"{folder_name}/{subfolder_name}"
                            subfolder_sorted_files = self._get_sorted_files_for_folder(subfolder_config_key, sub_files)
                            
                            for sub_file_name in subfolder_sorted_files:
                                sub_file_path = subfolder_path / sub_file_name
                                print(f"      处理子文件: {sub_file_name}")
                                
                                # 获取文档ID
                                sub_doc_id = self.get_doc_id_from_mdx(sub_file_path)
                                if not sub_doc_id:
                                    clean_sub_file_name = self.clean_name(sub_file_name)
                                    sub_doc_id = f"{folder_name}/{subfolder_name}/{clean_sub_file_name}"
                                else:
                                    # 确保文档ID包含完整的文件夹路径
                                    if not sub_doc_id.startswith(f"{folder_name}/"):
                                        sub_doc_id = f"{folder_name}/{sub_doc_id}"
                                
                                lines.append(f"          '{sub_doc_id}',")
                            
                            lines.append(f"        ],")
                            lines.append(f"        collapsed: true,")
                            lines.append("      },")
                    else:
                        # 处理普通文件
                        doc_id = self.get_doc_id_from_mdx(item_path)
                        print(f"      从MDX读取的文档ID: {doc_id}")
                        
                        if not doc_id:
                            # 如果没有id，使用清理后的文件名
                            clean_file_name = self.clean_name(item_name)
                            doc_id = f"{folder_name}/{clean_file_name}"
                            print(f"      使用清理后的文件名作为文档ID: {doc_id}")
                        
                        lines.append(f"        '{doc_id}',")
                
                lines.append(f"      ],")
                lines.append(f"      collapsed: true,")
                lines.append("    },")
            else:
                print(f"  文件夹 {folder_name} 中没有MDX文件")
        
        lines.append("  ],")
        lines.append("};")
        lines.append("")
        lines.append("export default sidebars;")
        
        result = "\n".join(lines)
        print(f"生成的侧边栏内容:\n{result}")
        return result
    
    def update_sidebars(self):
        """
        更新sidebars.js（基于文件夹结构）
        
        Returns:
            (success, message)
        """
        try:
            # 检查docs文件夹是否存在
            if not self.docs_folder.exists():
                return False, f"docs文件夹不存在: {self.docs_folder}"
            
            # 生成侧边栏内容
            content = self.generate_sidebar_content()
            
            # 备份原文件
            backup_path = self.sidebars_path.with_suffix('.js.backup')
            if self.sidebars_path.exists():
                shutil.copy2(self.sidebars_path, backup_path)
            
            # 写入新内容
            with open(self.sidebars_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "侧边栏更新成功（基于文件夹分类）"
            
        except Exception as e:
            return False, f"侧边栏更新失败: {str(e)}"
    
    def run_command(self, command, args, cwd=None, timeout=300, use_shell=None):
        """
        运行命令行命令
        
        Args:
            command: 命令（如'npm', 'git'）
            args: 参数列表
            cwd: 工作目录
            timeout: 超时时间（秒）
            use_shell: 是否使用shell（None表示自动判断）
        
        Returns:
            (success, output)
        """
        try:
            if cwd is None:
                cwd = str(self.project_path)
            
            # 自动判断是否使用shell
            if use_shell is None:
                # npm命令通常需要shell=True
                if command.lower() == 'npm':
                    use_shell = True
                else:
                    use_shell = False
            
            # 构建命令
            if use_shell:
                # 使用shell模式
                if isinstance(args, list):
                    full_command = f"{command} {' '.join(args)}"
                else:
                    full_command = f"{command} {args}"
                
                # 添加调试信息
                debug_info = f"执行命令: {full_command}\n工作目录: {cwd}\n模式: shell\n"
                
                # 执行命令（使用shell模式）- 隐藏控制台窗口
                result = subprocess.run(
                    full_command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # 替换无法解码的字符
                    timeout=timeout,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
                )
            else:
                # 使用列表形式
                if isinstance(args, list):
                    cmd_list = [command] + args
                    full_command = f"{command} {' '.join(args)}"
                else:
                    cmd_list = [command, args]
                    full_command = f"{command} {args}"
                
                # 添加调试信息
                debug_info = f"执行命令: {full_command}\n工作目录: {cwd}\n模式: 列表\n"
                
                # 执行命令（使用列表形式）- 隐藏控制台窗口
                result = subprocess.run(
                    cmd_list,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # 替换无法解码的字符
                    timeout=timeout,
                    shell=False,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
                )
            
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            
            success = (result.returncode == 0)
            
            # 添加返回码信息
            output = f"{debug_info}返回码: {result.returncode}\n输出:\n{output}"
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, f"命令执行超时（{timeout}秒）"
        except Exception as e:
            return False, f"命令执行失败: {str(e)}"
    
    def check_and_install_dependencies(self):
        """
        检查并安装必要的npm依赖（特别是搜索插件）
        
        Returns:
            (success, message)
        """
        try:
            import json
            from pathlib import Path
            
            # 检查缓存文件，避免重复检查
            cache_file = self.project_path / ".search_plugin_installed"
            if cache_file.exists():
                return True, "搜索插件已安装（缓存）"
            
            # 检查package.json是否存在
            package_json_path = self.project_path / "package.json"
            if not package_json_path.exists():
                return False, "package.json文件不存在"
            
            # 读取package.json
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            # 检查是否已安装搜索插件
            if '@easyops-cn/docusaurus-search-local' not in dependencies and \
               '@easyops-cn/docusaurus-search-local' not in dev_dependencies:
                
                # 安装搜索插件
                success, output = self.run_command(
                    self.npm_path, 
                    ["install", "@easyops-cn/docusaurus-search-local"]
                )
                
                if success:
                    # 创建缓存文件
                    cache_file.touch()
                    return True, "搜索插件安装成功"
                else:
                    return False, f"搜索插件安装失败: {output}"
            else:
                # 已安装，创建缓存文件
                cache_file.touch()
                return True, "搜索插件已安装"
            
        except Exception as e:
            return False, f"依赖检查异常: {str(e)}"
    
    def local_build_test(self):
        """
        执行本地构建测试
        
        Returns:
            (success, output)
        """
        try:
            output_lines = []
            
            # 0. 检查并安装依赖
            output_lines.append("=== 检查依赖 ===")
            dep_success, dep_message = self.check_and_install_dependencies()
            if not dep_success:
                output_lines.append(f"❌ 依赖检查失败: {dep_message}")
                return False, "\n".join(output_lines)
            output_lines.append(f"✅ {dep_message}")
            
            # 1. 清除缓存
            output_lines.append("\n=== 清除缓存 ===")
            success1, output1 = self.run_command(self.npm_path, ["run", "clear"])
            output_lines.append(output1)
            
            if not success1:
                output_lines.append("❌ 清除缓存失败")
                return False, "\n".join(output_lines)
            output_lines.append("✅ 缓存清除成功")
            
            # 2. 执行构建
            output_lines.append("\n=== 执行构建 ===")
            success2, output2 = self.run_command(self.npm_path, ["run", "build"])
            output_lines.append(output2)
            
            if not success2:
                output_lines.append("❌ 构建失败")
                return False, "\n".join(output_lines)
            output_lines.append("✅ 构建成功")
            
            return True, "\n".join(output_lines)
            
        except Exception as e:
            return False, f"构建测试异常: {str(e)}"
    
    def local_preview(self):
        """
        启动本地预览（自动选择可用端口并确认HTTP可访问）
        
        Returns:
            (success, output)
        """
        try:
            import socket
            import subprocess
            import sys
            import urllib.request
            
            def is_port_open(port=3000, timeout=1):
                # 同时检测 localhost 与 127.0.0.1，避免主机解析差异导致误判
                for host in ("localhost", "127.0.0.1"):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(timeout)
                        result = sock.connect_ex((host, port))
                        sock.close()
                        if result == 0:
                            return True
                    except Exception:
                        continue
                return False
            
            def is_http_accessible(port=3000, timeout=2):
                url = f"http://127.0.0.1:{port}/"
                try:
                    req = urllib.request.Request(url, method="GET")
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        return 200 <= int(resp.status) < 500
                except Exception:
                    return False
            
            # 优先端口：3000，不可用则自动切到3001/3002
            candidate_ports = [3000, 3001, 3002]
            
            # 先检查是否已有可访问服务
            for p in candidate_ports:
                if is_port_open(p) and is_http_accessible(p):
                    self.preview_url = f"http://localhost:{p}"
                    return True, f"本地服务器已在运行 (端口 {p})，请访问 {self.preview_url}"
            
            # 在Windows上隐藏控制台窗口
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                startupinfo = None
                creationflags = 0
            
            launch_errors = []
            
            for port in candidate_ports:
                # 端口被占用但HTTP不可达，直接跳过该端口
                if is_port_open(port) and not is_http_accessible(port):
                    launch_errors.append(f"端口{port}已被占用但HTTP不可访问，已跳过")
                    continue
                
                # 优先使用 serve（更符合“构建后预览”），失败再回退 start
                launch_commands = [
                    [self.npm_path, "run", "serve", "--", "--port", str(port)],
                    [self.npm_path, "start", "--", "--port", str(port)],
                ]
                
                for cmd in launch_commands:
                    process = subprocess.Popen(
                        cmd,
                        cwd=str(self.project_path),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        errors="ignore",
                        startupinfo=startupinfo,
                        shell=False,
                        creationflags=creationflags
                    )
                    
                    self.preview_process = process
                    
                    # 等待最多12秒确认端口已监听+HTTP可访问
                    for _ in range(12):
                        time.sleep(1)
                        if is_port_open(port) and is_http_accessible(port):
                            self.preview_url = f"http://localhost:{port}"
                            return True, f"本地预览服务器已启动，并已确认可访问：{self.preview_url}"
                        
                        # 进程提前退出，记录错误并尝试下一个命令
                        if process.poll() is not None:
                            try:
                                _, stderr = process.communicate(timeout=2)
                                err_text = (stderr or "").strip()
                            except Exception:
                                err_text = ""
                            # 端口已占用且可访问，按成功处理
                            if "already running on port" in err_text.lower() and is_http_accessible(port):
                                self.preview_url = f"http://localhost:{port}"
                                return True, f"检测到端口{port}已有预览服务在运行，可直接访问 {self.preview_url}"
                            launch_errors.append(f"{' '.join(cmd)} -> {err_text[:300]}")
                            break
                    
                    # 若进程未退出但端口仍未开放/不可访问，终止后尝试下一个命令
                    if process.poll() is None and not (is_port_open(port) and is_http_accessible(port)):
                        try:
                            process.terminate()
                        except Exception:
                            pass
                        launch_errors.append(f"{' '.join(cmd)} -> 启动超时，端口{port}未就绪")
            
            details = "；".join(launch_errors) if launch_errors else "未知原因"
            return False, f"本地预览启动失败，3000/3001/3002端口均不可用。详情: {details}"
            
        except Exception as e:
            return False, f"本地预览异常: {str(e)}"
    
    def auto_deploy(self, commit_message=None):
        """
        自动部署到GitHub
        
        Args:
            commit_message: 提交信息，如果为None则自动生成
        
        Returns:
            (success, output)
        """
        try:
            output_lines = []
            
            # 1. 检查Git状态
            output_lines.append("=== Git当前状态 ===")
            success0, output0 = self.run_command(self.git_path, ["status", "--short"])
            output_lines.append(output0)
            
            if not success0:
                return False, "\n".join(output_lines)
            
            # 2. 添加所有更改
            output_lines.append("\n=== Git添加更改 ===")
            success1, output1 = self.run_command(self.git_path, ["add", "."])
            output_lines.append(output1)
            
            if not success1:
                return False, "\n".join(output_lines)
            
            # 3. 提交更改
            output_lines.append("\n=== Git提交 ===")
            if commit_message is None:
                import time
                commit_message = f"自动部署: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            success2, output2 = self.run_command(self.git_path, ["commit", "-m", commit_message])
            output_lines.append(output2)
            
            if not success2:
                # 如果没有更改可提交，继续执行
                if "nothing to commit" in output2.lower():
                    output_lines.append("提示: 没有需要提交的更改")
                else:
                    return False, "\n".join(output_lines)
            
            # 4. 推送到GitHub（带重试机制）
            output_lines.append("\n=== Git推送 ===")
            
            # 尝试推送，最多重试3次
            max_retries = 3
            success3 = False
            output3 = ""
            
            for attempt in range(max_retries):
                if attempt > 0:
                    output_lines.append(f"\n[重试 {attempt}/{max_retries-1}] 网络连接失败，等待5秒后重试...")
                    time.sleep(5)
                
                success3, output3 = self.run_command(self.git_path, ["push", "origin", "master"])
                output_lines.append(output3)
                
                if success3:
                    break
                else:
                    # 检查是否是"already up to date"的情况
                    if "already up to date" in output3.lower():
                        output_lines.append("提示: 远程仓库已经是最新状态")
                        success3 = True
                        break
                    # 检查是否是"non-fast-forward"错误
                    elif "non-fast-forward" in output3.lower():
                        output_lines.append("⚠️ 推送失败: 远程有新的提交")
                        output_lines.append("建议先执行: git pull --rebase origin master")
                        break
                    # 检查是否是"fatal: not a git repository"错误
                    elif "not a git repository" in output3.lower():
                        output_lines.append("❌ 错误: 当前目录不是Git仓库")
                        output_lines.append("请先初始化Git仓库: git init")
                        break
                    # 检查是否是"fatal: remote origin does not exist"错误
                    elif "remote origin does not exist" in output3.lower():
                        output_lines.append("❌ 错误: 远程仓库origin不存在")
                        output_lines.append("请先添加远程仓库: git remote add origin <仓库地址>")
                        break
            
            if not success3:
                # 推送失败，但提交已保存在本地
                output_lines.append("\n⚠️ 推送失败，但提交已保存在本地")
                output_lines.append(f"最后提交: {commit_message}")
                output_lines.append("您可以稍后手动执行: git push origin master")
                return False, "\n".join(output_lines)
            
            # 5. 显示部署成功信息
            output_lines.append("\n✅ 自动部署成功！")
            output_lines.append(f"提交: {commit_message}")
            output_lines.append("网站将在几分钟内自动更新")
            output_lines.append("注意: 如果使用Cloudflare Pages，需要确保仓库已连接")
            
            return True, "\n".join(output_lines)
            
        except Exception as e:
            return False, f"自动部署异常: {str(e)}"
    
    def verify_deployment(self):
        """
        验证部署 - 简单打开部署后的网站主页
        
        Returns:
            (success, output) - 总是返回成功，只打开网页
        """
        try:
            import webbrowser
            
            # 部署后的网站地址 - 使用实际的部署地址
            # 根据实际部署，网站确实存在：https://docs.toothmen.com/docs/NEW-26040902
            # 打开网站首页
            url = "https://docs.toothmen.com"
            
            # 直接打开网页
            webbrowser.open(url)
            
            # 返回简单的成功信息
            return True, f"已打开部署网站: {url}"
            
        except Exception as e:
            # 即使出错也返回成功，只是提示手动访问
            return True, f"自动打开失败，请手动访问: https://docs.toothmen.com"
    
    def get_file_statistics(self) -> Dict[str, any]:
        """
        获取文件统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_folders": 0,
            "total_files": 0,
            "folders": [],
            "reverse_order_folders": []
        }
        
        if not self.docs_folder.exists():
            return stats
        
        # 扫描文件夹结构
        structure = self.scan_folder_structure()
        stats["total_folders"] = len(structure)
        
        for folder_name, files in structure.items():
            folder_info = {
                "name": folder_name,
                "display_name": self.clean_name(folder_name),
                "file_count": len(files),
                "is_reverse_order": self.should_reverse_order(folder_name)
            }
            
            stats["folders"].append(folder_info)
            stats["total_files"] += len(files)
            
            if folder_info["is_reverse_order"]:
                stats["reverse_order_folders"].append(folder_info["display_name"])
        
        return stats
