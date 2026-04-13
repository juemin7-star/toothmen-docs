#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 测试中英文映射
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

english_to_chinese = {v: k for k, v in chinese_to_english.items()}

print("✅ 中英文映射测试:")
print("=" * 50)

print("📁 文件夹映射:")
for cn, en in [(k, v) for k, v in chinese_to_english.items() if not k.endswith('.mdx')]:
    print(f"  {cn} → {en}")
    print(f"  {en} → {english_to_chinese[en]}")

print("\n📄 文件映射:")
for cn, en in [(k, v) for k, v in chinese_to_english.items() if k.endswith('.mdx')]:
    print(f"  {cn} → {en}")
    print(f"  {en} → {english_to_chinese[en]}")

print("\n🔍 实际目录检查:")
import os
from pathlib import Path

project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
english_path = project_path / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"

if english_path.exists():
    print(f"  ✅ 英文目录存在: {english_path}")
    
    # 检查文件夹
    for cn_folder, en_folder in [(k, v) for k, v in chinese_to_english.items() if not k.endswith('.mdx')]:
        en_folder_path = english_path / en_folder
        if en_folder_path.exists():
            print(f"    ✅ 英文文件夹存在: {en_folder}")
            
            # 检查文件
            for cn_file, en_file in [(k, v) for k, v in chinese_to_english.items() if k.endswith('.mdx')]:
                en_file_path = en_folder_path / en_file
                if en_file_path.exists():
                    print(f"      ✅ 英文文件存在: {en_file}")
                else:
                    print(f"      ❌ 英文文件缺失: {en_file}")
        else:
            print(f"    ❌ 英文文件夹缺失: {en_folder}")
else:
    print(f"  ❌ 英文目录不存在: {english_path}")