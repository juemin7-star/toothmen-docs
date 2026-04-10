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
        self.npm_path = "npm"
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
        """清理名称，移除数字前缀和扩展名"""
        # 移除.mdx扩展名
        name = name.replace('.mdx', '')
        
        # 移除数字前缀（支持整数和小数）
        match = re.match(r'^[0-9]+(?:\.[0-9]+)?-(.+)$', name)
        if match:
            return match.group(1)
        
        return name
    
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
        生成侧边栏内容（支持文件夹分类）
        
        Returns:
            sidebars.js内容字符串
        """
        lines = []
        lines.append("const sidebars = {")
        lines.append("  tutorialSidebar: [")
        
        # 扫描文件夹结构
        structure = self.scan_folder_structure()
        if not structure:
            lines.append("    // 暂无文档")
            lines.append("  ],")
            lines.append("};")
            lines.append("")
            lines.append("export default sidebars;")
            return "\n".join(lines)
        
        # 按数字前缀排序文件夹
        sorted_folders = self.sort_by_number_prefix(list(structure.keys()))
        
        for folder_name in sorted_folders:
            files = structure[folder_name]
            
            # 清理文件夹显示名称
            display_name = self.clean_name(folder_name)
            
            # 判断是否需要倒序排序
            is_reverse = self.should_reverse_order(folder_name)
            
            # 按规则排序文件
            sorted_files = self.sort_files_by_rule(files, reverse=is_reverse)
            
            if sorted_files:
                lines.append("    {")
                lines.append(f"      type: 'category',")
                lines.append(f"      label: '{display_name}',")
                lines.append(f"      items: [")
                
                for file_name in sorted_files:
                    # 生成文档ID（Docusaurus格式：文件夹名/文件名）
                    # 例如：1-主程序安装说明.mdx → 程序安装说明/主程序安装说明
                    clean_file_name = self.clean_name(file_name)
                    doc_id = f"{self.clean_name(folder_name)}/{clean_file_name}"
                    lines.append(f"        '{doc_id}',")
                
                lines.append(f"      ],")
                lines.append(f"      collapsed: true,")
                lines.append("    },")
        
        lines.append("  ],")
        lines.append("};")
        lines.append("")
        lines.append("export default sidebars;")
        
        return "\n".join(lines)
    
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
                
                # 执行命令（使用shell模式）
                result = subprocess.run(
                    full_command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # 替换无法解码的字符
                    timeout=timeout,
                    shell=True
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
                
                # 执行命令（使用列表形式）
                result = subprocess.run(
                    cmd_list,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # 替换无法解码的字符
                    timeout=timeout,
                    shell=False
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
        启动本地预览（只启动，不检查是否成功）
        
        Returns:
            (success, output)
        """
        try:
            # 先检查是否已经有服务器在运行
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 3000))
            sock.close()
            
            if result == 0:
                return True, "本地服务器已在运行 (端口 3000)"
            
            # 启动开发服务器（非阻塞方式）
            import subprocess
            import sys
            
            # 使用subprocess.Popen在后台启动
            cmd = f"{self.npm_path} start"
            
            # 在Windows上隐藏控制台窗口
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            else:
                startupinfo = None
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # 存储进程引用，以便后续检查
            self.preview_process = process
            
            # 等待2秒让进程启动
            time.sleep(2)
            
            # 不检查是否成功，只返回启动信息
            return True, "本地预览服务器已启动，请手动访问 http://localhost:3000 确认是否成功"
            
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
            
            return True, "\n".join(output_lines)
            
        except Exception as e:
            return False, f"自动部署异常: {str(e)}"
    
    def verify_deployment(self):
        """
        验证部署状态 - 检查网站可访问性
        
        Returns:
            (success, output)
        """
        try:
            output_lines = []
            
            # 1. 检查Git远程状态
            output_lines.append("=== 检查Git远程状态 ===")
            success1, output1 = self.run_command(self.git_path, ["remote", "-v"])
            output_lines.append(output1)
            
            if not success1:
                return False, "\n".join(output_lines)
            
            # 2. 检查最近提交
            output_lines.append("\n=== 检查最近提交 ===")
            success2, output2 = self.run_command(self.git_path, ["log", "--oneline", "-5"])
            output_lines.append(output2)
            
            if not success2:
                return False, "\n".join(output_lines)
            
            # 3. 检查Cloudflare Pages部署状态
            output_lines.append("\n=== 部署状态 ===")
            output_lines.append("✅ Git推送成功")
            output_lines.append("🌐 Cloudflare Pages会自动构建和部署")
            output_lines.append("📱 网站地址: https://docs.toothmen.com")
            output_lines.append("⏱️ 通常需要1-3分钟完成部署")
            
            # 4. 测试网站可访问性
            output_lines.append("\n=== 测试网站可访问性 ===")
            try:
                import urllib.request
                import urllib.error
                
                url = "https://docs.toothmen.com"
                try:
                    # 设置超时时间为10秒
                    response = urllib.request.urlopen(url, timeout=10)
                    status_code = response.getcode()
                    
                    if status_code == 200:
                        output_lines.append(f"✅ 网站可访问: {url} (状态码: {status_code})")
                        output_lines.append("网站正常运行")
                        
                        # 打开网站
                        import webbrowser
                        webbrowser.open(url)
                        output_lines.append(f"✅ 已打开浏览器访问: {url}")
                    else:
                        output_lines.append(f"⚠️ 网站返回异常状态码: {status_code}")
                        output_lines.append(f"请稍后再试或检查Cloudflare Pages部署状态")
                        
                except urllib.error.HTTPError as e:
                    output_lines.append(f"⚠️ HTTP错误: {e.code} - {e.reason}")
                    output_lines.append(f"网站可能正在构建中，请稍后再试")
                    
                except urllib.error.URLError as e:
                    output_lines.append(f"⚠️ 网络连接错误: {str(e)}")
                    output_lines.append(f"网站可能尚未部署或网络问题")
                    
                except Exception as e:
                    output_lines.append(f"⚠️ 访问网站时出错: {str(e)}")
                    
            except Exception as e:
                output_lines.append(f"⚠️ 测试网站可访问性失败: {str(e)}")
                output_lines.append(f"请手动访问: https://docs.toothmen.com")
            
            return True, "\n".join(output_lines)
            
        except Exception as e:
            return False, f"部署验证异常: {str(e)}"
    
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