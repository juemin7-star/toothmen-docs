#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

# 测试导入
try:
    # 测试映射关系
    from main_correct_layout import ToothMenDocsManager
    
    print("✅ 程序导入成功")
    
    # 创建测试映射
    test_mapping = {
        "主程序安装": "main-program-installation",
        "云更新服务": "cloud-update-service", 
        "补丁日志": "patch-log",
        "主程序安装说明.mdx": "main-program-installation-guide.mdx",
        "云更新服务注册说明.mdx": "cloud-update-service-registration-guide.mdx",
        "注册规则特殊说明.mdx": "special-registration-rules.mdx",
        "NEW-26040101.mdx": "patch-new-26040101.mdx",
        "NEW-26040902.mdx": "patch-new-26040902.mdx"
    }
    
    print("✅ 映射关系测试:")
    for cn, en in test_mapping.items():
        print(f"  {cn} → {en}")
    
    # 测试路径
    project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
    english_path = project_path / "i18n" / "en" / "docusaurus-plugin-content-docs" / "current"
    
    if english_path.exists():
        print(f"✅ 英文目录存在: {english_path}")
        
        # 检查关键文件
        test_files = [
            ("main-program-installation", "main-program-installation-guide.mdx"),
            ("cloud-update-service", "cloud-update-service-registration-guide.mdx"),
            ("cloud-update-service", "special-registration-rules.mdx"),
            ("patch-log", "patch-new-26040101.mdx"),
            ("patch-log", "patch-new-26040902.mdx")
        ]
        
        for folder, file in test_files:
            file_path = english_path / folder / file
            if file_path.exists():
                print(f"  ✅ {folder}/{file} 存在")
            else:
                print(f"  ❌ {folder}/{file} 缺失")
    else:
        print(f"❌ 英文目录不存在")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
