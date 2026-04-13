#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试构建问题
"""

import subprocess
import os
from pathlib import Path

print("🔍 测试构建问题")
print("=" * 60)

project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")

def run_command(command, args, cwd=None):
    """模拟程序的run_command方法"""
    try:
        if isinstance(args, list):
            cmd_list = [command] + args
            full_command = f"{command} {' '.join(args)}"
        else:
            cmd_list = [command, args]
            full_command = f"{command} {args}"
        
        print(f"\n执行命令: {full_command}")
        print(f"工作目录: {cwd}")
        
        result = subprocess.run(
            cmd_list,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=False
        )
        
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        
        print(f"返回码: {result.returncode}")
        print(f"输出长度: {len(output)} 字符")
        
        # 检查是否有错误
        if "DebugConfig" in output or "DebugContent" in output or "DebugGlobalData" in output:
            print("⚠️ 检测到调试组件错误")
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if "DebugConfig" in line or "DebugContent" in line or "DebugGlobalData" in line:
                    print(f"  第{i+1}行: {line}")
        
        return result.returncode == 0, output
        
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return False, str(e)

print("1. 模拟程序构建流程:")
print("-" * 40)

# 1. 清理缓存
print("\n步骤1: 清理缓存")
success1, output1 = run_command("npm", ["run", "clear"], cwd=project_path)
print(f"  成功: {success1}")

# 2. 执行构建
print("\n步骤2: 执行构建")
success2, output2 = run_command("npm", ["run", "build"], cwd=project_path)
print(f"  成功: {success2}")

print("\n2. 检查构建结果:")
print("-" * 40)

build_dir = project_path / "build"
if build_dir.exists():
    print(f"✅ build目录存在: {build_dir}")
    
    # 检查文件
    html_files = list(build_dir.rglob("*.html"))
    print(f"  HTML文件数: {len(html_files)}")
    
    # 检查中英文文档
    zh_docs = list((build_dir / "docs").rglob("*.html")) if (build_dir / "docs").exists() else []
    en_docs = list((build_dir / "en" / "docs").rglob("*.html")) if (build_dir / "en" / "docs").exists() else []
    
    print(f"  中文文档: {len(zh_docs)} 个")
    print(f"  英文文档: {len(en_docs)} 个")
    
    # 检查是否有index.html
    if (build_dir / "index.html").exists():
        print("  ✅ 中文首页存在")
    if (build_dir / "en" / "index.html").exists():
        print("  ✅ 英文首页存在")
else:
    print(f"❌ build目录不存在")

print("\n3. 分析问题:")
print("-" * 40)
print("可能的原因:")
print("1. 缓存问题: 程序可能没有正确清理缓存")
print("2. 环境变量: 程序可能缺少某些环境变量")
print("3. 版本冲突: Docusaurus 3.10.0可能有已知问题")
print("4. 输出解析: 程序可能错误解析了构建输出")

print("\n4. 解决方案:")
print("-" * 40)
print("方案A: 修改程序，忽略某些警告")
print("方案B: 降级Docusaurus版本")
print("方案C: 修复调试组件问题")
print("方案D: 修改构建命令参数")

print("\n" + "=" * 60)
print("建议: 检查Docusaurus配置，确保调试功能被禁用")