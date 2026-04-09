#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署管理模块
负责执行部署工作流：更新侧边栏、构建测试、预览、自动部署
"""

import os
import subprocess
import shutil
import json
from pathlib import Path
import time

class DeploymentManager:
    def __init__(self, project_path):
        """
        初始化部署管理器
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 命令路径配置
        self.npm_path = "npm"
        self.git_path = r"C:\Program Files\Git\cmd\git.exe"
        
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
            except:
                pass
    
    def update_sidebars(self, mdx_files=None):
        """
        根据文件列表更新sidebars.js
        
        Args:
            mdx_files: .mdx文件名列表（不含路径），如果为None则自动从docs文件夹获取
        
        Returns:
            (success, message)
        """
        try:
            # 如果未提供文件列表，自动从docs文件夹获取
            if mdx_files is None:
                docs_folder = self.project_path / "docs"
                if not docs_folder.exists():
                    return False, f"docs文件夹不存在: {docs_folder}"
                
                # 获取所有.mdx文件
                mdx_files = []
                for file_path in docs_folder.glob("*.mdx"):
                    mdx_files.append(file_path.name)
                
                if not mdx_files:
                    return False, "docs文件夹中没有.mdx文件"
                
                # 按文件名排序
                mdx_files.sort()
            
            # 生成sidebars.js内容
            content = self.generate_sidebars_content(mdx_files)
            
            # 备份原文件
            backup_path = self.sidebars_path.with_suffix('.js.backup')
            if self.sidebars_path.exists():
                shutil.copy2(self.sidebars_path, backup_path)
            
            # 写入新内容
            with open(self.sidebars_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "侧边栏更新成功"
            
        except Exception as e:
            return False, f"侧边栏更新失败: {str(e)}"
    
    def generate_sidebars_content(self, mdx_files):
        """
        生成sidebars.js内容
        
        Args:
            mdx_files: .mdx文件名列表
        
        Returns:
            sidebars.js内容字符串
        """
        lines = []
        lines.append("const sidebars = {")
        lines.append("  // 侧边栏显示文档")
        lines.append("  tutorialSidebar: [")
        
        for i, filename in enumerate(mdx_files):
            # 移除.mdx扩展名获取文档ID
            doc_id = filename.replace('.mdx', '')
            
            lines.append("    {")
            lines.append(f"      type: 'doc',")
            lines.append(f"      id: '{doc_id}',")
            lines.append(f"      label: '{doc_id}',")
            lines.append("    },")
        
        lines.append("  ],")
        lines.append("};")
        lines.append("")
        lines.append("export default sidebars;")
        
        return "\n".join(lines)
    
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
    
    def local_build_test(self):
        """
        执行本地构建测试
        
        Returns:
            (success, output)
        """
        try:
            # 1. 清除缓存
            success1, output1 = self.run_command(self.npm_path, ["run", "clear"])
            
            if not success1:
                return False, f"清除缓存失败:\n{output1}"
            
            # 2. 执行构建
            success2, output2 = self.run_command(self.npm_path, ["run", "build"])
            
            return success2, output2
            
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
                    import time
                    time.sleep(5)
                
                success3, output3 = self.run_command(self.git_path, ["push", "origin", "master"])
                output_lines.append(output3)
                
                if success3:
                    break
                else:
                    # 检查是否是网络错误
                    if "Connection was reset" in output3 or "RPC failed" in output3 or "unexpected disconnect" in output3:
                        output_lines.append(f"检测到网络错误，将重试...")
                        continue
                    else:
                        # 其他错误，不重试
                        break
            
            if not success3:
                 output_lines.append(f"\n⚠️ 推送失败，但提交已保存在本地")
                 # 尝试获取最后提交ID
                 try:
                     import subprocess
                     result = subprocess.run(
                         [self.git_path, "log", "--oneline", "-1"],
                         cwd=str(self.project_path),
                         capture_output=True,
                         text=True,
                         encoding='utf-8'
                     )
                     if result.returncode == 0:
                         commit_info = result.stdout.strip()
                         output_lines.append(f"最后提交: {commit_info}")
                     else:
                         output_lines.append("提交ID: 未知（无法获取）")
                 except:
                     output_lines.append("提交ID: 未知（获取失败）")
                 
                 output_lines.append(f"您可以稍后手动执行: git push origin master")
                 
                 # 详细错误分析
                 output_lines.append("\n🔍 错误分析:")
                 error_lower = output3.lower()
                 
                 if "permission denied" in error_lower or "authentication failed" in error_lower:
                     output_lines.append("🔐 检测到认证问题:")
                     output_lines.append("  • SSH密钥配置不正确")
                     output_lines.append("  • GitHub Token无效或过期")
                     output_lines.append("  • 远程仓库权限不足")
                     
                 elif "connection" in error_lower or "timeout" in error_lower or "could not connect" in error_lower:
                     output_lines.append("🌐 检测到网络连接问题:")
                     output_lines.append("  • 网络连接不稳定")
                     output_lines.append("  • 防火墙阻止GitHub连接")
                     output_lines.append("  • DNS解析问题")
                     
                 elif "proxy" in error_lower:
                     output_lines.append("🔄 检测到代理问题:")
                     output_lines.append("  • Git代理设置不正确")
                     output_lines.append("  • 代理服务器不可用")
                     
                 elif "remote origin already exists" in error_lower:
                     output_lines.append("⚙️ 检测到配置问题:")
                     output_lines.append("  • 远程仓库配置冲突")
                     
                 else:
                     output_lines.append("❓ 未知错误类型")
                     output_lines.append(f"  错误详情: {output3[:200]}...")
                 
                 # 提供详细的解决方案
                 output_lines.append("\n💡 解决方案（使用程序内置工具）:")
                 output_lines.append("1. 🔧 点击'Git连接诊断'按钮 - 自动诊断问题")
                 output_lines.append("2. ⚡ 点击'切换到SSH'按钮 - 使用SSH替代HTTPS")
                 output_lines.append("3. 🔄 点击'手动推送Git'按钮 - 手动重试推送")
                 output_lines.append("4. 🌐 点击'测试网络连接'按钮 - 检查网络状态")
                 
                 output_lines.append("\n🔧 手动解决方案:")
                 output_lines.append("1. 检查网络: ping github.com")
                 output_lines.append("2. 清除代理: git config --global --unset http.proxy")
                 output_lines.append("3. 检查配置: git remote -v")
                 output_lines.append("4. 使用SSH: git remote set-url origin git@github.com:juemin7-star/toothmen-docs.git")
                 
                 output_lines.append("\n✅ 您的文档更改已安全保存在本地，不会丢失！")
                 
                 return False, "\n".join(output_lines)
            
            # 5. 等待Cloudflare构建（模拟）
            output_lines.append("\n=== Cloudflare部署 ===")
            output_lines.append("已推送到GitHub，Cloudflare开始自动构建...")
            output_lines.append("构建通常需要2-3分钟完成")
            output_lines.append("部署到全球CDN需要1-2分钟")
            output_lines.append("总计约5分钟后网站完全更新")
            
            return True, "\n".join(output_lines)
            
        except Exception as e:
            return False, f"自动部署异常: {str(e)}"
    
    def check_deployment_status(self):
        """
        检查部署状态（模拟）
        
        Returns:
            状态信息
        """
        # 这里可以集成Cloudflare API来获取真实状态
        # 目前返回模拟信息
        
        status = {
            "github": {
                "last_push": time.strftime('%Y-%m-%d %H:%M:%S'),
                "status": "已同步"
            },
            "cloudflare": {
                "last_build": time.strftime('%Y-%m-%d %H:%M:%S'),
                "status": "构建中",
                "estimated_completion": "2分钟后"
            },
            "website": {
                "url": "https://docs.toothmen.com",
                "status": "更新中",
                "cdn_propagation": "进行中"
            }
        }
        
        return status
    
    def validate_project_structure(self):
        """
        验证项目结构
        
        Returns:
            (valid, issues)
        """
        issues = []
        
        # 检查必要文件
        required_files = [
            "package.json",
            "docusaurus.config.js",
            "sidebars.js",
            "docs/"
        ]
        
        for file in required_files:
            path = self.project_path / file
            if not path.exists():
                issues.append(f"缺少必要文件/目录: {file}")
        
        # 检查Node.js/npm
        try:
            subprocess.run([self.npm_path, "--version"], 
                          capture_output=True, check=True)
        except:
            issues.append("Node.js/npm未正确安装或不在PATH中")
        
        # 检查Git
        try:
            subprocess.run([self.git_path, "--version"], 
                          capture_output=True, check=True)
        except:
            issues.append("Git未正确安装或路径不正确")
        
        valid = (len(issues) == 0)
        return valid, issues
    
    def get_project_info(self):
        """获取项目信息"""
        try:
            info = {
                "project_path": str(self.project_path),
                "sidebars_path": str(self.sidebars_path),
                "docs_folder": str(self.project_path / "docs"),
                "test_folder": str(self.project_path / "docs-测试中转"),
                "npm_path": self.npm_path,
                "git_path": self.git_path,
                "exists": self.project_path.exists()
            }
            
            # 获取文档数量
            if (self.project_path / "docs").exists():
                mdx_files = list((self.project_path / "docs").glob("*.mdx"))
                info["doc_count"] = len(mdx_files)
                info["doc_files"] = [f.name for f in mdx_files]
            else:
                info["doc_count"] = 0
                info["doc_files"] = []
            
            # 获取package.json信息
            package_path = self.project_path / "package.json"
            if package_path.exists():
                try:
                    with open(package_path, 'r', encoding='utf-8') as f:
                        package_info = json.load(f)
                    info["package_name"] = package_info.get("name", "未知")
                    info["package_version"] = package_info.get("version", "未知")
                except:
                    info["package_name"] = "解析失败"
                    info["package_version"] = "解析失败"
            
            return info
            
        except Exception as e:
            return {"error": str(e)}