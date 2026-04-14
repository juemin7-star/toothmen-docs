#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试错误
"""

import sys
import traceback

try:
    # 设置编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 导入并执行主脚本
    sys.path.insert(0, '.')
    
    with open('main_simple_fixed.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 编译并执行
    compiled_code = compile(code, 'main_simple_fixed.py', 'exec')
    exec(compiled_code, {'__name__': '__main__'})
    
except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("\n完整堆栈跟踪:")
    traceback.print_exc()