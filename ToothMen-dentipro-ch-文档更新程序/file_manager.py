#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理模块
负责监控和管理docs-测试中转和docs文件夹中的.mdx文件
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class FileManager:
    def __init__(self, test_folder, prod_folder):
        """
        初始化文件管理器
        
        Args:
            test_folder: 测试中转文件夹路径
            prod_folder: 生产文件夹路径
        """
        self.test_folder = Path(test_folder)
        self.prod_folder = Path(prod_folder)
        
        # 确保文件夹存在
        self.test_folder.mkdir(exist_ok=True)
        self.prod_folder.mkdir(exist_ok=True)
        
        # 加载文件顺序配置
        self.order_config_path = self.prod_folder.parent / "file_order.json"
        self.file_order = self.load_file_order()
    
    def load_file_order(self):
        """加载文件顺序配置"""
        if self.order_config_path.exists():
            try:
                with open(self.order_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_file_order(self):
        """保存文件顺序配置"""
        try:
            with open(self.order_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.file_order, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存文件顺序失败: {e}")
            return False
    
    def get_test_files(self):
        """获取测试文件夹中的所有.mdx文件"""
        try:
            files = list(self.test_folder.glob("*.mdx"))
            # 按修改时间排序（最新的在前面）
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return files
        except Exception as e:
            print(f"获取测试文件失败: {e}")
            return []
    
    def get_prod_files(self):
        """获取生产文件夹中的所有.mdx文件"""
        try:
            files = list(self.prod_folder.glob("*.mdx"))
            
            # 如果有保存的顺序，按顺序排序
            if self.file_order:
                ordered_files = []
                unordered_files = []
                
                for file in files:
                    filename = file.name
                    if filename in self.file_order:
                        ordered_files.append((self.file_order[filename], file))
                    else:
                        unordered_files.append(file)
                
                # 按顺序排序
                ordered_files.sort(key=lambda x: x[0])
                sorted_files = [file for _, file in ordered_files]
                
                # 添加未排序的文件（按文件名排序）
                unordered_files.sort(key=lambda x: x.name)
                sorted_files.extend(unordered_files)
                
                return sorted_files
            else:
                # 按文件名排序
                files.sort(key=lambda x: x.name)
                return files
                
        except Exception as e:
            print(f"获取生产文件失败: {e}")
            return []
    
    def update_prod_order(self, filenames):
        """更新生产文件顺序"""
        try:
            # 创建新的顺序映射
            new_order = {}
            for i, filename in enumerate(filenames):
                new_order[filename] = i
            
            # 更新并保存
            self.file_order = new_order
            self.save_file_order()
            
            return True
        except Exception as e:
            print(f"更新文件顺序失败: {e}")
            return False
    
    def create_file(self, filename, content=None):
        """
        在测试文件夹创建新文件
        
        Args:
            filename: 文件名（可以包含.mdx扩展名）
            content: 文件内容，如果为None则使用模板
        
        Returns:
            (success, message)
        """
        try:
            # 确保文件名以.mdx结尾
            if not filename.endswith('.mdx'):
                filename += '.mdx'
            
            file_path = self.test_folder / filename
            
            # 检查文件是否已存在
            if file_path.exists():
                return False, f"文件 {filename} 已存在"
            
            # 使用模板内容
            if content is None:
                base_name = filename.replace('.mdx', '')
                content = f"""---
title: {base_name}
description: 文档描述
sidebar_position: 1
---

# {base_name}

开始编写您的文档内容...

## 章节标题

文档内容...
"""
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, f"文件 {filename} 创建成功"
            
        except Exception as e:
            return False, f"创建文件失败: {str(e)}"
    
    def delete_file(self, filename, from_test=True):
        """
        删除文件
        
        Args:
            filename: 文件名
            from_test: True=从测试文件夹删除，False=从生产文件夹删除
        
        Returns:
            (success, message)
        """
        try:
            if from_test:
                file_path = self.test_folder / filename
            else:
                file_path = self.prod_folder / filename
            
            # 检查文件是否存在
            if not file_path.exists():
                return False, f"文件 {filename} 不存在"
            
            # 删除文件
            file_path.unlink()
            
            # 如果从生产文件夹删除，更新顺序配置
            if not from_test and filename in self.file_order:
                del self.file_order[filename]
                self.save_file_order()
            
            return True, f"文件 {filename} 删除成功"
            
        except Exception as e:
            return False, f"删除文件失败: {str(e)}"
    
    def rename_file(self, old_name, new_name, from_test=True):
        """
        重命名文件
        
        Args:
            old_name: 原文件名
            new_name: 新文件名
            from_test: True=重命名测试文件，False=重命名生产文件
        
        Returns:
            (success, message)
        """
        try:
            # 确保新文件名以.mdx结尾
            if not new_name.endswith('.mdx'):
                new_name += '.mdx'
            
            if from_test:
                old_path = self.test_folder / old_name
                new_path = self.test_folder / new_name
            else:
                old_path = self.prod_folder / old_name
                new_path = self.prod_folder / new_name
            
            # 检查原文件是否存在
            if not old_path.exists():
                return False, f"文件 {old_name} 不存在"
            
            # 检查新文件是否已存在
            if new_path.exists():
                return False, f"文件 {new_name} 已存在"
            
            # 重命名文件
            old_path.rename(new_path)
            
            # 如果重命名生产文件，更新顺序配置
            if not from_test and old_name in self.file_order:
                self.file_order[new_name] = self.file_order[old_name]
                del self.file_order[old_name]
                self.save_file_order()
            
            return True, f"文件重命名成功: {old_name} → {new_name}"
            
        except Exception as e:
            return False, f"重命名文件失败: {str(e)}"
    
    def move_file(self, filename, to_prod=True):
        """
        移动文件
        
        Args:
            filename: 文件名
            to_prod: True=移动到生产文件夹，False=移动到测试文件夹
        
        Returns:
            (success, message)
        """
        try:
            if to_prod:
                src_path = self.test_folder / filename
                dst_path = self.prod_folder / filename
            else:
                src_path = self.prod_folder / filename
                dst_path = self.test_folder / filename
            
            # 检查源文件是否存在
            if not src_path.exists():
                return False, f"源文件 {filename} 不存在"
            
            # 检查目标文件是否已存在
            if dst_path.exists():
                return False, f"目标文件 {filename} 已存在"
            
            # 移动文件
            shutil.move(str(src_path), str(dst_path))
            
            # 如果从生产文件夹移出，更新顺序配置
            if not to_prod and filename in self.file_order:
                del self.file_order[filename]
                self.save_file_order()
            
            return True, f"文件移动成功: {filename}"
            
        except Exception as e:
            return False, f"移动文件失败: {str(e)}"
    
    def open_file(self, filename, from_test=True):
        """
        用系统默认程序打开文件
        
        Args:
            filename: 文件名
            from_test: True=打开测试文件，False=打开生产文件
        
        Returns:
            (success, message)
        """
        try:
            if from_test:
                file_path = self.test_folder / filename
            else:
                file_path = self.prod_folder / filename
            
            # 检查文件是否存在
            if not file_path.exists():
                return False, f"文件 {filename} 不存在"
            
            # 用系统默认程序打开
            os.startfile(str(file_path))
            
            return True, f"已打开文件: {filename}"
            
        except Exception as e:
            return False, f"打开文件失败: {str(e)}"
    
    def get_file_info(self, filename, from_test=True):
        """
        获取文件信息
        
        Args:
            filename: 文件名
            from_test: True=获取测试文件信息，False=获取生产文件信息
        
        Returns:
            文件信息字典或None
        """
        try:
            if from_test:
                file_path = self.test_folder / filename
            else:
                file_path = self.prod_folder / filename
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            info = {
                'filename': filename,
                'path': str(file_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'is_file': file_path.is_file(),
                'exists': True
            }
            
            return info
            
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    def get_folder_stats(self):
        """获取文件夹统计信息"""
        try:
            test_files = list(self.test_folder.glob("*.mdx"))
            prod_files = list(self.prod_folder.glob("*.mdx"))
            
            stats = {
                'test_folder': {
                    'path': str(self.test_folder),
                    'file_count': len(test_files),
                    'total_size': sum(f.stat().st_size for f in test_files) if test_files else 0
                },
                'prod_folder': {
                    'path': str(self.prod_folder),
                    'file_count': len(prod_files),
                    'total_size': sum(f.stat().st_size for f in prod_files) if prod_files else 0
                }
            }
            
            return stats
            
        except Exception as e:
            print(f"获取文件夹统计失败: {e}")
            return None