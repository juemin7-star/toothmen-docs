#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试英文目录路径问题
"""

import os
import sys
from pathlib import Path

print("🔍 调试英文目录路径问题")
print("=" * 60)

# 模拟程序中的路径计算
print("1. 模拟程序路径计算:")
print(f"   __file__ (假设): {__file__}")

# 计算父目录的父目录
current_file = Path(__file__)
parent_parent = current_file.parent.parent
print(f"   current_file.parent.parent: {parent_parent}")

# 拼接英文路径
english_docs_path = parent_parent / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
print(f"   英文目录路径: {english_docs_path}")
print(f"   路径是否存在: {english_docs_path.exists()}")

print("\n2. 详细路径检查:")
print(f"   绝对路径: {english_docs_path.absolute()}")
print(f"   解析路径: {english_docs_path.resolve()}")

print("\n3. 检查路径组件:")
components = [
    parent_parent,
    parent_parent / "i18n",
    parent_parent / "i18n" / "en",
    parent_parent / "i18n" / "en" / "docusaurus-plugin-content-docs",
    english_docs_path
]

for comp in components:
    exists = "✅ 存在" if comp.exists() else "❌ 不存在"
    print(f"   {comp.name if comp.name else comp}: {exists}")

print("\n4. 检查目录内容:")
if english_docs_path.exists():
    print(f"   ✅ 目录存在，检查内容:")
    
    # 列出所有项目
    try:
        items = list(english_docs_path.iterdir())
        print(f"   目录项数量: {len(items)}")
        
        for item in items:
            if item.is_dir():
                print(f"   📁 {item.name}")
                # 检查文件夹内的文件
                mdx_files = list(item.glob("*.mdx"))
                print(f"     MDX文件数: {len(mdx_files)}")
                for mdx in mdx_files:
                    print(f"     📄 {mdx.name}")
            else:
                print(f"   📄 {item.name}")
    except Exception as e:
        print(f"   ❌ 列出目录内容失败: {e}")
else:
    print(f"   ❌ 目录不存在")

print("\n5. 权限检查:")
if english_docs_path.exists():
    try:
        # 尝试读取
        test_file = None
        for item in english_docs_path.rglob("*.mdx"):
            if item.is_file():
                test_file = item
                break
        
        if test_file:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read(100)
                print(f"   ✅ 可以读取文件: {test_file.name} (前100字符)")
        else:
            print("   ⚠️ 没有找到测试文件")
            
        # 尝试列出目录
        list(english_docs_path.iterdir())
        print("   ✅ 可以列出目录内容")
        
    except PermissionError as e:
        print(f"   ❌ 权限错误: {e}")
    except Exception as e:
        print(f"   ❌ 其他错误: {e}")

print("\n6. 程序中的实际代码检查:")
print("   在 main_correct_layout.py 中:")
print("   english_docs_path = Path(__file__).parent.parent / 'i18n' / 'en' / 'docusaurus-plugin-content-docs' / 'current'")
print("   if english_docs_path.exists():")
print("       # 正常处理")
print("   else:")
print("       self.log_message('警告：英文文档目录不存在，请先创建英文文档', 'warning')")

print("\n" + "=" * 60)
print("结论: 如果这里显示目录存在，但程序显示不存在，可能是:")
print("1. 程序运行时的当前目录不同")
print("2. 程序有其他地方修改了路径")
print("3. 程序逻辑错误（检查后立即删除或移动了目录）")
print("4. 多线程/异步问题")