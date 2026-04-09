#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MDX检测器
"""

import sys
from pathlib import Path
from mdx_checker import MDXChecker

def main():
    # 设置docs文件夹路径
    docs_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs")
    
    # 创建检测器
    checker = MDXChecker(docs_path)
    
    # 执行检测
    print("开始检测MDX文件语法...")
    results = checker.check_all_mdx_files()
    
    # 输出报告
    report = checker.format_report(results)
    print(report)
    
    # 如果有问题，显示详细建议
    if results:
        print("\n详细修复建议:")
        for file_path, issues in results.items():
            print(f"\n文件: {Path(file_path).name}")
            suggestions = checker.get_fix_suggestions(issues)
            for suggestion in suggestions:
                print(f"  {suggestion}")

if __name__ == "__main__":
    main()