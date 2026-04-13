import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append('.')

from mdx_checker import MDXChecker

# docs文件夹路径
docs_folder = Path(r'D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs')

# 创建检测器
checker = MDXChecker(docs_folder)

print('🔍 MDX文件详细检测报告')
print('=' * 70)

# 查找所有.mdx文件
mdx_files = list(docs_folder.glob('**/*.mdx'))

for mdx_file in mdx_files:
    print(f'\\n📄 文件: {mdx_file.relative_to(docs_folder)}')
    print('-' * 50)
    
    issues = checker.check_single_file(mdx_file)
    
    if not issues:
        print('✅ 语法正确 - 没有发现问题')
    else:
        print(f'❌ 发现 {len(issues)} 个问题:')
        for i, issue in enumerate(issues, 1):
            print(f'  {i}. 类型: {issue[\"type\"]}')
            print(f'     行号: {issue[\"line\"]}')
            print(f'     消息: {issue[\"message\"]}')
            print(f'     建议: {issue[\"suggestion\"]}')
            
            # 显示相关代码行
            try:
                with open(mdx_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    line_num = issue['line']
                    if 1 <= line_num <= len(lines):
                        print(f'     代码: {lines[line_num-1].rstrip()}')
            except:
                pass
            print()

print('=' * 70)
print(f'📊 总结: 共检测 {len(mdx_files)} 个文件')
