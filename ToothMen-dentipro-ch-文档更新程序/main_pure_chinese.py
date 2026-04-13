#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen鏂囨。绠＄悊宸ュ叿 - 绠€鍗曠増鏈?"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import sys
import json
import threading
import subprocess
import shutil
import re
from datetime import datetime
from pathlib import Path

# 瀵煎叆鑷畾涔夋ā鍧?from deployment_manager_new import DeploymentManager
from logger import Logger
from mdx_checker import MDXChecker

class ToothMenDocsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ToothMen-DentiPro-涓枃鐗埪锋枃妗ｇ鐞嗙郴缁?v2.2")
        self.root.geometry("1400x1000")
        
        # 椤圭洰璺緞
        self.project_path = Path(r"D:\magicdental寮€鍙戝蹇樺綍\toothmen-瀹樻柟璇存槑鏂囨。绯荤粺\ToothMen-Docs-Simple")
        self.docs_folder = self.project_path / "docs"
        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 纭繚docs鏂囦欢澶瑰瓨鍦?        self.docs_folder.mkdir(exist_ok=True)
        
        # 鍒濆鍖栫鐞嗗櫒
        self.deployment_manager = DeploymentManager(self.project_path)
        self.logger = Logger()
        self.mdx_checker = MDXChecker(self.docs_folder)
        
        # 璁剧疆鏃ュ織鏂囨湰妗?        self.log_text = None
        
        # 閮ㄧ讲娴佺▼鐘舵€?        self.deployment_started = False
        self.deployment_steps = [
            "鍒锋柊鏂囦欢缁撴瀯",
            "鐢熸垚渚ц竟鏍?, 
            "鏈湴鏋勫缓娴嬭瘯",
            "鏈湴棰勮",
            "鑷姩閮ㄧ讲"
        ]
        self.current_step = 0
        
        # 鍒涘缓UI
        self.create_ui()
        
        # 鍒濆鍒锋柊鏂囦欢澶圭粨鏋?        self.refresh_folder_structure()
    
    def create_ui(self):
        """鍒涘缓鐢ㄦ埛鐣岄潰"""
        # 涓绘鏋?        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 閰嶇疆缃戞牸鏉冮噸
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)
        
        # 椤堕儴锛氭爣棰樺拰鎸夐挳鍖哄煙
        self.create_top_area(main_frame)
        
        # 涓儴锛氭枃浠跺す缁撴瀯鏄剧ず
        self.create_folder_structure_area(main_frame)
        
        # 搴曢儴锛氭棩蹇楀尯鍩?        self.create_log_area(main_frame)
    
    def create_top_area(self, parent):
        """鍒涘缓椤堕儴鍖哄煙"""
        top_frame = ttk.Frame(parent)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 鏍囬
        title_label = ttk.Label(top_frame, text="ToothMen鏂囨。绠＄悊绯荤粺", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # 鎸夐挳妗嗘灦
        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=0, column=1, sticky=tk.E)
        
        # 妫€娴婱DX璇硶鎸夐挳
        self.check_mdx_btn = ttk.Button(button_frame, text="妫€娴婱DX璇硶", command=self.check_mdx_syntax)
        self.check_mdx_btn.grid(row=0, column=0, padx=5)
        
        # 閮ㄧ讲娴佺▼鎸夐挳
        self.deploy_start_btn = ttk.Button(button_frame, text="寮€濮嬮儴缃?, command=self.start_deployment)
        self.deploy_start_btn.grid(row=0, column=1, padx=5)
        
        self.deploy_end_btn = ttk.Button(button_frame, text="缁撴潫娴佺▼", command=self.end_deployment, state=tk.DISABLED)
        self.deploy_end_btn.grid(row=0, column=2, padx=5)
        
        # 楠岃瘉閮ㄧ讲鎸夐挳
        self.verify_deploy_btn = ttk.Button(button_frame, text="楠岃瘉閮ㄧ讲", command=self.verify_deployment)
        self.verify_deploy_btn.grid(row=0, column=3, padx=5)
        
        # 閮ㄧ讲姝ラ鎸夐挳
        self.step_buttons = []
        for i, step in enumerate(self.deployment_steps):
            btn = ttk.Button(button_frame, text=step, command=lambda s=step: self.execute_step(s), state=tk.DISABLED)
            btn.grid(row=1, column=i, padx=5, pady=(5, 0))
            self.step_buttons.append(btn)
    
    def create_folder_structure_area(self, parent):
        """鍒涘缓鏂囦欢澶圭粨鏋勬樉绀哄尯鍩?""
        frame = ttk.LabelFrame(parent, text="馃搧 鏂囨。鏂囦欢澶圭粨鏋?, padding="10")
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # 鍒涘缓Treeview
        self.tree = ttk.Treeview(frame, columns=("type", "path"), show="tree", height=15)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 娣诲姞婊氬姩鏉?        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 閰嶇疆鍒?        self.tree.column("#0", width=400)
        self.tree.column("type", width=100)
        self.tree.column("path", width=300)
        
        # 娣诲姞鏍囬
        self.tree.heading("#0", text="鏂囦欢/鏂囦欢澶?)
        self.tree.heading("type", text="绫诲瀷")
        self.tree.heading("path", text="璺緞")
    
    def create_log_area(self, parent):
        """鍒涘缓鏃ュ織鍖哄煙"""
        frame = ttk.LabelFrame(parent, text="馃摑 鎿嶄綔鏃ュ織", padding="10")
        frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # 鍒涘缓鏃ュ織鏂囨湰妗?        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 閰嶇疆鏍囩
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
    
    def log_message(self, message, level="info"):
        """璁板綍鏃ュ織娑堟伅"""
        if self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"
            
            self.log_text.insert(tk.END, log_line, level)
            self.log_text.see(tk.END)
            self.log_text.update()
    
    def refresh_folder_structure(self):
        """鍒锋柊鏂囦欢澶圭粨鏋勬樉绀?""
        try:
            # 娓呯┖鏍?            for item in self.tree.get_children():
                self.tree.delete(item)
            
            total_folders = 0
            total_files = 0
            
            # 娣诲姞鏍硅妭鐐?            root_text = "馃搨 docs鏂囦欢澶?
            self.tree.insert("", 0, text=root_text, values=("鏍圭洰褰?, ""), open=True)
            
            # 鑾峰彇鎵€鏈夋枃浠跺す
            folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    folders.append(item.name)
            
            # 鎸夋暟瀛楀墠缂€鎺掑簭
            sorted_folders = self.sort_by_number_prefix(folders)
            
            for folder_name in sorted_folders:
                total_folders += 1
                folder_path = self.docs_folder / folder_name
                folder_id = self.tree.insert("", tk.END, text=f"馃搧 {folder_name}", values=("鏂囦欢澶?, str(folder_path)), open=True)
                
                # 鑾峰彇鏂囦欢澶瑰唴鐨凪DX鏂囦欢
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                
                # 鍒ゆ柇鏄惁闇€瑕佸€掑簭鎺掑簭
                is_reverse = self.should_reverse_order(folder_name)
                
                # 鎸夎鍒欐帓搴忔枃浠?                sorted_files = self.sort_files_by_rule(mdx_files, reverse=is_reverse)
                
                for file_name in sorted_files:
                    total_files += 1
                    file_path = folder_path / file_name
                    self.tree.insert(folder_id, tk.END, text=f"馃搫 {file_name}", values=("MDX鏂囦欢", str(file_path)))
            
            # 鏇存柊鏍硅妭鐐规枃鏈?            self.tree.item(self.tree.get_children()[0], text=f"馃搨 docs鏂囦欢澶?(鍏眥total_folders}涓垎绫伙紝{total_files}涓狹DX鏂囦欢)")
            
            self.log_message(f"鏂囦欢澶圭粨鏋勫凡鍒锋柊锛屽叡{total_folders}涓垎绫伙紝{total_files}涓狹DX鏂囦欢", "success")
            
        except Exception as e:
            self.log_message(f"鍒锋柊鏂囦欢澶圭粨鏋勫け璐? {str(e)}", "error")
    
    def sort_by_number_prefix(self, items):
        """鎸夋暟瀛楀墠缂€鎺掑簭"""
        def extract_sort_key(item):
            import re
            match = re.match(r'^(\d+)[\-\.]?(.*)', item)
            if match:
                num = int(match.group(1))
                name = match.group(2)
                return (num, name)
            return (float('inf'), item)
        
        return sorted(items, key=extract_sort_key)
    
    def should_reverse_order(self, folder_name):
        """鍒ゆ柇鏄惁闇€瑕佸€掑簭鎺掑簭"""
        reverse_folders = ["琛ヤ竵鏇存柊鏃ュ織", "bugfixlog", "3-bugfixlog"]
        clean_name = self.clean_name(folder_name)
        return clean_name in reverse_folders
    
    def sort_files_by_rule(self, files, reverse=False):
        """鎸夎鍒欐帓搴忔枃浠?""
        def extract_sort_key(item):
            import re
            match = re.match(r'^(\d+)[\-\.]?(.*)', item)
            if match:
                num = int(match.group(1))
                name = match.group(2)
                return (num, name)
            return (float('inf'), item)
        
        sorted_files = sorted(files, key=extract_sort_key, reverse=reverse)
        return sorted_files
    
    def clean_name(self, name):
        """娓呯悊鍚嶇О"""
        if name.endswith('.mdx'):
            name = name[:-4]
        
        import re
        name = re.sub(r'^\d+\-', '', name)
        
        return name
    
    def check_mdx_syntax(self):
        """妫€娴婱DX璇硶"""
        self.log_message("寮€濮嬫娴婱DX璇硶...")
        
        try:
            success_count = 0
            error_count = 0
            
            # 閬嶅巻鎵€鏈夋枃浠跺す
            for folder in self.docs_folder.iterdir():
                if folder.is_dir():
                    # 閬嶅巻鏂囦欢澶瑰唴鐨凪DX鏂囦欢
                    for file in folder.glob("*.mdx"):
                        result = self.mdx_checker.check_single_file(file)
                        if result:
                            self.log_message(f"  鉁?{folder.name}\\{file.name}", "success")
                            success_count += 1
                        else:
                            self.log_message(f"  鉁?{folder.name}\\{file.name}", "error")
                            error_count += 1
            
            self.log_message("=" * 60)
            self.log_message(f"MDX璇硶妫€娴嬪畬鎴?")
            self.log_message(f"  鎬绘枃浠舵暟: {success_count + error_count}")
            self.log_message(f"  閿欒鏂囦欢: {error_count}")
            
            if error_count == 0:
                self.log_message("鎵€鏈塎DX鏂囦欢璇硶姝ｇ‘锛?, "success")
            else:
                self.log_message(f"鍙戠幇{error_count}涓敊璇枃浠讹紝璇锋鏌?, "error")
                
        except Exception as e:
            self.log_message(f"妫€娴婱DX璇硶澶辫触: {str(e)}", "error")
    
    def start_deployment(self):
        """寮€濮嬮儴缃叉祦绋?""
        self.deployment_started = True
        self.current_step = 0
        self.deploy_start_btn.config(state=tk.DISABLED)
        self.deploy_end_btn.config(state=tk.NORMAL)
        
        # 鍚敤绗竴涓楠ゆ寜閽?        if self.step_buttons:
            self.step_buttons[0].config(state=tk.NORMAL)
        
        self.log_message("閮ㄧ讲娴佺▼宸插紑濮嬶紝璇锋寜椤哄簭鎵ц姝ラ")
        self.log_message("姝ラ1: 鍒锋柊鏂囦欢缁撴瀯 鈫?姝ラ2: 鐢熸垚渚ц竟鏍?鈫?姝ラ3: 鏈湴鏋勫缓娴嬭瘯 鈫?姝ラ4: 鏈湴棰勮 鈫?姝ラ5: 鑷姩閮ㄧ讲")
    
    def end_deployment(self):
        """缁撴潫閮ㄧ讲娴佺▼"""
        self.deployment_started = False
        self.current_step = 0
        self.deploy_start_btn.config(state=tk.NORMAL)
        self.deploy_end_btn.config(state=tk.DISABLED)
        
        # 绂佺敤鎵€鏈夋楠ゆ寜閽?        for btn in self.step_buttons:
            btn.config(state=tk.DISABLED)
        
        self.log_message("閮ㄧ讲娴佺▼宸茬粨鏉?, "success")
    
    def execute_step(self, step_name):
        """鎵ц閮ㄧ讲姝ラ"""
        if not self.deployment_started:
            return
        
        # 鏇存柊鎸夐挳鐘舵€?        step_index = self.deployment_steps.index(step_name)
        if step_index != self.current_step:
            self.log_message(f"璇锋寜椤哄簭鎵ц姝ラ锛屽綋鍓嶅簲鎵ц: {self.deployment_steps[self.current_step]}", "warning")
            return
        
        # 鎵ц姝ラ
        if step_name == "鍒锋柊鏂囦欢缁撴瀯":
            self.refresh_folder_structure_thread()
        elif step_name == "鐢熸垚渚ц竟鏍?:
            self.generate_sidebar_thread()
        elif step_name == "鏈湴鏋勫缓娴嬭瘯":
            self.local_build_test_thread()
        elif step_name == "鏈湴棰勮":
            self.local_preview_thread()
        elif step_name == "鑷姩閮ㄧ讲":
            self.auto_deploy_thread()
        
        # 鏇存柊褰撳墠姝ラ
        self.current_step += 1
        
        # 鍚敤涓嬩竴涓楠ゆ寜閽?        if self.current_step < len(self.step_buttons):
            self.step_buttons[self.current_step].config(state=tk.NORMAL)
    
    def refresh_folder_structure_thread(self):
        """鍒锋柊鏂囦欢澶圭粨鏋勭嚎绋?""
        thread = threading.Thread(target=self.refresh_folder_structure)
        thread.daemon = True
        thread.start()
    
    def generate_sidebar_thread(self):
        """鐢熸垚渚ц竟鏍忕嚎绋?""
        thread = threading.Thread(target=self.generate_sidebar)
        thread.daemon = True
        thread.start()
    
    def generate_sidebar(self):
        """鐢熸垚渚ц竟鏍?""
        self.log_message("寮€濮嬬敓鎴愪晶杈规爮...")
        
        try:
            sidebar_content = self.deployment_manager.generate_sidebar_content()
            
            # 淇濆瓨鍒版枃浠?            with open(self.sidebars_path, 'w', encoding='utf-8') as f:
                f.write(sidebar_content)
            
            self.log_message(f"渚ц竟鏍忕敓鎴愭垚鍔燂紒", "success")
            self.log_message(f"鏂囦欢宸蹭繚瀛? {self.sidebars_path}")
            
            # 鏄剧ず鐢熸垚鐨勪晶杈规爮缁撴瀯
            self.log_message("鐢熸垚鐨勪晶杈规爮缁撴瀯:")
            self.log_message("-" * 40)
            for line in sidebar_content.split('\n'):
                if line.strip():
                    self.log_message(f"  {line}")
            self.log_message("-" * 40)
            
            self.log_message("渚ц竟鏍忓凡鎴愬姛鐢熸垚骞朵繚瀛橈紒", "success")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?            if self.deployment_started:
                step_index = self.deployment_steps.index("鐢熸垚渚ц竟鏍?)
                self.step_buttons[step_index].config(state=tk.DISABLED)
                self.log_message(f"宸茶В閿佹楠?{self.current_step + 1}: {self.deployment_steps[self.current_step]}")
                
        except Exception as e:
            self.log_message(f"鐢熸垚渚ц竟鏍忓け璐? {str(e)}", "error")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?            if self.deployment_started:
                step_index = self.deployment_steps.index("鐢熸垚渚ц竟鏍?)
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
    def local_build_test_thread(self):
        """鏈湴鏋勫缓娴嬭瘯绾跨▼"""
        thread = threading.Thread(target=self.local_build_test)
        thread.daemon = True
        thread.start()
    
    def local_build_test(self):
        """鏈湴鏋勫缓娴嬭瘯"""
        self.log_message("寮€濮嬫湰鍦版瀯寤烘祴璇?..")
        
        try:
            success, output = self.deployment_manager.local_build_test()
            if success:
                self.log_message("鏈湴鏋勫缓娴嬭瘯鎴愬姛锛?, "success")
                self.log_message("鏈湴鏋勫缓娴嬭瘯鎴愬姛锛屽彲浠ョ户缁笅涓€姝?)
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?                if self.deployment_started:
                    step_index = self.deployment_steps.index("鏈湴鏋勫缓娴嬭瘯")
                    self.step_buttons[step_index].config(state=tk.DISABLED)
                    self.log_message(f"宸茶В閿佹楠?{self.current_step + 1}: {self.deployment_steps[self.current_step]}")
            else:
                self.log_message("鏈湴鏋勫缓娴嬭瘯澶辫触", "error")
                self.log_message("鏈湴鏋勫缓娴嬭瘯澶辫触锛岃鏌ョ湅鏃ュ織", "error")
                
                # 鏄剧ず璇︾粏閿欒淇℃伅
                for line in output.split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?                if self.deployment_started:
                    step_index = self.deployment_steps.index("鏈湴鏋勫缓娴嬭瘯")
                    self.step_buttons[step_index].config(state=tk.NORMAL)
                    
        except Exception as e:
            self.log_message(f"鏈湴鏋勫缓娴嬭瘯寮傚父: {str(e)}", "error")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?            if self.deployment_started:
                step_index = self.deployment_steps.index("鏈湴鏋勫缓娴嬭瘯")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
    def local_preview_thread(self):
        """鏈湴棰勮绾跨▼"""
        thread = threading.Thread(target=self.local_preview)
        thread.daemon = True
        thread.start()
    
    def local_preview(self):
        """鏈湴棰勮"""
        self.log_message("寮€濮嬫湰鍦伴瑙?..")
        
        try:
            success, output = self.deployment_manager.local_preview()
            if success:
                self.log_message("鏈湴棰勮鏈嶅姟鍣ㄥ凡鍚姩锛?, "success")
                self.log_message("鏈湴棰勮鏈嶅姟鍣ㄥ凡鍚姩锛岃鍦ㄦ祻瑙堝櫒涓煡鐪?)
                
                # 寤惰繜鍚庤嚜鍔ㄦ墦寮€娴忚鍣?                self.log_message("鏈嶅姟鍣ㄥ凡鍚姩锛?绉掑悗鑷姩鎵撳紑娴忚鍣?..")
                self.root.after(3000, self.open_local_preview)
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?                if self.deployment_started:
                    step_index = self.deployment_steps.index("鏈湴棰勮")
                    self.step_buttons[step_index].config(state=tk.DISABLED)
                    self.log_message(f"宸茶В閿佹楠?{self.current_step + 1}: {self.deployment_steps[self.current_step]}")
            else:
                self.log_message("鍚姩鏈湴棰勮澶辫触", "error")
                self.log_message("鍚姩鏈湴棰勮澶辫触锛岃鏌ョ湅鏃ュ織", "error")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?                if self.deployment_started:
                    step_index = self.deployment_steps.index("鏈湴棰勮")
                    self.step_buttons[step_index].config(state=tk.NORMAL)
                    
        except Exception as e:
            self.log_message(f"鍚姩鏈湴棰勮寮傚父: {str(e)}", "error")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?            if self.deployment_started:
                step_index = self.deployment_steps.index("鏈湴棰勮")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
    def open_local_preview(self):
        """鑷姩鎵撳紑鏈湴棰勮椤甸潰"""
        try:
            import webbrowser
            import time
            
            # 绛夊緟鏈嶅姟鍣ㄥ畬鍏ㄥ惎鍔?            self.log_message("绛夊緟鏈嶅姟鍣ㄥ畬鍏ㄥ惎鍔?..")
            time.sleep(5)
            
            # 鎵撳紑缃戠珯棣栭〉
            url = "http://localhost:3000"
            
            # 鍚屾椂鏄剧ず鍙敤鐨勬枃妗ｉ摼鎺?            self.log_message("宸叉墦寮€缃戠珯棣栭〉锛屽彲鐢ㄦ枃妗ｉ摼鎺?")
            
            # 浠庝晶杈规爮涓幏鍙栨墍鏈夋枃妗ｉ摼鎺?            if self.sidebars_path.exists():
                try:
                    with open(self.sidebars_path, 'r', encoding='utf-8') as f:
                        sidebar_content = f.read()
                    
                    # 鎻愬彇鎵€鏈夋枃妗D
                    import re
                    doc_ids = re.findall(r"'([^']+/[^']+)'", sidebar_content)
                    
                    if doc_ids:
                        for doc_id in doc_ids:
                            doc_url = f"http://localhost:3000/docs/{doc_id}"
                            self.log_message(f"  鈥?{doc_id}: {doc_url}")
                        
                        # 鍚屾椂鑷姩鎵撳紑绗竴涓枃妗?                        first_doc_id = doc_ids[0]
                        first_doc_url = f"http://localhost:3000/docs/{first_doc_id}"
                        self.log_message(f"鍚屾椂鎵撳紑绗竴涓枃妗? {first_doc_url}")
                        webbrowser.open(first_doc_url)
                    else:
                        self.log_message("  鈥?鏈壘鍒版枃妗ｉ摼鎺?)
                        webbrowser.open(url)
                except Exception as e:
                    self.log_message(f"  鈥?璇诲彇渚ц竟鏍忓け璐? {str(e)}")
                    webbrowser.open(url)
            else:
                self.log_message("  鈥?渚ц竟鏍忔枃浠朵笉瀛樺湪")
                webbrowser.open(url)
            
            self.log_message(f"宸茶嚜鍔ㄦ墦寮€娴忚鍣ㄨ闂? {url}", "success")
            
        except Exception as e:
            self.log_message(f"鑷姩鎵撳紑娴忚鍣ㄥけ璐? {str(e)}", "error")
            self.log_message("璇锋墜鍔ㄨ闂? http://localhost:3000")
    
    def auto_deploy_thread(self):
        """鑷姩閮ㄧ讲绾跨▼"""
        thread = threading.Thread(target=self.auto_deploy)
        thread.daemon = True
        thread.start()
    
    def auto_deploy(self):
        """鑷姩閮ㄧ讲"""
        self.log_message("寮€濮嬭嚜鍔ㄩ儴缃?..")
        
        try:
            success, output = self.deployment_manager.auto_deploy()
            if success:
                self.log_message("鑷姩閮ㄧ讲鎴愬姛锛?, "success")
                self.log_message("缃戠珯宸叉垚鍔熼儴缃插埌GitHub Pages")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€佸苟缁撴潫娴佺▼
                if self.deployment_started:
                    step_index = self.deployment_steps.index("鑷姩閮ㄧ讲")
                    self.step_buttons[step_index].config(state=tk.DISABLED)
                    self.end_deployment()
            else:
                self.log_message("鑷姩閮ㄧ讲澶辫触", "error")
                self.log_message("鑷姩閮ㄧ讲澶辫触锛岃鏌ョ湅鏃ュ織", "error")
                
                # 鏄剧ず璇︾粏閿欒淇℃伅
                for line in output.split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?                if self.deployment_started:
                    step_index = self.deployment_steps.index("鑷姩閮ㄧ讲")
                    self.step_buttons[step_index].config(state=tk.NORMAL)
                    
        except Exception as e:
            self.log_message(f"鑷姩閮ㄧ讲寮傚父: {str(e)}", "error")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€?            if self.deployment_started:
                step_index = self.deployment_steps.index("鑷姩閮ㄧ讲")
                self.step_buttons[step_index].config(state=tk.NORMAL)
    
    def verify_deployment(self):
        """楠岃瘉閮ㄧ讲"""
        self.log_message("寮€濮嬮獙璇侀儴缃?..")
        
        try:
            import webbrowser
            webbrowser.open("https://docs.toothmen.com")
            self.log_message("宸叉墦寮€閮ㄧ讲缃戠珯: https://docs.toothmen.com", "success")
            
        except Exception as e:
            self.log_message(f"楠岃瘉閮ㄧ讲澶辫触: {str(e)}", "error")

def main():
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
