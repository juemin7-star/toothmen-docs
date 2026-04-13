#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# 测试修复后的路径计算
print("🔍 测试修复后的路径计算")
print("=" * 60)

# 模拟程序中的项目路径
project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
print(f"项目路径: {project_path}")
print(f"项目路径存在: {project_path.exists()}")

# 新方法：使用项目路径
english_docs_path = project_path / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
print(f"\n新方法 - 英文路径: {english_docs_path}")
print(f"新方法 - 路径存在: {english_docs_path.exists()}")

# 旧方法：使用__file__
old_english_docs_path = Path(__file__).parent.parent / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
print(f"\n旧方法 - 英文路径: {old_english_docs_path}")
print(f"旧方法 - 路径存在: {old_english_docs_path.exists()}")

# 检查差异
if english_docs_path.exists() and not old_english_docs_path.exists():
    print("\n⚠️ 发现问题：旧方法路径计算有误！")
    print(f"  新方法路径: {english_docs_path}")
    print(f"  旧方法路径: {old_english_docs_path}")
    print(f"  差异: {english_docs_path != old_english_docs_path}")
elif english_docs_path.exists() and old_english_docs_path.exists():
    print("\n✅ 两种方法都正确")
else:
    print("\n❌ 两种方法都有问题")

# 检查实际内容
if english_docs_path.exists():
    print(f"\n📁 英文目录内容:")
    folders = list(english_docs_path.iterdir())
    print(f"  文件夹数量: {len(folders)}")
    
    for folder in folders:
        if folder.is_dir():
            files = list(folder.glob("*.mdx"))
            print(f"  📁 {folder.name}: {len(files)} 个文件")
            for file in files:
                print(f"    📄 {file.name}")
