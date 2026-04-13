#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试英文树刷新逻辑
"""

import json
from pathlib import Path

print("🔍 调试英文树刷新逻辑")
print("=" * 60)

# 模拟程序中的变量
project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
docs_folder = project_path / "docs"
english_docs_path = project_path / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"

# 映射关系
chinese_to_english = {
    # 文件夹映射
    "主程序安装": "main-program-installation",
    "云更新服务": "cloud-update-service", 
    "补丁日志": "patch-log",
    # 文件映射
    "主程序安装说明.mdx": "main-program-installation-guide.mdx",
    "云更新服务注册说明.mdx": "cloud-update-service-registration-guide.mdx",
    "注册规则特殊说明.mdx": "special-registration-rules.mdx",
    "NEW-26040101.mdx": "patch-new-26040101.mdx",
    "NEW-26040902.mdx": "patch-new-26040902.mdx"
}

print("1. 基本路径检查:")
print(f"   项目路径: {project_path}")
print(f"   中文文档路径: {docs_folder}")
print(f"   英文文档路径: {english_docs_path}")
print(f"   英文路径存在: {english_docs_path.exists()}")

print("\n2. 检查中文文件夹结构:")
all_folders = []
for item in docs_folder.iterdir():
    if item.is_dir():
        all_folders.append(item.name)

print(f"   中文文件夹数量: {len(all_folders)}")
for folder in all_folders:
    print(f"   📁 {folder}")

print("\n3. 模拟排序配置文件读取:")
sort_config_path = Path(__file__).parent / "sort_config.json"
sort_config = {"folders": [], "files": {}}

if sort_config_path.exists():
    with open(sort_config_path, 'r', encoding='utf-8') as f:
        sort_config = json.load(f)
    print(f"   ✅ 读取排序配置文件: {sort_config_path}")
else:
    print(f"   ⚠️ 排序配置文件不存在: {sort_config_path}")

print("\n4. 模拟display_folders生成:")
display_folders = []
for folder_name in sort_config.get("folders", []):
    if folder_name in all_folders:
        display_folders.append(folder_name)

for folder_name in sorted(all_folders):
    if folder_name not in display_folders:
        display_folders.append(folder_name)

print(f"   display_folders: {display_folders}")

print("\n5. 模拟sorted_files生成（针对第一个文件夹）:")
if display_folders:
    first_folder = display_folders[0]
    folder_path = docs_folder / first_folder
    
    mdx_files = []
    for file in folder_path.glob("*.mdx"):
        mdx_files.append(file.name)
    
    print(f"   文件夹: {first_folder}")
    print(f"   MDX文件: {mdx_files}")
    
    # 模拟配置文件中的文件顺序
    sorted_files = []
    config_files = sort_config.get("files", {}).get(first_folder, [])
    
    print(f"   配置文件中的文件顺序: {config_files}")
    
    for config_file in config_files:
        config_file_with_ext = f"{config_file}.mdx"
        if config_file_with_ext in mdx_files:
            sorted_files.append(config_file_with_ext)
    
    for file_name in sorted(mdx_files):
        if file_name not in sorted_files:
            sorted_files.append(file_name)
    
    print(f"   最终sorted_files: {sorted_files}")

print("\n6. 检查英文文件夹映射:")
for chinese_folder in display_folders:
    english_folder = chinese_to_english.get(chinese_folder, chinese_folder)
    english_folder_path = english_docs_path / english_folder
    
    exists = english_folder_path.exists()
    status = "✅" if exists else "❌"
    
    print(f"   {status} {chinese_folder} → {english_folder} (存在: {exists})")
    
    if exists:
        # 检查英文文件
        english_mdx_files = []
        for file in english_folder_path.glob("*.mdx"):
            english_mdx_files.append(file.name)
        
        print(f"     英文文件: {english_mdx_files}")
        
        # 检查映射关系
        for chinese_file in ["主程序安装说明.mdx", "云更新服务注册说明.mdx", "注册规则特殊说明.mdx", "NEW-26040101.mdx", "NEW-26040902.mdx"]:
            if chinese_file in chinese_to_english:
                english_file = chinese_to_english[chinese_file]
                exists_in_folder = english_file in english_mdx_files
                status_file = "✅" if exists_in_folder else "❌"
                print(f"     {status_file} {chinese_file} → {english_file} (存在: {exists_in_folder})")

print("\n7. 模拟英文树刷新逻辑:")
print("   for folder_name in display_folders:")
print("       english_folder_name = chinese_to_english.get(folder_name, folder_name)")
print("       folder_english_path = english_docs_path / english_folder_name")
print("       ")
print("       if folder_english_path.exists():")
print("           # 获取英文文件夹内的MDX文件")
print("           english_mdx_files = []")
print("           for file in folder_english_path.glob('*.mdx'):")
print("               english_mdx_files.append(file.name)")
print("           ")
print("           # 按照相同的顺序添加文件")
print("           for file_name in sorted_files:")
print("               english_file_name = chinese_to_english.get(file_name, file_name)")
print("               if english_file_name in english_mdx_files:")
print("                   # 添加文件节点")
print("               else:")
print("                   # 显示占位符")

print("\n" + "=" * 60)
print("问题分析:")
print("1. 如果只有patch-log被正确读取，可能是:")
print("   - display_folders顺序问题")
print("   - sorted_files生成问题")
print("   - 映射关系应用时机问题")
print("2. 检查sorted_files是否只包含第一个文件夹的文件")
print("3. 检查循环逻辑是否正确处理每个文件夹")