#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的排序逻辑
"""

import sys
from pathlib import Path
import json

# 添加当前目录到路径
sys.path.append('.')

# 模拟docs文件夹结构
docs_folder = Path(r'D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs')

print("📁 测试新的排序逻辑")
print("=" * 70)

# 1. 检查当前文件夹结构
print("\n1. 当前文件夹结构:")
folders = []
for item in docs_folder.iterdir():
    if item.is_dir():
        folders.append(item.name)
        print(f"   📁 {item.name}")

print(f"\n   共 {len(folders)} 个文件夹")

# 2. 检查排序配置文件
print("\n2. 排序配置文件:")
sort_config_path = Path(__file__).parent / "sort_config.json"
if sort_config_path.exists():
    with open(sort_config_path, 'r', encoding='utf-8') as f:
        sort_config = json.load(f)
    
    print(f"   文件夹顺序: {sort_config.get('folders', [])}")
    print(f"   文件配置: {sort_config.get('files', {})}")
else:
    print("   ❌ 排序配置文件不存在")

# 3. 模拟新的排序逻辑
print("\n3. 模拟新的排序逻辑:")
print("   - 不使用数字前缀排序")
print("   - 完全通过上下移动实现排序")
print("   - 从sort_config.json读取排序顺序")

# 4. 测试排序逻辑
print("\n4. 测试排序逻辑实现:")

# 模拟refresh_folder_structure方法中的逻辑
all_folders = []
for item in docs_folder.iterdir():
    if item.is_dir():
        all_folders.append(item.name)

print(f"   所有文件夹: {all_folders}")

# 如果有排序配置，按配置显示
if sort_config_path.exists():
    display_folders = []
    
    # 先添加排序配置文件中指定的文件夹
    for folder_name in sort_config.get("folders", []):
        if folder_name in all_folders:
            display_folders.append(folder_name)
    
    # 再添加其他文件夹（按字母顺序）
    for folder_name in sorted(all_folders):
        if folder_name not in display_folders:
            display_folders.append(folder_name)
    
    print(f"   显示顺序: {display_folders}")
else:
    print(f"   显示顺序（按字母）: {sorted(all_folders)}")

# 5. 检查每个文件夹中的文件
print("\n5. 文件夹中的文件:")
for folder_name in all_folders:
    folder_path = docs_folder / folder_name
    mdx_files = []
    for file in folder_path.glob("*.mdx"):
        mdx_files.append(file.name)
    
    print(f"   📁 {folder_name}: {len(mdx_files)} 个文件")
    for file in mdx_files:
        print(f"      📄 {file}")

print("\n" + "=" * 70)
print("✅ 测试完成")
print("\n说明:")
print("1. 现在文件夹和文件都没有数字前缀")
print("2. 完全通过上下移动文件夹和文件来实现排序")
print("3. 排序配置保存在 sort_config.json 中")
print("4. 刷新时会按照配置文件的顺序显示")
print("5. 新文件夹/文件会按字母顺序添加到末尾")