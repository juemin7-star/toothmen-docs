#!/usr/bin/env python3
"""
测试中英文双树功能
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

class TestDualTree:
    def __init__(self, root):
        self.root = root
        self.root.title("中英文文档结构管理测试")
        self.root.geometry("1200x600")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格布局：左中文 | 中控制 | 右英文
        main_frame.columnconfigure(0, weight=1)  # 中文Treeview
        main_frame.columnconfigure(1, weight=0)  # 控制面板
        main_frame.columnconfigure(2, weight=1)  # 英文Treeview
        main_frame.rowconfigure(0, weight=1)
        
        # ========== 左侧：中文文档树 ==========
        chinese_frame = ttk.LabelFrame(main_frame, text="📚 中文文档", padding="10")
        chinese_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        chinese_frame.columnconfigure(0, weight=1)
        chinese_frame.rowconfigure(0, weight=1)
        
        self.tree_chinese = ttk.Treeview(chinese_frame, show="tree")
        self.tree_chinese.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_chinese.heading("#0", text="文件/文件夹结构")
        
        # 中文滚动条
        chinese_v_scroll = ttk.Scrollbar(chinese_frame, orient=tk.VERTICAL, command=self.tree_chinese.yview)
        chinese_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_chinese.config(yscrollcommand=chinese_v_scroll.set)
        
        # ========== 中间：控制面板 ==========
        control_frame = ttk.LabelFrame(main_frame, text="🔄 控制面板", padding="10")
        control_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10)
        
        # 文件夹排序按钮
        ttk.Label(control_frame, text="📁 文件夹排序", font=("Arial", 9, "bold")).pack(pady=(10, 5))
        
        self.btn_folder_up = tk.Button(control_frame, text="⬆ 上移文件夹", 
                                      command=self.move_folder_up_both, width=14)
        self.btn_folder_up.pack(pady=3)
        
        self.btn_folder_down = tk.Button(control_frame, text="⬇ 下移文件夹", 
                                        command=self.move_folder_down_both, width=14)
        self.btn_folder_down.pack(pady=3)
        
        # 文件排序按钮
        ttk.Label(control_frame, text="📄 文件排序", font=("Arial", 9, "bold")).pack(pady=(15, 5))
        
        self.btn_file_up = tk.Button(control_frame, text="⬆ 上移文件", 
                                    command=self.move_file_up_both, width=14)
        self.btn_file_up.pack(pady=3)
        
        self.btn_file_down = tk.Button(control_frame, text="⬇ 下移文件", 
                                      command=self.move_file_down_both, width=14)
        self.btn_file_down.pack(pady=3)
        
        # 同步按钮
        ttk.Label(control_frame, text="🔄 同步操作", font=("Arial", 9, "bold")).pack(pady=(20, 5))
        
        self.btn_sync_chinese_to_english = tk.Button(control_frame, text="📥 中→英同步", 
                                                   command=self.sync_chinese_to_english, width=14)
        self.btn_sync_chinese_to_english.pack(pady=3)
        
        self.btn_sync_english_to_chinese = tk.Button(control_frame, text="📤 英→中同步", 
                                                   command=self.sync_english_to_chinese, width=14)
        self.btn_sync_english_to_chinese.pack(pady=3)
        
        # 保存按钮
        self.btn_save_both = tk.Button(control_frame, text="💾 保存双排序", 
                                      command=self.save_both_sort_config, width=14, bg="#4CAF50", fg="white")
        self.btn_save_both.pack(pady=(20, 0))
        
        # ========== 右侧：英文文档树 ==========
        english_frame = ttk.LabelFrame(main_frame, text="🌐 英文文档", padding="10")
        english_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        english_frame.columnconfigure(0, weight=1)
        english_frame.rowconfigure(0, weight=1)
        
        self.tree_english = ttk.Treeview(english_frame, show="tree")
        self.tree_english.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_english.heading("#0", text="File/Folder Structure")
        
        # 英文滚动条
        english_v_scroll = ttk.Scrollbar(english_frame, orient=tk.VERTICAL, command=self.tree_english.yview)
        english_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_english.config(yscrollcommand=english_v_scroll.set)
        
        # 绑定选择事件
        self.tree_chinese.bind('<<TreeviewSelect>>', self.on_chinese_tree_selection)
        self.tree_english.bind('<<TreeviewSelect>>', self.on_english_tree_selection)
        
        # 初始化测试数据
        self.init_test_data()
        
        # 初始化时禁用所有按钮
        self.update_button_states()
    
    def init_test_data(self):
        """初始化测试数据"""
        # 添加中文测试数据
        root_chinese = self.tree_chinese.insert("", 0, text="📂 docs文件夹 (中文)", open=True)
        
        # 添加文件夹
        folder1 = self.tree_chinese.insert(root_chinese, 0, text="📁 主程序安装", open=True)
        self.tree_chinese.insert(folder1, 0, text="📄 主程序安装说明.mdx")
        self.tree_chinese.insert(folder1, 1, text="📄 安装常见问题.mdx")
        
        folder2 = self.tree_chinese.insert(root_chinese, 1, text="📁 云更新服务", open=True)
        self.tree_chinese.insert(folder2, 0, text="📄 云更新服务注册说明.mdx")
        self.tree_chinese.insert(folder2, 1, text="📄 注册规则特殊说明.mdx")
        
        folder3 = self.tree_chinese.insert(root_chinese, 2, text="📁 补丁日志", open=True)
        self.tree_chinese.insert(folder3, 0, text="📄 NEW-26040101.mdx")
        self.tree_chinese.insert(folder3, 1, text="📄 NEW-26040902.mdx")
        
        # 添加英文测试数据
        root_english = self.tree_english.insert("", 0, text="📂 docs文件夹 (英文)", open=True)
        
        # 添加文件夹（与中文相同）
        folder1_en = self.tree_english.insert(root_english, 0, text="📁 主程序安装", open=True)
        self.tree_english.insert(folder1_en, 0, text="📄 主程序安装说明.mdx")
        self.tree_english.insert(folder1_en, 1, text="📄 安装常见问题.mdx")
        
        folder2_en = self.tree_english.insert(root_english, 1, text="📁 云更新服务", open=True)
        self.tree_english.insert(folder2_en, 0, text="📄 云更新服务注册说明.mdx")
        self.tree_english.insert(folder2_en, 1, text="📄 注册规则特殊说明.mdx")
        
        folder3_en = self.tree_english.insert(root_english, 2, text="📁 补丁日志", open=True)
        self.tree_english.insert(folder3_en, 0, text="📄 NEW-26040101.mdx")
        self.tree_english.insert(folder3_en, 1, text="📄 NEW-26040902.mdx")
    
    def on_chinese_tree_selection(self, event):
        """处理中文Treeview选择事件"""
        self.update_button_states()
    
    def on_english_tree_selection(self, event):
        """处理英文Treeview选择事件"""
        self.update_button_states()
    
    def update_button_states(self):
        """更新按钮状态"""
        # 获取中文和英文的选择
        chinese_selection = self.tree_chinese.selection()
        english_selection = self.tree_english.selection()
        
        # 默认禁用所有按钮
        self.btn_folder_up.config(state=tk.DISABLED)
        self.btn_folder_down.config(state=tk.DISABLED)
        self.btn_file_up.config(state=tk.DISABLED)
        self.btn_file_down.config(state=tk.DISABLED)
        
        # 检查是否有选择
        if not chinese_selection and not english_selection:
            return
        
        # 优先使用中文选择，如果没有则使用英文选择
        selection = chinese_selection if chinese_selection else english_selection
        tree = self.tree_chinese if chinese_selection else self.tree_english
        
        if selection:
            item_text = tree.item(selection[0], "text")
            # 判断选中的是文件夹还是文件
            if item_text.startswith("📁"):
                # 选中文件夹，启用文件夹排序按钮
                self.btn_folder_up.config(state=tk.NORMAL)
                self.btn_folder_down.config(state=tk.NORMAL)
            elif item_text.startswith("📄"):
                # 选中文件，启用文件排序按钮
                self.btn_file_up.config(state=tk.NORMAL)
                self.btn_file_down.config(state=tk.NORMAL)
    
    def move_folder_up_both(self):
        """同时上移中英文文件夹"""
        self.move_folder_up(self.tree_chinese)
        self.move_folder_up(self.tree_english)
        print("中英文文件夹已同时上移")
    
    def move_folder_down_both(self):
        """同时下移中英文文件夹"""
        self.move_folder_down(self.tree_chinese)
        self.move_folder_down(self.tree_english)
        print("中英文文件夹已同时下移")
    
    def move_file_up_both(self):
        """同时上移中英文文件"""
        self.move_file_up(self.tree_chinese)
        self.move_file_up(self.tree_english)
        print("中英文文件已同时上移")
    
    def move_file_down_both(self):
        """同时下移中英文文件"""
        self.move_file_down(self.tree_chinese)
        self.move_file_down(self.tree_english)
        print("中英文文件已同时下移")
    
    def move_folder_up(self, tree):
        """上移文件夹（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📁"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                tree.move(item_id, parent, index - 1)
    
    def move_folder_down(self, tree):
        """下移文件夹（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📁"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                tree.move(item_id, parent, index + 1)
    
    def move_file_up(self, tree):
        """上移文件（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📄"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index > 0:
                # 交换位置
                tree.move(item_id, parent, index - 1)
    
    def move_file_down(self, tree):
        """下移文件（通用方法）"""
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = tree.item(item_id, "text")
        
        if not item_text.startswith("📄"):
            return
        
        # 获取父节点和兄弟节点
        parent = tree.parent(item_id)
        siblings = list(tree.get_children(parent))
        
        if item_id in siblings:
            index = siblings.index(item_id)
            if index < len(siblings) - 1:
                # 交换位置
                tree.move(item_id, parent, index + 1)
    
    def sync_chinese_to_english(self):
        """将中文排序同步到英文"""
        print("中文排序已同步到英文")
    
    def sync_english_to_chinese(self):
        """将英文排序同步到中文"""
        print("英文排序已同步到中文")
    
    def save_both_sort_config(self):
        """保存中英文排序配置"""
        print("中英文排序配置已保存")

def main():
    root = tk.Tk()
    app = TestDualTree(root)
    root.mainloop()

if __name__ == "__main__":
    main()