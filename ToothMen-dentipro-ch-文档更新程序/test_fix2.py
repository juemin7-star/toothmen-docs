#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

print("🔍 测试修复后的逻辑")
print("=" * 60)

# 模拟修复后的逻辑
project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
docs_folder = project_path / "docs"
english_docs_path = project_path / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"

# 映射关系
chinese_to_english = {
    "主程序安装": "main-program-installation",
    "云更新服务": "cloud-update-service", 
    "补丁日志": "patch-log",
    "主程序安装说明.mdx": "main-program-installation-guide.mdx",
    "云更新服务注册说明.mdx": "cloud-update-service-registration-guide.mdx",
    "注册规则特殊说明.mdx": "special-registration-rules.mdx",
    "NEW-26040101.mdx": "patch-new-26040101.mdx",
    "NEW-26040902.mdx": "patch-new-26040902.mdx"
}

# 模拟display_folders
display_folders = ["主程序安装", "云更新服务", "补丁日志"]

# 模拟folder_files_map（修复后的逻辑）
folder_files_map = {
    "主程序安装": ["主程序安装说明.mdx"],
    "云更新服务": ["云更新服务注册说明.mdx", "注册规则特殊说明.mdx"],
    "补丁日志": ["NEW-26040101.mdx", "NEW-26040902.mdx"]
}

print("1. 文件夹文件映射表:")
for folder, files in folder_files_map.items():
    print(f"   📁 {folder}: {files}")

print("\n2. 模拟英文树刷新:")
for folder_name in display_folders:
    english_folder_name = chinese_to_english.get(folder_name, folder_name)
    english_folder_path = english_docs_path / english_folder_name
    
    if english_folder_path.exists():
        print(f"\n   ✅ {folder_name} → {english_folder_name}")
        
        # 获取英文文件
        english_mdx_files = []
        for file in english_folder_path.glob("*.mdx"):
            english_mdx_files.append(file.name)
        
        print(f"      英文文件: {english_mdx_files}")
        
        # 获取对应的文件列表
        folder_sorted_files = folder_files_map.get(folder_name, [])
        print(f"      对应文件列表: {folder_sorted_files}")
        
        # 检查映射
        matched = 0
        total = len(folder_sorted_files)
        
        for file_name in folder_sorted_files:
            english_file_name = chinese_to_english.get(file_name, file_name)
            if english_file_name in english_mdx_files:
                print(f"      ✅ {file_name} → {english_file_name}")
                matched += 1
            else:
                print(f"      ❌ {file_name} → {english_file_name} (未找到)")
        
        print(f"      匹配率: {matched}/{total}")
    else:
        print(f"\n   ❌ {folder_name} → {english_folder_name} (文件夹不存在)")

print("\n" + "=" * 60)
print("预期结果: 所有文件夹都应该正确匹配")
print("修复前问题: 所有文件夹都使用最后一个文件夹的文件列表")
print("修复后: 每个文件夹使用自己的文件列表")
