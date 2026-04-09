#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
提供彩色日志输出和日志文件管理
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import threading

class Logger:
    def __init__(self, log_file=None, level="INFO"):
        """
        初始化日志管理器
        
        Args:
            log_file: 日志文件路径，如果为None则不保存到文件
            level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        """
        self.log_file = Path(log_file) if log_file else None
        self.level = level.upper()
        
        # 日志级别映射
        self.levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "SUCCESS": 25  # 自定义级别，介于INFO和WARNING之间
        }
        
        # 控制台颜色映射
        self.colors = {
            "DEBUG": "\033[90m",      # 灰色
            "INFO": "\033[97m",       # 白色
            "SUCCESS": "\033[92m",    # 绿色
            "WARNING": "\033[93m",    # 黄色
            "ERROR": "\033[91m",      # 红色
            "RESET": "\033[0m"        # 重置
        }
        
        # 线程锁，确保线程安全
        self.lock = threading.Lock()
        
        # 确保日志目录存在
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def set_level(self, level):
        """设置日志级别"""
        level = level.upper()
        if level in self.levels:
            self.level = level
            self.log(f"日志级别已设置为: {level}", "INFO")
        else:
            self.log(f"无效的日志级别: {level}，保持为: {self.level}", "WARNING")
    
    def should_log(self, level):
        """检查是否应该记录该级别的日志"""
        level_num = self.levels.get(level.upper(), 20)  # 默认INFO级别
        current_num = self.levels.get(self.level, 20)
        return level_num >= current_num
    
    def log(self, message, level="INFO"):
        """
        记录日志
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        if not self.should_log(level):
            return
        
        with self.lock:
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 格式化日志消息
            formatted = f"[{timestamp}] [{level.upper()}] {message}"
            
            # 输出到控制台（带颜色）
            self._print_to_console(formatted, level)
            
            # 保存到文件
            if self.log_file:
                self._write_to_file(formatted)
    
    def _print_to_console(self, message, level):
        """输出到控制台（带颜色）"""
        color = self.colors.get(level.upper(), self.colors["INFO"])
        reset = self.colors["RESET"]
        
        print(f"{color}{message}{reset}")
    
    def _write_to_file(self, message):
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception as e:
            # 如果写入失败，尝试输出到控制台
            print(f"\033[91m日志文件写入失败: {e}\033[0m")
    
    def debug(self, message):
        """DEBUG级别日志"""
        self.log(message, "DEBUG")
    
    def info(self, message):
        """INFO级别日志"""
        self.log(message, "INFO")
    
    def success(self, message):
        """SUCCESS级别日志"""
        self.log(message, "SUCCESS")
    
    def warning(self, message):
        """WARNING级别日志"""
        self.log(message, "WARNING")
    
    def error(self, message):
        """ERROR级别日志"""
        self.log(message, "ERROR")
    
    def section(self, title, level="INFO"):
        """记录一个章节标题"""
        line = "=" * 60
        self.log(line, level)
        self.log(f" {title} ", level)
        self.log(line, level)
    
    def progress(self, current, total, message="", level="INFO"):
        """
        记录进度
        
        Args:
            current: 当前进度
            total: 总进度
            message: 附加消息
            level: 日志级别
        """
        if total == 0:
            percentage = 100
        else:
            percentage = int((current / total) * 100)
        
        progress_bar = self._create_progress_bar(percentage)
        progress_msg = f"{progress_bar} {percentage}% ({current}/{total})"
        
        if message:
            progress_msg += f" - {message}"
        
        self.log(progress_msg, level)
    
    def _create_progress_bar(self, percentage, width=20):
        """创建进度条"""
        filled = int(width * percentage / 100)
        empty = width - filled
        
        # 使用ASCII字符避免编码问题
        bar = "[" + "#" * filled + "." * empty + "]"
        return bar
    
    def table(self, headers, rows, level="INFO"):
        """
        记录表格
        
        Args:
            headers: 表头列表
            rows: 行数据列表（每行是一个列表）
            level: 日志级别
        """
        if not headers or not rows:
            return
        
        # 计算每列的最大宽度
        col_widths = []
        for i in range(len(headers)):
            max_width = len(str(headers[i]))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)  # 加2作为padding
        
        # 创建分隔线
        separator = "+" + "+".join(["-" * w for w in col_widths]) + "+"
        
        # 记录表格
        self.log(separator, level)
        
        # 表头
        header_cells = []
        for i, header in enumerate(headers):
            cell = f" {header}".ljust(col_widths[i])
            header_cells.append(cell)
        self.log("|" + "|".join(header_cells) + "|", level)
        
        self.log(separator, level)
        
        # 数据行
        for row in rows:
            row_cells = []
            for i in range(len(headers)):
                if i < len(row):
                    cell = f" {row[i]}".ljust(col_widths[i])
                else:
                    cell = " " * col_widths[i]
                row_cells.append(cell)
            self.log("|" + "|".join(row_cells) + "|", level)
        
        self.log(separator, level)
    
    def clear_log_file(self):
        """清空日志文件"""
        if self.log_file and self.log_file.exists():
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.info(f"日志文件已清空: {self.log_file}")
                return True
            except Exception as e:
                self.error(f"清空日志文件失败: {e}")
                return False
        return False
    
    def get_log_content(self, lines=100):
        """
        获取日志内容
        
        Args:
            lines: 要获取的行数（从末尾开始）
        
        Returns:
            日志内容字符串
        """
        if not self.log_file or not self.log_file.exists():
            return "日志文件不存在"
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            # 获取最后lines行
            start = max(0, len(all_lines) - lines)
            return "".join(all_lines[start:])
            
        except Exception as e:
            return f"读取日志文件失败: {e}"
    
    def get_log_stats(self):
        """获取日志统计信息"""
        if not self.log_file or not self.log_file.exists():
            return {"error": "日志文件不存在"}
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            stats = {
                "total_lines": len(lines),
                "file_size": os.path.getsize(self.log_file),
                "created": datetime.fromtimestamp(os.path.getctime(self.log_file)).strftime('%Y-%m-%d %H:%M:%S'),
                "modified": datetime.fromtimestamp(os.path.getmtime(self.log_file)).strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 统计各级别数量
            level_counts = {}
            for line in lines:
                for level in self.levels:
                    if f"[{level}]" in line:
                        level_counts[level] = level_counts.get(level, 0) + 1
                        break
            
            stats["level_counts"] = level_counts
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}


# 全局日志实例
global_logger = None

def get_logger(log_file=None, level="INFO"):
    """获取全局日志实例"""
    global global_logger
    
    if global_logger is None:
        global_logger = Logger(log_file, level)
    
    return global_logger


if __name__ == "__main__":
    # 测试日志功能
    logger = Logger("test.log", "DEBUG")
    
    logger.section("日志测试")
    logger.debug("这是一条DEBUG消息")
    logger.info("这是一条INFO消息")
    logger.success("这是一条SUCCESS消息")
    logger.warning("这是一条WARNING消息")
    logger.error("这是一条ERROR消息")
    
    # 测试进度条
    logger.section("进度测试")
    for i in range(11):
        logger.progress(i, 10, f"处理项目 {i}")
    
    # 测试表格
    logger.section("表格测试")
    headers = ["ID", "名称", "状态", "进度"]
    rows = [
        [1, "任务A", "进行中", "75%"],
        [2, "任务B", "已完成", "100%"],
        [3, "任务C", "等待中", "0%"],
        [4, "任务D", "错误", "50%"],
    ]
    logger.table(headers, rows)
    
    # 测试日志统计
    stats = logger.get_log_stats()
    logger.info(f"日志统计: {stats}")