#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试主程序
"""

import sys
import traceback

# 重定向输出，确保编码正确
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== 开始调试 main_simple_fixed.py ===")

try:
    # 模拟EXE环境
    sys.frozen = True  # 模拟PyInstaller环境
    
    # 导入主模块
    import main_simple_fixed
    
    print("=== 导入成功 ===")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n导入路径:")
    for path in sys.path:
        print(f"  {path}")
    
except Exception as e:
    print(f"其他错误: {e}")
    print("\n完整堆栈跟踪:")
    traceback.print_exc()

input("\n按Enter键退出...")