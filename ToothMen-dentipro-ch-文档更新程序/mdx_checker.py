#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDX语法检测模块
功能：检测MDX文件中的语法错误，提供修复建议
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class MDXChecker:
    """MDX语法检测器"""
    
    def __init__(self, docs_folder: Path):
        """
        初始化MDX检测器
        
        Args:
            docs_folder: docs文件夹路径
        """
        self.docs_folder = docs_folder
        
    def check_all_mdx_files(self) -> Dict[str, List[Dict]]:
        """
        检查所有MDX文件
        
        Returns:
            字典，键为文件路径，值为问题列表
        """
        results = {}
        
        # 查找所有.mdx文件
        mdx_files = list(self.docs_folder.glob("**/*.mdx"))
        
        for mdx_file in mdx_files:
            issues = self.check_single_file(mdx_file)
            if issues:
                results[str(mdx_file)] = issues
                
        return results
    
    def check_single_file(self, file_path: Path) -> List[Dict]:
        """
        检查单个MDX文件
        
        Args:
            file_path: MDX文件路径
            
        Returns:
            问题列表，每个问题是一个字典
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # 检查1: 未闭合的JSX标签
            issues.extend(self._check_unclosed_jsx_tags(content, lines))
            
            # 检查2: 未闭合的HTML标签
            issues.extend(self._check_unclosed_html_tags(content, lines))
            
            # 检查3: 不匹配的括号
            issues.extend(self._check_unmatched_brackets(content, lines))
            
            # 检查4: 不匹配的引号
            issues.extend(self._check_unmatched_quotes(content, lines))
            
            # 检查5: 不正确的自闭合标签
            issues.extend(self._check_self_closing_tags(content, lines))
            
        except Exception as e:
            issues.append({
                'type': '读取错误',
                'line': 1,
                'message': f'无法读取文件: {str(e)}',
                'suggestion': '检查文件权限或编码格式'
            })
            
        return issues
    
    def _check_unclosed_jsx_tags(self, content: str, lines: List[str]) -> List[Dict]:
        """检查未闭合的JSX标签"""
        issues = []
        
        # 匹配JSX标签：<Component ...> 或 <div ...>
        jsx_pattern = r'<([A-Z][a-zA-Z0-9]*|[a-z][a-z0-9]*)(?:\s+[^>]*)?>'
        closing_pattern = r'</([A-Z][a-zA-Z0-9]*|[a-z][a-z0-9]*)>'
        
        # 查找所有JSX标签
        tag_stack = []
        
        for i, line in enumerate(lines, 1):
            # 查找开始标签
            for match in re.finditer(jsx_pattern, line):
                tag_name = match.group(1)
                # 检查是否是自闭合标签
                if line[match.end()-2] == '/':
                    continue
                tag_stack.append((tag_name, i, match.start()))
            
            # 查找结束标签
            for match in re.finditer(closing_pattern, line):
                tag_name = match.group(1)
                if tag_stack and tag_stack[-1][0] == tag_name:
                    tag_stack.pop()
        
        # 报告未闭合的标签
        for tag_name, line_num, char_pos in tag_stack:
            issues.append({
                'type': '未闭合的JSX标签',
                'line': line_num,
                'message': f'标签 <{tag_name}> 没有闭合',
                'suggestion': f'添加 </{tag_name}> 标签或使用自闭合语法 <{tag_name} ... />'
            })
            
        return issues
    
    def _check_unclosed_html_tags(self, content: str, lines: List[str]) -> List[Dict]:
        """检查未闭合的HTML标签（iframe, div, span等）"""
        issues = []
        
        # 常见的需要闭合的HTML标签
        html_tags = ['iframe', 'div', 'span', 'p', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th']
        
        for tag in html_tags:
            # 查找开始标签
            start_pattern = rf'<{tag}(?:\s+[^>]*)?>'
            # 查找结束标签
            end_pattern = rf'</{tag}>'
            
            start_count = len(re.findall(start_pattern, content, re.IGNORECASE))
            end_count = len(re.findall(end_pattern, content, re.IGNORECASE))
            
            if start_count > end_count:
                # 找到第一个未闭合的标签位置
                for i, line in enumerate(lines, 1):
                    if re.search(start_pattern, line, re.IGNORECASE):
                        issues.append({
                            'type': '未闭合的HTML标签',
                            'line': i,
                            'message': f'HTML标签 <{tag}> 没有闭合',
                            'suggestion': f'添加 </{tag}> 标签或使用自闭合语法 <{tag} ... />'
                        })
                        break
        
        return issues
    
    def _check_unmatched_brackets(self, content: str, lines: List[str]) -> List[Dict]:
        """检查不匹配的括号"""
        issues = []
        
        bracket_pairs = {
            '(': ')',
            '[': ']',
            '{': '}'
        }
        
        for i, line in enumerate(lines, 1):
            stack = []
            
            for j, char in enumerate(line):
                if char in bracket_pairs:
                    stack.append((char, j))
                elif char in bracket_pairs.values():
                    if not stack:
                        issues.append({
                            'type': '不匹配的括号',
                            'line': i,
                            'message': f'多余的闭合括号 "{char}"',
                            'suggestion': '删除多余的括号或添加对应的开始括号'
                        })
                    else:
                        last_open, pos = stack.pop()
                        if bracket_pairs[last_open] != char:
                            issues.append({
                                'type': '不匹配的括号',
                                'line': i,
                                'message': f'括号不匹配: "{last_open}" 和 "{char}"',
                                'suggestion': '修正括号匹配'
                            })
            
            # 检查未闭合的括号
            for open_bracket, pos in stack:
                issues.append({
                    'type': '不匹配的括号',
                    'line': i,
                    'message': f'未闭合的括号 "{open_bracket}"',
                    'suggestion': f'添加对应的闭合括号 "{bracket_pairs[open_bracket]}"'
                })
        
        return issues
    
    def _check_unmatched_quotes(self, content: str, lines: List[str]) -> List[Dict]:
        """检查不匹配的引号"""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # 检查单引号
            single_quotes = line.count("'")
            if single_quotes % 2 != 0:
                issues.append({
                    'type': '不匹配的引号',
                    'line': i,
                    'message': '单引号不匹配',
                    'suggestion': '检查并修正单引号配对'
                })
            
            # 检查双引号
            double_quotes = line.count('"')
            if double_quotes % 2 != 0:
                issues.append({
                    'type': '不匹配的引号',
                    'line': i,
                    'message': '双引号不匹配',
                    'suggestion': '检查并修正双引号配对'
                })
        
        return issues
    
    def _check_self_closing_tags(self, content: str, lines: List[str]) -> List[Dict]:
        """检查不正确的自闭合标签"""
        issues = []
        
        # 常见的自闭合标签
        self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link']
        
        for tag in self_closing_tags:
            # 查找没有自闭合的标签
            pattern = rf'<{tag}(?:\s+[^>]*)?>(?!\s*</{tag}>)'
            
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': '不正确的自闭合标签',
                        'line': i,
                        'message': f'标签 <{tag}> 应该使用自闭合语法',
                        'suggestion': f'将 <{tag} ...> 改为 <{tag} ... />'
                    })
        
        return issues
    
    def get_fix_suggestions(self, issues: List[Dict]) -> List[str]:
        """
        获取修复建议
        
        Args:
            issues: 问题列表
            
        Returns:
            修复建议列表
        """
        suggestions = []
        
        for issue in issues:
            suggestion = f"行 {issue['line']}: {issue['type']} - {issue['message']}"
            suggestion += f"\n    建议: {issue['suggestion']}"
            suggestions.append(suggestion)
            
        return suggestions
    
    def format_report(self, results: Dict[str, List[Dict]]) -> str:
        """
        格式化检测报告
        
        Args:
            results: 检测结果
            
        Returns:
            格式化的报告字符串
        """
        if not results:
            return "[SUCCESS] 所有MDX文件语法检查通过，未发现问题。"
        
        report_lines = ["[INFO] MDX语法检测报告"]
        report_lines.append("=" * 60)
        
        total_issues = 0
        for file_path, issues in results.items():
            report_lines.append(f"\n[FILE] 文件: {os.path.basename(file_path)}")
            report_lines.append(f"      路径: {file_path}")
            report_lines.append(f"      问题数量: {len(issues)}")
            
            total_issues += len(issues)
            
            for issue in issues:
                report_lines.append(f"      - 行 {issue['line']}: {issue['type']}")
                report_lines.append(f"        问题: {issue['message']}")
                report_lines.append(f"        建议: {issue['suggestion']}")
        
        report_lines.append("\n" + "=" * 60)
        report_lines.append(f"[SUMMARY] 总结: 共检测到 {len(results)} 个文件存在 {total_issues} 个问题")
        
        return "\n".join(report_lines)