﻿#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToothMen鏂囨。绠＄悊宸ュ叿 - 鍏ㄦ柊鐗堟湰
鍔熻兘锛氭枃浠跺す鍒嗙被绠＄悊 + 鑷姩鍖栭儴缃插伐浣滄祦
鎸夌収鏁板瓧鍓嶇紑鏂囦欢澶圭粨鏋勮嚜鍔ㄧ敓鎴愬垎绫讳晶杈规爮
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import json
import threading
import subprocess
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 瀵煎叆鑷畾涔夋ā?from deployment_manager_new import DeploymentManager
from logger import Logger
from mdx_checker import MDXChecker

class ToothMenDocsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ToothMen-DentiPro-涓枃鐗埪锋枃妗ｇ鐞嗙郴?v2.3 - 鏂板鎺掑簭鎺у埗鍔熻兘")
        self.root.geometry("1400x1000")
        
        # 璁剧疆鍥炬爣
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # 椤圭洰璺緞
        self.project_path = Path(r"D:\magicdental寮€鍙戝蹇樺綍\toothmen-瀹樻柟璇存槑鏂囨。绯荤粺\ToothMen-Docs-Simple")
        self.docs_folder = self.project_path / "docs"  # 鐩存帴鐩戞帶docs鏂囦欢?        self.sidebars_path = self.project_path / "sidebars.js"
        
        # 纭繚docs鏂囦欢澶瑰瓨?        self.docs_folder.mkdir(exist_ok=True)
        
        # 鍒濆鍖栫鐞嗗櫒
        self.deployment_manager = DeploymentManager(self.project_path)
        self.logger = Logger()
        self.mdx_checker = MDXChecker(self.docs_folder)
        
        # 鐗规畩鏂囦欢澶归厤缃紙闇€瑕佸€掑簭鎺掑簭?        self.reverse_order_folders = ["琛ヤ竵鏇存柊鏃ュ織", "patch-notes", "鏇存柊璁板綍", "changelog"]
        
        # 鍔犺浇閰嶇疆
        self.config = self.load_config()
        
        # 鍒涘缓UI
        self.create_widgets()
        
        # 鍒濆鍔犺浇鏂囦欢澶圭粨?        self.refresh_folder_structure()
        
    def load_config(self):
        """鍔犺浇閰嶇疆鏂囦欢"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 榛樿閰嶇疆
            default_config = {
                "project_path": str(self.project_path),
                "docs_folder": str(self.docs_folder),
                "sidebars_path": str(self.sidebars_path),
                "npm_path": "npm",
                "git_path": r"C:\Program Files\Git\cmd\git.exe",
                "auto_refresh": True,
                "log_level": "INFO",
                "reverse_order_folders": self.reverse_order_folders
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def create_widgets(self):
        """鍒涘缓UI缁勪欢"""
        # 涓绘?        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 閰嶇疆缃戞牸鏉冮噸 - 鏂囦欢澶圭粨鏋勫崰鎹叏閮ㄥ搴︼紝鏃ュ織鍜岃皟璇曞伐鍏峰湪涓嬮潰
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 鏂囦欢澶圭粨鏋勶紙鍗犲叏閮ㄥ搴︼級
        main_frame.columnconfigure(1, weight=0)  # 璋冭瘯宸ュ叿锛堝浐瀹氬搴︼級
        main_frame.rowconfigure(0, weight=0)  # 鏍囬?        main_frame.rowconfigure(1, weight=1)  # 鏂囦欢澶圭粨鏋勫尯?        main_frame.rowconfigure(2, weight=0)  # 鎺у埗鎸夐挳鍖哄煙
        main_frame.rowconfigure(3, weight=1)  # 鏃ュ織鍜岃皟璇曞伐鍏峰尯?        
        # 鍒涘缓椤堕儴鏍囬
        title_label = ttk.Label(main_frame, text="ToothMen-DentiPro-涓枃鐗埪锋枃妗ｇ鐞嗙郴?v2.0", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 鍒涘缓鏂囦欢澶圭粨鏋勫尯鍩燂紙鍗犳嵁鍏ㄩ儴瀹藉害?        self.create_folder_structure_area(main_frame)
        
        # 鍒涘缓鎺у埗鎸夐挳鍖哄煙
        self.create_control_area(main_frame)
        
        # 鍒涘缓鏃ュ織鍜岃皟璇曞伐鍏峰尯?        self.create_log_and_debug_area(main_frame)
        
    def create_folder_structure_area(self, parent):
        """鍒涘缓鏂囦欢澶圭粨鏋勬樉绀哄尯鍩?""
        # 鏂囦欢澶圭粨鏋勬鏋?
        folder_frame = ttk.LabelFrame(parent, text="鏂囨。鏂囦欢澶圭粨鏋?, padding="10")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        folder_frame.columnconfigure(1, weight=0)  # 鍨傜洿婊氬姩鏉″垪
        folder_frame.columnconfigure(2, weight=0)  # 鎺掑簭鎸夐挳鍒?
        folder_frame.rowconfigure(0, weight=1)
        folder_frame.rowconfigure(1, weight=0)  # 姘村钩婊氬姩鏉¤
        
        # 鍒涘缓Treeview鏄剧ず鏂囦欢澶圭粨鏋?- 鍙樉绀哄悕绉板拰绫诲瀷锛屼笉鏄剧ず鏁伴噺
        self.tree = ttk.Treeview(folder_frame, columns=("type"), show="tree headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 璁剧疆鏍囬
        self.tree.heading("#0", text="鏂囦欢/鏂囦欢澶瑰悕绉?)
        self.tree.heading("type", text="绫诲瀷")
        
        # 璁剧疆鍒楀搴?- 杩涗竴姝ョ缉灏忓搴︼紝涓烘寜閽暀鍑烘洿澶氱┖闂?
        self.tree.column("#0", width=350, minwidth=250)  # 杩涗竴姝ョ缉灏忓搴?
        self.tree.column("type", width=70, minwidth=50)  # 杩涗竴姝ョ缉灏忓搴?
        
        # 鍨傜洿婊氬姩鏉?
        v_scrollbar = ttk.Scrollbar(folder_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.config(yscrollcommand=v_scrollbar.set)
        
        # 姘村钩婊氬姩鏉★紙鏂囦欢澶氭椂鏂逛究鏌ョ湅锛?
        h_scrollbar = ttk.Scrollbar(folder_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.config(xscrollcommand=h_scrollbar.set)
        
        # 鍒涘缓鎺掑簭鎸夐挳鍖哄煙锛堝湪Treeview鍙充晶锛?
        sort_button_frame = ttk.Frame(folder_frame)
        sort_button_frame.grid(row=0, column=2, sticky=(tk.N, tk.S), padx=(10, 0))
        
        # 鏂囦欢澶规帓搴忔寜閽?
        ttk.Label(sort_button_frame, text="鏂囦欢澶规帓搴?").pack(pady=(0, 5))
        
        self.btn_folder_up = tk.Button(sort_button_frame, text="猬?涓婄Щ", 
                                      command=self.move_folder_up, width=10)
        self.btn_folder_up.pack(pady=2)
        
        self.btn_folder_down = tk.Button(sort_button_frame, text="猬?涓嬬Щ", 
                                        command=self.move_folder_down, width=10)
        self.btn_folder_down.pack(pady=2)
        
        # 鏂囦欢鎺掑簭鎸夐挳
        ttk.Label(sort_button_frame, text="鏂囦欢鎺掑簭:").pack(pady=(10, 5))
        
        self.btn_file_up = tk.Button(sort_button_frame, text="猬?涓婄Щ", 
                                    command=self.move_file_up, width=10)
        self.btn_file_up.pack(pady=2)
        
        self.btn_file_down = tk.Button(sort_button_frame, text="猬?涓嬬Щ", 
                                      command=self.move_file_down, width=10)
        self.btn_file_down.pack(pady=2)
        
        # 淇濆瓨鎺掑簭鎸夐挳
        self.btn_save_sort = tk.Button(sort_button_frame, text="馃捑 淇濆瓨鎺掑簭", 
                                      command=self.save_sort_config, width=10)
        self.btn_save_sort.pack(pady=(20, 0))
        
        # 缁戝畾鍙屽嚮浜嬩欢
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        
        # 缁戝畾閫夋嫨浜嬩欢锛岀敤浜庡惎鐢?绂佺敤鎺掑簭鎸夐挳
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_selection)
        
    def create_log_and_debug_area(self, parent):
        """鍒涘缓鏃ュ織鍜岃皟璇曞伐鍏峰尯鍩?""
        # 涓绘鏋?       log_debug_frame = ttk.Frame(parent)
        log_debug_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_debug_frame.columnconfigure(0, weight=3)  # 鏃ュ織鍖哄煙锛堝崰3/4锛?
        log_debug_frame.columnconfigure(1, weight=1)  # 璋冭瘯宸ュ叿鍖哄煙锛堝崰1/4锛?
        log_debug_frame.rowconfigure(0, weight=1)
        
        # 宸︿晶锛氭棩蹇楀尯鍩?
        self.create_log_area(log_debug_frame)
        
        # 鍙充晶锛氳皟璇曞伐鍏峰尯鍩?
        self.create_debug_tools_area(log_debug_frame)
        
    def create_log_area(self, parent):
        """鍒涘缓鏃ュ織鍖哄煙"""
        # 鏃ュ織妗嗘灦
        log_frame = ttk.LabelFrame(parent, text="馃摑 鎿嶄綔鏃ュ織", padding="10")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 鏃ュ織鏂囨湰妗?- 浣跨敤ScrolledText鑷甫婊氬姩鏉?
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=("Consolas", 9), height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 閰嶇疆鏃ュ織杈撳嚭锛堢洿鎺ヨ緭鍑哄埌鎺у埗鍙板拰鏂囦欢?        # 閲嶅啓logger鐨刲og鏂规硶锛屽悓鏃惰緭鍑哄埌鏂囨湰?        original_log = self.logger.log
        def new_log(message, level="INFO"):
            original_log(message, level)
            # 鍚屾椂杈撳嚭鍒版枃鏈
            self.log_text.insert(tk.END, f"[{level}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.update()
        self.logger.log = new_log
        
    def create_debug_tools_area(self, parent):
        """鍒涘缓璋冭瘯宸ュ叿鍖哄煙"""
        # 璋冭瘯宸ュ叿妗嗘灦
        debug_frame = ttk.LabelFrame(parent, text="馃敡 璋冭瘯宸ュ叿", padding="10")
        debug_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        debug_frame.columnconfigure(0, weight=1)
        
        # 璋冭瘯鎸夐挳
        debug_buttons = [
            ("馃寪 娴嬭瘯缃戠粶杩炴帴", self.test_network_connection),
            ("馃攳 妫€鏌it鐘舵€?, self.check_git_status),
            ("馃搳 鏌ョ湅Git鏃ュ織", self.show_git_log),
            ("馃攧 鎵嬪姩鎺ㄩ€丟it", self.manual_git_push),
            ("馃敡 Git杩炴帴璇婃柇", self.diagnose_git_connection),
            ("馃攽 鍒囨崲鍒癝SH", self.switch_to_ssh),
            ("馃Ч 娓呴櫎npm缂撳瓨", self.clear_npm_cache),
            ("鈿欙笍 妫€鏌ラ厤缃?, self.check_config),
        ]
        
        for i, (text, command) in enumerate(debug_buttons):
            btn = tk.Button(
                debug_frame,
                text=text,
                command=command,
                bg="SystemButtonFace",
                fg="black",
                width=20,
                relief="raised",
                bd=2
            )
            btn.grid(row=i, column=0, pady=5, sticky="ew")
        
    def create_control_area(self, parent):
        """鍒涘缓鎺у埗鎸夐挳鍖哄煙"""
        # 鎺у埗妗嗘灦
        control_frame = ttk.LabelFrame(parent, text="鏂囨。绠＄悊鎺у埗", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 绗竴琛岋細涓昏鍔熻兘鎸夐挳
        top_frame = ttk.Frame(control_frame)
        top_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 妫€娴嬭娉曟寜?        self.btn_check_mdx = tk.Button(top_frame, text="馃攳 妫€娴婱DX璇硶", 
                                      command=self.check_mdx_syntax, width=20,
                                      bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_check_mdx.pack(side=tk.LEFT, padx=5)
        
        # 鍒嗛殧?        ttk.Separator(control_frame, orient='horizontal').grid(row=1, column=0, columnspan=4, 
                                                              sticky=(tk.W, tk.E), pady=10)
        
        # 绗簩琛岋細閮ㄧ讲娴佺▼鎺у埗鎸夐挳
        deploy_control_frame = ttk.Frame(control_frame)
        deploy_control_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 寮€濮嬮儴缃叉祦绋嬫寜?        self.btn_start_deploy = tk.Button(deploy_control_frame, text="?寮€濮嬮儴缃叉祦?, 
                                         command=self.start_deployment_flow, width=20,
                                         bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_start_deploy.pack(side=tk.LEFT, padx=5)
        
        # 缁撴潫娴佺▼鎸夐挳
        self.btn_end_deploy = tk.Button(deploy_control_frame, text="?缁撴潫娴佺▼", 
                                       command=self.end_deployment_flow, width=20, state="disabled",
                                       bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_end_deploy.pack(side=tk.LEFT, padx=5)
        
        # 楠岃瘉閮ㄧ讲鎸夐挳锛堢嫭绔嬶紝涓€鐩村彲鐢級
        self.btn_verify_deploy = tk.Button(deploy_control_frame, text="馃寪 楠岃瘉閮ㄧ讲", 
                                          command=self.verify_deployment, width=20,
                                          bg="SystemButtonFace", fg="black", relief="raised", bd=2)
        self.btn_verify_deploy.pack(side=tk.LEFT, padx=5)
        
        # 鍒嗛殧?        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, columnspan=4, 
                                                              sticky=(tk.W, tk.E), pady=10)
        
        # 绗笁琛岋細閮ㄧ讲姝ラ鎸夐挳锛堥粯璁ょ鐢級
        deploy_steps_frame = ttk.Frame(control_frame)
        deploy_steps_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # 閮ㄧ讲娴佺▼鏍囩
        ttk.Label(deploy_steps_frame, text="閮ㄧ讲姝ラ:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # 閮ㄧ讲姝ラ鎸夐挳锛堟寜椤哄簭鎵ц?        self.deployment_buttons = [
            ("鍒锋柊鏂囦欢缁撴瀯", self.refresh_folder_structure, "鍒锋柊骞舵樉绀烘枃浠跺す缁撴瀯"),
            ("鐢熸垚渚ц竟?, self.generate_sidebar, "鐢熸垚Docusaurus渚ц竟?),
            ("鏈湴鏋勫缓娴嬭瘯", self.local_build_test, "鎵цnpm run build娴嬭瘯鏋勫缓"),
            ("鏈湴棰勮", self.local_preview, "鍚姩鏈湴寮€鍙戞湇鍔″櫒棰勮"),
            ("鑷姩閮ㄧ讲", self.auto_deploy, "鎵цGit鎺ㄩ€佸拰Cloudflare閮ㄧ讲"),
        ]
        
        # 鍒涘缓閮ㄧ讲姝ラ鎸夐挳锛堥粯璁ょ鐢級
        for i, (text, command, tooltip) in enumerate(self.deployment_buttons):
            btn = tk.Button(deploy_steps_frame, text=text, command=command, width=15, state="disabled",
                          bg="SystemButtonFace", fg="black", relief="raised", bd=2)
            btn.pack(side=tk.LEFT, padx=5)
            
            # 瀛樺偍鎸夐挳寮曠敤浠ヤ究鏇存柊鐘?            setattr(self, f"btn_{text.replace(' ', '_')}", btn)
            
            # 娣诲姞宸ュ叿鎻愮ず
            self.create_tooltip(btn, tooltip)
        
        # 閮ㄧ讲娴佺▼鐘舵€佸彉?        self.deployment_started = False
        self.deployment_step = 0
    
    def create_tooltip(self, widget, text):
        """鍒涘缓宸ュ叿鎻愮ず"""
        def enter(event):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(self.tooltip, text=text, background="#ffffe0", 
                             relief="solid", borderwidth=1, padding=5)
            label.pack()
        
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                delattr(self, 'tooltip')
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def refresh_folder_structure(self):
        """鍒锋柊鏂囦欢澶圭粨鏋勬樉绀?""
        self.logger.info("寮€濮嬪埛鏂版枃浠跺す缁撴瀯...")
        
        # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€佷负杩愯?        if self.deployment_started:
            self.update_button_state("鍒锋柊鏂囦欢缁撴瀯", "running")
        
        # 娓呯┖?        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 鎵弿docs鏂囦欢澶圭粨?        self.scan_and_display_structure()
        
        # 璁板綍鏃ュ織
        self.logger.info("鏂囦欢澶圭粨鏋勫凡鍒锋柊")
        
        # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?        if self.deployment_started:
            self.update_button_state("鍒锋柊鏂囦欢缁撴瀯", "success")
        
    def scan_and_display_structure(self):
        """鎵弿骞舵樉绀烘枃浠跺す缁撴瀯"""
        try:
            # 璇诲彇鎺掑簭閰嶇疆鏂囦欢
            import json
            sort_config_path = Path(__file__).parent / "sort_config.json"
            sort_config = {"folders": [], "files": {}}
            
            if sort_config_path.exists():
                with open(sort_config_path, 'r', encoding='utf-8') as f:
                    sort_config = json.load(f)
            
            # 鑾峰彇鎵€鏈変竴绾ф枃浠跺す
            all_folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    all_folders.append(item.name)
            
            # 鎸夌収鎺掑簭閰嶇疆鏂囦欢鐨勯『搴忔樉绀烘枃浠跺す
            display_folders = []
            
            # 鍏堟坊鍔犻厤缃枃浠朵腑鎸囧畾鐨勬枃浠跺す
            for folder_name in sort_config.get("folders", []):
                if folder_name in all_folders:
                    display_folders.append(folder_name)
            
            # 鍐嶆坊鍔犲叾浠栨枃浠跺す锛堟寜瀛楁瘝椤哄簭锛?
            for folder_name in sorted(all_folders):
                if folder_name not in display_folders:
                    display_folders.append(folder_name)
            
            total_files = 0
            total_folders = len(display_folders)
            
            # 娣诲姞姣忎釜鏂囦欢澶瑰埌Treeview
            for folder_name in display_folders:
                folder_path = self.docs_folder / folder_name
                
                # 鑾峰彇鏂囦欢澶瑰唴鐨凪DX鏂囦欢
                mdx_files = []
                for file in folder_path.glob("*.mdx"):
                    mdx_files.append(file.name)
                
                # 鎸夌収閰嶇疆鏂囦欢涓殑鏂囦欢椤哄簭
                sorted_files = []
                config_files = sort_config.get("files", {}).get(folder_name, [])
                
                # 鍏堟坊鍔犻厤缃枃浠朵腑鎸囧畾鐨勬枃浠?
                for config_file in config_files:
                    config_file_with_ext = f"{config_file}.mdx"
                    if config_file_with_ext in mdx_files:
                        sorted_files.append(config_file_with_ext)
                
                # 鍐嶆坊鍔犲叾浠栨枃浠讹紙鎸夊瓧姣嶉『搴忥級
                for file_name in sorted(mdx_files):
                    if file_name not in sorted_files:
                        sorted_files.append(file_name)
                
                # 娣诲姞鏂囦欢澶硅妭鐐?- 榛樿灞曞紑
                folder_id = self.tree.insert("", "end", text=f"馃搧 {folder_name}", 
                                           values=("鏂囦欢澶?,),
                                           open=True)  # 榛樿灞曞紑
                
                # 娣诲姞鏂囦欢鑺傜偣
                for file_name in sorted_files:
                    # 娓呯悊鏂囦欢鏄剧ず鍚嶇О锛堢Щ闄?mdx鎵╁睍鍚嶏級
                    file_display_name = self.clean_name(file_name)
                    self.tree.insert(folder_id, "end", text=f"馃搫 {file_display_name}", 
                                   values=("MDX鏂囦欢",))
                    total_files += 1
                
                # 濡傛灉娌℃湁鏂囦欢锛屾樉绀烘彁绀?
                if not sorted_files:
                    self.tree.insert(folder_id, "end", text="(绌烘枃浠跺す)", 
                                   values=("鎻愮ず",))
            
            # 娣诲姞鏍硅妭鐐癸紙涓嶆樉绀虹粺璁′俊鎭級
            self.tree.insert("", 0, text="馃搨 docs鏂囦欢澶?, values=("鏍圭洰褰?,), open=True)
            
        except Exception as e:
            self.logger.error(f"鎵弿鏂囦欢澶圭粨鏋勫け璐? {str(e)}")
    
    def sort_by_number_prefix(self, items: List[str]) -> List[str]:
        """鎸夋暟瀛楀墠缂€鎺掑簭椤圭洰"""
        def extract_sort_key(name: str) -> Tuple[float, str]:
            """鎻愬彇鎺掑簭閿?""
            # 鍖归厤鏁板瓧鍓嶇紑锛堟敮鎸佹暣鏁板拰灏忔暟?            match = re.match(r'^([0-9]+(?:\.[0-9]+)?)-(.+)$', name)
            if match:
                num = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
                return (num, match.group(2))
            
            # 鏃犲墠缂€锛屾寜鍘熷悕绉版帓?            return (float('inf'), name)
        
        return sorted(items, key=extract_sort_key)
    
    def clean_name(self, name: str) -> str:
        """
        娓呯悊鍚嶇О - 鍙Щ闄?mdx鎵╁睍鍚?
        
        Args:
            name: 鍘熷鍚嶇О锛堝"涓荤▼搴忓畨瑁呰鏄?mdx"锛?
        
        Returns:
            娓呯悊鍚庣殑鍚嶇О锛堝"涓荤▼搴忓畨瑁呰鏄?锛?
        """
        # 鍙Щ闄?mdx鎵╁睍鍚?
        if name.endswith('.mdx'):
            return name[:-4]
        return name
    
    def clean_name_for_url(self, name: str) -> str:
        """Clean name for URL"""
        # 绉婚櫎.mdx鎵╁睍鍚?
        if name.endswith('.mdx'):
            name = name[:-4]
        
        # 绉婚櫎鏁板瓧鍓嶇紑锛堝"1-"鎴?1 -"锛?
        import re
        # 鍖归厤鏁板瓧寮€澶达紝鍚庨潰鍙兘璺熺┖鏍煎拰杩炲瓧绗?
        name = re.sub(r'^\d+\s*\-*\s*', '', name)
        
        # 涓枃杞嫳?鎷奸煶鏄犲皠?        chinese_to_english = {
            # 鏂囦欢澶瑰悕绉版槧?            '绋嬪簭瀹夎璇存槑': 'program-installation-guide',
            '浜戞洿鏂版湇鍔℃敞鍐岃?: 'cloud-update-service-registration',
            '琛ヤ竵鏇存柊鏃ュ織': 'patch-update-log',
            
            # 鏂囦欢鍚嶇О鏄犲皠
            '涓荤▼搴忓畨瑁呰?: 'main-program-installation',
            '浜戞洿鏂版湇鍔℃敞鍐岃?: 'cloud-update-service-registration',
            '娉ㄥ唽瑙勫垯鐗规畩璇存槑': 'registration-rules-special',
            'NEW-26040101': 'new-26040101',
            'NEW-26040902': 'new-26040902',
        }
        
        # 濡傛灉鍚嶇О鍦ㄦ槧灏勮〃涓紝浣跨敤鑻辨枃鍚嶇О
        if name in chinese_to_english:
            return chinese_to_english[name]
        
        # 鍚﹀垯锛屽皢涓枃杞崲涓烘嫾闊筹紙绠€鍗曞疄鐜帮級
        # 杩欓噷浣跨敤绠€鍗曠殑鏇挎崲锛屽疄闄呭彲浠ヤ娇鐢╬ypinyin?        pinyin_map = {
            '绋嬪簭': 'program',
            '瀹夎': 'installation',
            '璇存槑': 'guide',
            '?: 'cloud',
            '鏇存柊': 'update',
            '鏈嶅姟': 'service',
            '娉ㄥ唽': 'registration',
            '瑙勫垯': 'rules',
            '鐗规畩': 'special',
            '琛ヤ竵': 'patch',
            '鏃ュ織': 'log',
            '?: 'main',
        }
        
        # 绠€鍗曠殑涓枃杞嫳?        result = name
        for chinese, english in pinyin_map.items():
            result = result.replace(chinese, english)
        
        # 濡傛灉杩樻湁涓枃瀛楃锛屼娇鐢ㄩ€氱敤鏍煎紡
        if any('\u4e00' <= char <= '\u9fff' for char in result):
            # 鐢熸垚瀹夊叏鐨勮嫳鏂囧悕绉帮細绉婚櫎鐗规畩瀛楃锛岀敤杩炲瓧绗﹁繛?            import unicodedata
            result = unicodedata.normalize('NFKD', result)
            result = result.encode('ascii', 'ignore').decode('ascii')
            result = re.sub(r'[^\w\s-]', '', result).strip().lower()
            result = re.sub(r'[-\s]+', '-', result)
        
        return result
    
    def should_reverse_order(self, folder_name: str) -> bool:
        """鍒ゆ柇鏂囦欢澶规槸鍚﹂渶瑕佸€掑簭鎺掑簭"""
        clean_name = self.clean_name(folder_name)
        for pattern in self.reverse_order_folders:
            if pattern in clean_name:
                return True
        return False
    
    def sort_files_by_rule(self, files: List[str], reverse: bool = False) -> List[str]:
        """鎸夎鍒欐帓搴忔枃?""
        def extract_number(filename: str) -> float:
            """鎻愬彇鏂囦欢鏁板瓧鍓嶇紑"""
            match = re.match(r'^([0-9]+(?:\.[0-9]+)?)-', filename)
            if match:
                num = match.group(1)
                return float(num) if '.' in num else int(num)
            return float('inf')  # 鏃犳暟瀛楀墠缂€鐨勬帓鏈€?        
        return sorted(files, key=extract_number, reverse=reverse)
    
    def on_tree_double_click(self, event):
        """鏍戣妭鐐瑰弻鍑讳簨?""
        item = self.tree.selection()[0]
        item_text = self.tree.item(item, "text")
        
        # 鍒囨崲灞曞紑/鎶樺彔鐘?        if self.tree.item(item, "open"):
            self.tree.item(item, open=False)
        else:
            self.tree.item(item, open=True)
    
    def check_mdx_syntax(self):
        """妫€娴婱DX璇硶"""
        self.logger.info("寮€濮嬫娴婱DX璇硶...")
        
        # 鍦ㄦ柊绾跨▼涓墽琛屾?        thread = threading.Thread(target=self._check_mdx_syntax_thread)
        thread.daemon = True
        thread.start()
    
    def _check_mdx_syntax_thread(self):
        """妫€娴婱DX璇硶绾跨▼"""
        try:
            total_files = 0
            error_files = []
            
            # 閬嶅巻鎵€鏈塎DX鏂囦欢
            for mdx_file in self.docs_folder.rglob("*.mdx"):
                total_files += 1
                relative_path = mdx_file.relative_to(self.docs_folder)
                
                try:
                    # 浣跨敤check_single_file鏂规硶妫€娴嬪崟涓枃?                    issues = self.mdx_checker.check_single_file(mdx_file)
                    
                    if issues:
                        error_files.append(str(relative_path))
                        for issue in issues:
                            self.logger.error(f"  {relative_path}: 琛寋issue['line']} - {issue['type']}: {issue['message']}")
                    else:
                        self.logger.info(f"  ?{relative_path}")
                        
                except Exception as e:
                    error_files.append(str(relative_path))
                    self.logger.error(f"  {relative_path}: 妫€娴嬪け?- {str(e)}")
            
            # 鏄剧ず缁熻淇℃伅
            self.logger.info("=" * 60)
            self.logger.info(f"MDX璇硶妫€娴嬪畬?")
            self.logger.info(f"  鎬绘枃浠舵暟: {total_files}")
            self.logger.info(f"  閿欒鏂囦欢: {len(error_files)}")
            
            if error_files:
                self.logger.warning("閿欒鏂囦欢鍒楄〃:")
                for file in error_files:
                    self.logger.warning(f"  ?{file}")
                self.logger.warning(f"妫€娴嬪畬鎴愶細鍙戠幇{len(error_files)}涓枃浠舵湁璇硶閿欒")
            else:
                self.logger.success("鎵€鏈塎DX鏂囦欢璇硶姝ｇ‘?)
                
        except Exception as e:
            self.logger.error(f"妫€娴婱DX璇硶澶辫触: {str(e)}")
    
    def generate_sidebar(self):
        """鐢熸垚渚ц竟?""
        self.logger.info("寮€濮嬬敓鎴愪晶杈规爮...")
        
        # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€佷负杩愯?        if self.deployment_started:
            self.update_button_state("鐢熸垚渚ц竟?, "running")
        
        # 鍦ㄦ柊绾跨▼涓墽琛岀敓?        thread = threading.Thread(target=self._generate_sidebar_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_sidebar_thread(self):
        """鐢熸垚渚ц竟鏍忕嚎?""
        try:
            # 鑾峰彇鏂囦欢澶圭粨鏋勫苟鐢熸垚渚ц竟鏍忓唴?            sidebar_content = self.generate_sidebar_content()
            
            # 鍐欏叆sidebars.js鏂囦欢
            with open(self.sidebars_path, 'w', encoding='utf-8') as f:
                f.write(sidebar_content)
            
            self.logger.success("渚ц竟鏍忕敓鎴愭垚鍔燂紒")
            self.logger.info(f"鏂囦欢宸蹭繚? {self.sidebars_path}")
            
            # 鏄剧ず鐢熸垚鐨勪晶杈规爮鍐呭
            self.logger.info("鐢熸垚鐨勪晶杈规爮缁撴瀯:")
            self.logger.info("-" * 40)
            for line in sidebar_content.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
            
            self.logger.success("渚ц竟鏍忓凡鎴愬姛鐢熸垚骞朵繚瀛橈紒")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?            if self.deployment_started:
                self.update_button_state("鐢熸垚渚ц竟?, "success")
            
        except Exception as e:
            self.logger.error(f"鐢熸垚渚ц竟鏍忓け? {str(e)}")
            self.logger.error(f"鐢熸垚渚ц竟鏍忓け? {str(e)}")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?            if self.deployment_started:
                self.update_button_state("鐢熸垚渚ц竟?, "error")
    
    def generate_sidebar_content(self) -> str:
        """鐢熸垚渚ц竟鏍忓唴瀹?- 鎸夌収鎺掑簭閰嶇疆鏂囦欢鐢熸垚"""
        import json
        
        lines = []
        lines.append("const sidebars = {")
        lines.append("  tutorialSidebar: [")
        
        # 璇诲彇鎺掑簭閰嶇疆鏂囦欢
        sort_config_path = Path(__file__).parent / "sort_config.json"
        if sort_config_path.exists():
            with open(sort_config_path, 'r', encoding='utf-8') as f:
                sort_config = json.load(f)
            
            # 鎸夌収閰嶇疆鐨勬枃浠跺す椤哄簭鐢熸垚
            for folder_name in sort_config.get("folders", []):
                folder_path = self.docs_folder / folder_name
                
                if not folder_path.exists():
                    continue
                
                # 鑾峰彇鏂囦欢澶逛腑鐨勬枃浠?
                files = []
                for file_item in folder_path.iterdir():
                    if file_item.is_file() and file_item.name.endswith('.mdx'):
                        files.append(file_item.name)
                
                # 鎸夌収閰嶇疆鏂囦欢涓殑鏂囦欢椤哄簭
                sorted_files = []
                config_files = sort_config.get("files", {}).get(folder_name, [])
                
                # 鍏堟坊鍔犻厤缃枃浠朵腑鎸囧畾鐨勬枃浠?
                for config_file in config_files:
                    config_file_with_ext = f"{config_file}.mdx"
                    if config_file_with_ext in files:
                        sorted_files.append(config_file_with_ext)
                
                # 鍐嶆坊鍔犲叾浠栨枃浠讹紙鎸夊瓧姣嶉『搴忥級
                for file_name in sorted(files):
                    if file_name not in sorted_files:
                        sorted_files.append(file_name)
                
                if sorted_files:
                    lines.append("    {")
                    lines.append(f"      type: 'category',")
                    lines.append(f"      label: '{folder_name}',")
                    lines.append(f"      items: [")
                    
                    for file_name in sorted_files:
                        # 鐢熸垚鏂囨。ID锛圖ocusaurus鏍煎紡锛氭枃浠跺す鍚?鏂囦欢鍚嶏級
                        # 鏃犻渶娓呯悊鏁板瓧鍓嶇紑锛屽洜涓烘枃浠跺す鍜屾枃浠堕兘娌℃湁鏁板瓧鍓嶇紑浜?
                        clean_file_name = self.clean_name(file_name)
                        doc_id = f"{folder_name}/{clean_file_name}"
                        lines.append(f"        '{doc_id}',")
                    
                    lines.append(f"      ],")
                    lines.append(f"      collapsed: true,")
                    lines.append("    },")
        else:
            # 濡傛灉娌℃湁鎺掑簭閰嶇疆鏂囦欢锛屾寜瀛楁瘝椤哄簭鐢熸垚
            folders = []
            for item in self.docs_folder.iterdir():
                if item.is_dir():
                    folders.append(item.name)
            
            for folder_name in sorted(folders):
                folder_path = self.docs_folder / folder_name
                
                # 鑾峰彇鏂囦欢澶逛腑鐨勬枃浠?
                files = []
                for file_item in folder_path.iterdir():
                    if file_item.is_file() and file_item.name.endswith('.mdx'):
                        files.append(file_item.name)
                
                if files:
                    lines.append("    {")
                    lines.append(f"      type: 'category',")
                    lines.append(f"      label: '{folder_name}',")
                    lines.append(f"      items: [")
                    
                    for file_name in sorted(files):
                        clean_file_name = self.clean_name(file_name)
                        doc_id = f"{folder_name}/{clean_file_name}"
                        lines.append(f"        '{doc_id}',")
                    
                    lines.append(f"      ],")
                    lines.append(f"      collapsed: true,")
                    lines.append("    },")
        
        lines.append("  ],")
        lines.append("};")
        lines.append("")
        lines.append("export default sidebars;")
        
        return "\n".join(lines)
    
    def on_tree_selection(self, event):
        """澶勭悊Treeview閫夋嫨浜嬩欢锛屽惎鐢?绂佺敤鎺掑簭鎸夐挳"""
        selection = self.tree.selection()
        if not selection:
            # 娌℃湁閫夋嫨锛岀鐢ㄦ墍鏈夋帓搴忔寜閽?
            self.btn_folder_up.config(state="disabled")
            self.btn_folder_down.config(state="disabled")
            self.btn_file_up.config(state="disabled")
            self.btn_file_down.config(state="disabled")
            return
        
        item_id = selection[0]
        item = self.tree.item(item_id)
        
        # 妫€鏌ユ槸鏂囦欢澶硅繕鏄枃浠?
        parent_id = self.tree.parent(item_id)
        
        if parent_id == "":
            # 杩欐槸鏂囦欢澶?
            self.btn_folder_up.config(state="normal")
            self.btn_folder_down.config(state="normal")
            self.btn_file_up.config(state="disabled")
            self.btn_file_down.config(state="disabled")
        else:
            # 杩欐槸鏂囦欢
            self.btn_folder_up.config(state="disabled")
            self.btn_folder_down.config(state="disabled")
            self.btn_file_up.config(state="normal")
            self.btn_file_down.config(state="normal")
    
    def move_folder_up(self):
        """涓婄Щ閫変腑鐨勬枃浠跺す"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        parent_id = self.tree.parent(item_id)
        
        # 鍙湁椤剁骇鏂囦欢澶瑰彲浠ョЩ鍔?
        if parent_id != "":
            return
        
        # 鑾峰彇鎵€鏈夊悓绾ф枃浠跺す
        siblings = list(self.tree.get_children(parent_id))
        index = siblings.index(item_id)
        
        if index > 0:
            # 涓婄Щ
            self.tree.move(item_id, parent_id, index - 1)
            self.logger.info(f"鏂囦欢澶逛笂绉? {self.tree.item(item_id)['text']}")
    
    def move_folder_down(self):
        """涓嬬Щ閫変腑鐨勬枃浠跺す"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        parent_id = self.tree.parent(item_id)
        
        # 鍙湁椤剁骇鏂囦欢澶瑰彲浠ョЩ鍔?
        if parent_id != "":
            return
        
        # 鑾峰彇鎵€鏈夊悓绾ф枃浠跺す
        siblings = list(self.tree.get_children(parent_id))
        index = siblings.index(item_id)
        
        if index < len(siblings) - 1:
            # 涓嬬Щ
            self.tree.move(item_id, parent_id, index + 1)
            self.logger.info(f"鏂囦欢澶逛笅绉? {self.tree.item(item_id)['text']}")
    
    def move_file_up(self):
        """涓婄Щ閫変腑鐨勬枃浠?""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        parent_id = self.tree.parent(item_id)
        
        # 鍙湁鏂囦欢鍙互绉诲姩锛堟湁鐖剁骇锛?
        if parent_id == "":
            return
        
        # 鑾峰彇鎵€鏈夊悓绾ф枃浠?
        siblings = list(self.tree.get_children(parent_id))
        index = siblings.index(item_id)
        
        if index > 0:
            # 涓婄Щ
            self.tree.move(item_id, parent_id, index - 1)
            self.logger.info(f"鏂囦欢涓婄Щ: {self.tree.item(item_id)['text']}")
    
    def move_file_down(self):
        """涓嬬Щ閫変腑鐨勬枃浠?""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        parent_id = self.tree.parent(item_id)
        
        # 鍙湁鏂囦欢鍙互绉诲姩锛堟湁鐖剁骇锛?
        if parent_id == "":
            return
        
        # 鑾峰彇鎵€鏈夊悓绾ф枃浠?
        siblings = list(self.tree.get_children(parent_id))
        index = siblings.index(item_id)
        
        if index < len(siblings) - 1:
            # 涓嬬Щ
            self.tree.move(item_id, parent_id, index + 1)
            self.logger.info(f"鏂囦欢涓嬬Щ: {self.tree.item(item_id)['text']}")
    
    def save_sort_config(self):
        """淇濆瓨鎺掑簭閰嶇疆鍒版枃浠?""
        try:
            import json
            
            # 浠嶵reeview涓彁鍙栨帓搴忎俊鎭?
            sort_config = {
                "folders": [],
                "files": {}
            }
            
            # 鑾峰彇鎵€鏈夐《绾ф枃浠跺す锛堟寜鏄剧ず椤哄簭锛?
            folder_items = self.tree.get_children("")
            for folder_id in folder_items:
                folder_name = self.tree.item(folder_id)["text"]
                sort_config["folders"].append(folder_name)
                
                # 鑾峰彇璇ユ枃浠跺す涓嬬殑鏂囦欢锛堟寜鏄剧ず椤哄簭锛?
                file_items = self.tree.get_children(folder_id)
                file_names = []
                for file_id in file_items:
                    file_full_name = self.tree.item(file_id)["text"]
                    # 绉婚櫎.mdx鎵╁睍鍚?
                    if file_full_name.endswith(".mdx"):
                        file_name = file_full_name[:-4]
                    else:
                        file_name = file_full_name
                    file_names.append(file_name)
                
                sort_config["files"][folder_name] = file_names
            
            # 淇濆瓨鍒版枃浠?
            config_path = Path(__file__).parent / "sort_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(sort_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info("鉁?鎺掑簭閰嶇疆宸蹭繚瀛?)
            self.logger.info(f"馃搧 鏂囦欢澶归『搴? {', '.join(sort_config['folders'])}")
            
        except Exception as e:
            self.logger.error(f"淇濆瓨鎺掑簭閰嶇疆澶辫触: {str(e)}")
    
    def open_docs_folder(self):
        """鎵撳紑docs鏂囦欢?""
        try:
            os.startfile(str(self.docs_folder))
            self.logger.info(f"宸叉墦寮€鏂囦欢? {self.docs_folder}")
        except Exception as e:
            self.logger.error(f"鎵撳紑鏂囦欢澶瑰け? {str(e)}")
    
    def local_build_test(self):
        """鏈湴鏋勫缓娴嬭瘯"""
        self.logger.info("寮€濮嬫湰鍦版瀯寤烘祴?..")
        
        # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€佷负杩愯?        if self.deployment_started:
            self.update_button_state("鏈湴鏋勫缓娴嬭瘯", "running")
        
        # 鍦ㄦ柊绾跨▼涓墽琛屾瀯?        thread = threading.Thread(target=self._local_build_test_thread)
        thread.daemon = True
        thread.start()
    
    def _local_build_test_thread(self):
        """鏈湴鏋勫缓娴嬭瘯绾跨▼"""
        try:
            success, output = self.deployment_manager.local_build_test()
            if success:
                self.logger.success("鏈湴鏋勫缓娴嬭瘯鎴愬姛?)
                self.logger.info("鏈湴鏋勫缓娴嬭瘯鎴愬姛?)
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?                if self.deployment_started:
                    self.update_button_state("鏈湴鏋勫缓娴嬭瘯", "success")
            else:
                self.logger.error("鏈湴鏋勫缓娴嬭瘯澶辫触")
                self.logger.error("鏈湴鏋勫缓娴嬭瘯澶辫触锛岃鏌ョ湅鏃ュ織")
                # 杈撳嚭璇︾粏閿欒淇℃伅
                self.logger.error("璇︾粏閿欒淇℃伅:")
                for line in output.split('\n'):
                    if line.strip():
                        self.logger.error(f"  {line}")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?                if self.deployment_started:
                    self.update_button_state("鏈湴鏋勫缓娴嬭瘯", "error")
        except Exception as e:
            self.logger.error(f"鏈湴鏋勫缓娴嬭瘯寮傚父: {str(e)}")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?            if self.deployment_started:
                self.update_button_state("鏈湴鏋勫缓娴嬭瘯", "error")
    
    def local_preview(self):
        """鏈湴棰勮"""
        self.logger.info("寮€濮嬫湰鍦伴?..")
        
        # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€佷负杩愯?        if self.deployment_started:
            self.update_button_state("鏈湴棰勮", "running")
        
        # 鍦ㄦ柊绾跨▼涓墽琛岄?        thread = threading.Thread(target=self._local_preview_thread)
        thread.daemon = True
        thread.start()
    
    def _local_preview_thread(self):
        """鏈湴棰勮绾跨▼"""
        try:
            success, output = self.deployment_manager.local_preview()
            if success:
                self.logger.success("鏈湴棰勮鏈嶅姟鍣ㄥ凡鍚姩?)
                self.logger.info("鏈湴棰勮鏈嶅姟鍣ㄥ凡鍚姩锛岃鍦ㄦ祻瑙堝櫒涓煡?)
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?                if self.deployment_started:
                    self.update_button_state("鏈湴棰勮", "success")
                
                # 寤惰繜3绉掑悗鑷姩鎵撳紑娴忚?                self.logger.info("鏈嶅姟鍣ㄥ凡鍚姩?绉掑悗鑷姩鎵撳紑娴忚?..")
                self.root.after(3000, self.open_local_preview)
            else:
                self.logger.error("鍚姩鏈湴棰勮澶辫触")
                self.logger.error("鍚姩鏈湴棰勮澶辫触锛岃鏌ョ湅鏃ュ織")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?                if self.deployment_started:
                    self.update_button_state("鏈湴棰勮", "error")
        except Exception as e:
            self.logger.error(f"鍚姩鏈湴棰勮寮傚父: {str(e)}")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?            if self.deployment_started:
                self.update_button_state("鏈湴棰勮", "error")
    
    def open_local_preview(self):
        """鑷姩鎵撳紑鏈湴棰勮椤甸潰"""
        try:
            import webbrowser
            import time
            
            # 绛夊緟鏈嶅姟鍣ㄥ畬鍏ㄥ惎鍔紙澧炲姞绛夊緟鏃堕棿?            self.logger.info("绛夊緟鏈嶅姟鍣ㄥ畬鍏ㄥ惎?..")
            time.sleep(5)
            
            # 娴嬭瘯鏈嶅姟鍣ㄦ槸鍚︾湡鐨勫湪杩愯
            try:
                import urllib.request
                response = urllib.request.urlopen("http://localhost:3000", timeout=10)
                status_code = response.getcode()
                self.logger.info(f"鏈湴鏈嶅姟鍣ㄧ姸鎬佺爜: {status_code}")
            except Exception as e:
                self.logger.warning(f"鏈嶅姟鍣ㄥ彲鑳藉皻鏈畬鍏ㄥ惎? {str(e)}")
                self.logger.info("璇风◢绛夊嚑绉掑啀鍒锋柊椤甸潰")
            
            # 鎵撳紑缃戠珯棣栭〉
            url = "http://localhost:3000"
            
            # 鍚屾椂鏄剧ず鍙敤鐨勬枃妗ｉ摼鎺ワ紝鏂逛究鐢ㄦ埛蹇€熻?            self.logger.info("宸叉墦寮€缃戠珯棣栭〉锛屽彲鐢ㄦ枃妗ｉ摼?")
            
            # 浠庝晶杈规爮涓幏鍙栨墍鏈夋枃妗ｉ摼?            sidebars_path = self.project_path / "sidebars.js"
            if sidebars_path.exists():
                try:
                    with open(sidebars_path, 'r', encoding='utf-8') as f:
                        sidebar_content = f.read()
                    
                    # 鎻愬彇鎵€鏈夋枃妗D
                    import re
                    doc_ids = re.findall(r"'([^']+/[^']+)'", sidebar_content)
                    
                    if doc_ids:
                        for doc_id in doc_ids:
                            # 鏂囨。ID宸茬粡鏄嫳鏂囨枃浠跺す?涓枃鏂囦欢鍚嶆牸?                            # 渚嬪锛歅rogramInstallationInstructions/涓荤▼搴忓畨瑁呰?                            doc_url = f"http://localhost:3000/docs/{doc_id}"
                            self.logger.info(f"  ?{doc_id}: {doc_url}")
                        
                        # 鍚屾椂鑷姩鎵撳紑绗竴涓枃妗ｏ紙閬垮厤棣栭〉404?                        first_doc_id = doc_ids[0]
                        first_doc_url = f"http://localhost:3000/docs/{first_doc_id}"
                        self.logger.info(f"鍚屾椂鎵撳紑绗竴涓枃? {first_doc_url}")
                        webbrowser.open(first_doc_url)
                    else:
                        self.logger.info("  ?鏈壘鍒版枃妗ｉ摼?)
                        webbrowser.open(url)
                except Exception as e:
                    self.logger.info(f"  ?璇诲彇渚ц竟鏍忓け? {str(e)}")
                    webbrowser.open(url)
            else:
                self.logger.info("  ?渚ц竟鏍忔枃浠朵笉瀛樺湪")
                webbrowser.open(url)
            
            self.logger.success(f"宸茶嚜鍔ㄦ墦寮€娴忚鍣ㄨ? {url}")
            self.logger.info("濡傛灉鏄剧ず404锛岃:")
            self.logger.info("1. 娓呴櫎娴忚鍣ㄧ紦?)
            self.logger.info("2. 浣跨敤鏃犵棔妯″紡")
            self.logger.info("3. 绛夊緟鍑犵鍚庡埛鏂伴〉?)
            
        except Exception as e:
            self.logger.error(f"鑷姩鎵撳紑娴忚鍣ㄥけ? {str(e)}")
            self.logger.info("璇锋墜鍔ㄨ? http://localhost:3000")
    
    def auto_deploy(self):
        """鑷姩閮ㄧ讲"""
        self.logger.info("寮€濮嬭嚜鍔ㄩ儴?..")
        
        # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘舵€佷负杩愯?        if self.deployment_started:
            self.update_button_state("鑷姩閮ㄧ讲", "running")
        
        # 鍦ㄦ柊绾跨▼涓墽琛岄儴?        thread = threading.Thread(target=self._auto_deploy_thread)
        thread.daemon = True
        thread.start()
    
    def _auto_deploy_thread(self):
        """鑷姩閮ㄧ讲绾跨▼"""
        try:
            success, output = self.deployment_manager.auto_deploy()
            if success:
                self.logger.success("鑷姩閮ㄧ讲鎴愬姛?)
                self.logger.info("鑷姩閮ㄧ讲鎴愬姛?)
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?                if self.deployment_started:
                    self.update_button_state("鑷姩閮ㄧ讲", "success")
            else:
                self.logger.error("鑷姩閮ㄧ讲澶辫触")
                self.logger.error("鑷姩閮ㄧ讲澶辫触锛岃鏌ョ湅鏃ュ織")
                
                # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?                if self.deployment_started:
                    self.update_button_state("鑷姩閮ㄧ讲", "error")
        except Exception as e:
            self.logger.error(f"鑷姩閮ㄧ讲寮傚父: {str(e)}")
            
            # 濡傛灉鏄湪閮ㄧ讲娴佺▼涓紝鏇存柊鎸夐挳鐘?            if self.deployment_started:
                self.update_button_state("鑷姩閮ㄧ讲", "error")
    
    def verify_deployment(self):
        """楠岃瘉閮ㄧ讲锛堢嫭绔嬪姛鑳斤紝闅忔椂鍙敤?""
        self.logger.info("楠岃瘉閮ㄧ讲鐘?..")
        
        # 鍦ㄦ柊绾跨▼涓墽琛岄獙?        thread = threading.Thread(target=self._verify_deployment_thread)
        thread.daemon = True
        thread.start()
    
    def _verify_deployment_thread(self):
        """楠岃瘉閮ㄧ讲绾跨▼ - 绠€鍗曟墦寮€缃戦〉锛屼笉鍐欏叆鏃ュ織"""
        try:
            # 鐩存帴璋冪敤楠岃瘉閮ㄧ讲锛屽畠浼氳嚜鍔ㄦ墦寮€缃戦〉
            success, output = self.deployment_manager.verify_deployment()
            
            # 鍙湪鏃ュ織涓樉绀虹畝鍗曚俊?            self.logger.info(f"楠岃瘉閮ㄧ讲: {output}")
            
        except Exception as e:
            # 鍗充娇鍑洪敊涔熶笉鏄剧ず閿欒
            self.logger.info("楠岃瘉閮ㄧ讲: 璇锋墜鍔ㄨ?https://docs.toothmen.com")
    
    # ==================== 璋冭瘯宸ュ叿鏂规硶 ====================
    
    def test_network_connection(self):
        """娴嬭瘯缃戠粶杩炴帴"""
        self.logger.info("姝ｅ湪娴嬭瘯缃戠粶杩炴帴...")
        
        import subprocess
        import threading
        
        def _test_network():
            try:
                # 娴嬭瘯ping GitHub
                self.logger.info("娴嬭瘯ping github.com...")
                result = subprocess.run(
                    ["ping", "-n", "4", "github.com"],
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                )
                
                if result.returncode == 0:
                    self.logger.success("?Ping娴嬭瘯鎴愬姛")
                    # 鎻愬彇鍏抽敭淇℃伅
                    for line in result.stdout.split('\n'):
                        if "鏁版嵁?" in line or "Packets:" in line:
                            self.logger.info(f"缃戠粶鐘? {line.strip()}")
                        if "骞冲潎 =" in line or "Average =" in line:
                            self.logger.info(f"缃戠粶寤惰繜: {line.strip()}")
                else:
                    self.logger.error("?Ping娴嬭瘯澶辫触")
                    self.logger.error(f"閿欒淇℃伅: {result.stderr}")
                
                # 娴嬭瘯HTTPS璁块棶
                self.logger.info("娴嬭瘯HTTPS璁块棶...")
                import urllib.request
                try:
                    response = urllib.request.urlopen("https://github.com", timeout=10)
                    self.logger.success(f"?HTTPS璁块棶鎴愬姛 (鐘舵€佺爜: {response.status})")
                except Exception as e:
                    self.logger.error(f"?HTTPS璁块棶澶辫触: {str(e)}")
                    
            except Exception as e:
                self.logger.error(f"缃戠粶娴嬭瘯寮傚父: {str(e)}")
        
        # 鍦ㄦ柊绾跨▼涓墽琛岀綉缁滄祴?        thread = threading.Thread(target=_test_network)
        thread.daemon = True
        thread.start()
    
    def check_git_status(self):
        """妫€鏌it鐘?""
        self.logger.info("姝ｅ湪妫€鏌it鐘?..")
        
        import threading
        
        def _check_git():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["status", "--short"]
                )
                
                if success:
                    if output.strip():
                        self.logger.info("Git鐘?")
                        self.logger.info(output)
                    else:
                        self.logger.success("?宸ヤ綔鍖哄共鍑€锛屾病鏈夋湭鎻愪氦鐨勬洿?)
                else:
                    self.logger.error(f"?Git鐘舵€佹鏌ュけ? {output}")
                    
            except Exception as e:
                self.logger.error(f"Git鐘舵€佹鏌ュ紓? {str(e)}")
        
        thread = threading.Thread(target=_check_git)
        thread.daemon = True
        thread.start()
    
    def show_git_log(self):
        """鏌ョ湅Git鏃ュ織"""
        self.logger.info("姝ｅ湪鑾峰彇Git鎻愪氦鍘嗗彶...")
        
        import threading
        
        def _show_log():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-10"]
                )
                
                if success:
                    self.logger.info("鏈€?0娆℃彁?")
                    self.logger.info(output)
                else:
                    self.logger.error(f"?鑾峰彇Git鏃ュ織澶辫触: {output}")
                    
            except Exception as e:
                self.logger.error(f"鑾峰彇Git鏃ュ織寮傚父: {str(e)}")
        
        thread = threading.Thread(target=_show_log)
        thread.daemon = True
        thread.start()
    
    def manual_git_push(self):
        """鎵嬪姩鎺ㄩ€丟it"""
        self.logger.info("姝ｅ湪鎵嬪姩鎺ㄩ€丟it...")
        
        import threading
        
        def _manual_push():
            try:
                # 鍏堟坊鍔犳墍鏈夋洿?                success1, output1 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["add", "."]
                )
                
                if not success1:
                    self.logger.error(f"?Git娣诲姞澶辫触: {output1}")
                    return
                
                # 鎻愪氦
                import datetime
                commit_msg = f"鎵嬪姩鎺? {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                success2, output2 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["commit", "-m", commit_msg]
                )
                
                if not success2:
                    # 濡傛灉娌℃湁鏇存敼鍙彁?                    if "nothing to commit" in output2.lower():
                        self.logger.warning("鈿狅笍 娌℃湁闇€瑕佹彁浜ょ殑鏇存敼")
                    else:
                        self.logger.error(f"?Git鎻愪氦澶辫触: {output2}")
                        return
                
                # 鎺?                success3, output3 = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["push", "origin", "master"]
                )
                
                if success3:
                    self.logger.success("?鎵嬪姩鎺ㄩ€佹垚?)
                    self.logger.info(output3)
                else:
                    self.logger.error(f"?鎵嬪姩鎺ㄩ€佸け? {output3}")
                    
            except Exception as e:
                self.logger.error(f"鎵嬪姩鎺ㄩ€佸紓? {str(e)}")
        
        thread = threading.Thread(target=_manual_push)
        thread.daemon = True
        thread.start()
    
    def diagnose_git_connection(self):
        """璇婃柇Git杩炴帴闂"""
        self.logger.info("馃敡 寮€濮婫it杩炴帴璇婃柇...")
        
        import threading
        
        def _diagnose():
            try:
                self.logger.info("=" * 60)
                self.logger.info("Git杩炴帴闂璇婃柇鎶ュ憡")
                self.logger.info("=" * 60)
                
                # 1. 娴嬭瘯缃戠粶杩炴帴
                self.logger.info("\n1. 娴嬭瘯缃戠粶杩炴帴...")
                success_ping, output_ping = self.deployment_manager.run_command(
                    "ping",
                    ["-n", "4", "github.com"]
                )
                
                if success_ping:
                    self.logger.success("?Ping娴嬭瘯鎴愬姛")
                    # 鎻愬彇寤惰繜淇℃伅
                    if "骞冲潎" in output_ping:
                        for line in output_ping.split('\n'):
                            if "骞冲潎" in line:
                                self.logger.info(f"缃戠粶寤惰繜: {line.strip()}")
                else:
                    self.logger.error("?Ping娴嬭瘯澶辫触")
                    self.logger.warning("鍙兘鍘熷洜: 缃戠粶鏂紑銆丏NS闂銆侀槻鐏闃绘")
                
                # 2. 娴嬭瘯HTTPS杩炴帴
                self.logger.info("\n2. 娴嬭瘯HTTPS杩炴帴...")
                try:
                    import urllib.request
                    import urllib.error
                    import ssl
                    
                    # 鍒涘缓涓嶉獙璇丼SL鐨勪笂涓嬫枃锛堜粎鐢ㄤ簬娴嬭瘯?                    context = ssl._create_unverified_context()
                    req = urllib.request.Request("https://github.com", method="HEAD")
                    
                    try:
                        response = urllib.request.urlopen(req, timeout=10, context=context)
                        self.logger.success(f"?HTTPS杩炴帴鎴愬姛 (鐘舵€佺爜: {response.status})")
                    except urllib.error.URLError as e:
                        self.logger.error(f"?HTTPS杩炴帴澶辫触: {str(e)}")
                except Exception as e:
                    self.logger.error(f"HTTPS娴嬭瘯寮傚父: {str(e)}")
                
                # 3. 妫€鏌it閰嶇疆
                self.logger.info("\n3. 妫€鏌it閰嶇疆...")
                
                # 妫€鏌ヨ繙绋嬩粨?                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.logger.info("杩滅▼浠撳簱閰嶇疆:")
                    self.logger.info(output_remote)
                else:
                    self.logger.error("?鏃犳硶鑾峰彇杩滅▼浠撳簱閰嶇疆")
                
                # 妫€鏌ヤ唬鐞嗚?                success_proxy, output_proxy = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["config", "--global", "http.proxy"]
                )
                
                if success_proxy and output_proxy.strip():
                    self.logger.warning(f"鈿狅笍 妫€娴嬪埌Git浠ｇ悊璁剧疆: {output_proxy.strip()}")
                else:
                    self.logger.success("?鏃燝it浠ｇ悊璁剧疆")
                
                # 4. 娴嬭瘯Git杩炴帴
                self.logger.info("\n4. 娴嬭瘯Git杩炴帴...")
                success_git, output_git = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["ls-remote", "https://github.com/juemin7-star/toothmen-docs.git", "--heads"]
                )
                
                if success_git:
                    self.logger.success("?Git杩炴帴鎴愬姛")
                else:
                    self.logger.error("?Git杩炴帴澶辫触")
                    self.logger.error(f"閿欒璇︽儏: {output_git}")
                    
                    # 鍒嗘瀽閿欒绫诲瀷
                    error_lower = output_git.lower()
                    if "permission denied" in error_lower or "authentication failed" in error_lower:
                        self.logger.warning("\n馃攼 妫€娴嬪埌璁よ瘉闂:")
                        self.logger.info("  1. 妫€鏌SH瀵嗛挜閰嶇疆")
                        self.logger.info("  2. 妫€鏌itHub Token鏄惁鏈夋晥")
                        self.logger.info("  3. 妫€鏌ヨ繙绋嬩粨搴撴潈?)
                    elif "connection" in error_lower or "timeout" in error_lower or "could not connect" in error_lower:
                        self.logger.warning("\n馃寪 妫€娴嬪埌缃戠粶杩炴帴闂:")
                        self.logger.info("  1. 妫€鏌ョ綉缁滆繛?)
                        self.logger.info("  2. 妫€鏌ラ槻鐏璁剧疆")
                        self.logger.info("  3. 灏濊瘯浣跨敤VPN鎴栧垏鎹㈢綉?)
                    elif "proxy" in error_lower:
                        self.logger.warning("\n馃攧 妫€娴嬪埌浠ｇ悊闂:")
                        self.logger.info("  娓呴櫎浠ｇ悊: git config --global --unset http.proxy")
                
                # 5. 妫€鏌ユ湰鍦版彁浜ょ姸?                self.logger.info("\n5. 妫€鏌ユ湰鍦版彁浜ょ姸?..")
                
                # 鑾峰彇鏈€鍚庢彁?                success_log, output_log = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "--oneline", "-1"]
                )
                
                if success_log:
                    self.logger.info(f"鏈€鍚庢彁? {output_log.strip()}")
                else:
                    self.logger.warning("鏃犳硶鑾峰彇鎻愪氦淇℃伅")
                
                # 妫€鏌ユ湭鎺ㄩ€佺殑鎻愪氦
                success_unpushed, output_unpushed = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["log", "origin/master..HEAD", "--oneline"]
                )
                
                if success_unpushed and output_unpushed.strip():
                    self.logger.warning("鈿狅笍 鏈夋湭鎺ㄩ€佺殑鎻愪氦:")
                    self.logger.info(output_unpushed)
                else:
                    self.logger.success("?鎵€鏈夋彁浜ゅ凡鎺ㄩ€佹垨娌℃湁鏂版彁?)
                
                # 6. 鎻愪緵瑙ｅ喅鏂规
                self.logger.info("\n" + "=" * 60)
                self.logger.info("馃挕 瑙ｅ喅鏂规寤鸿:")
                self.logger.info("=" * 60)
                
                self.logger.info("\n馃敼 濡傛灉HTTPS杩炴帴澶辫触:")
                self.logger.info("  1. 鍒囨崲鍒癝SH鏂瑰紡锛堢偣?鍒囨崲鍒癝SH'鎸夐挳?)
                self.logger.info("  2. 妫€鏌ラ槻鐏璁剧疆")
                self.logger.info("  3. 娓呴櫎浠ｇ悊: git config --global --unset http.proxy")
                self.logger.info("  4. 灏濊瘯浣跨敤VPN鎴栨墜鏈虹儹?)
                
                self.logger.info("\n馃敼 濡傛灉璁よ瘉澶辫触:")
                self.logger.info("  1. 鐢熸垚SSH瀵嗛挜: ssh-keygen -t ed25519 -C \"your_email\"")
                self.logger.info("  2. 娣诲姞鍏挜鍒癎itHub")
                self.logger.info("  3. 娴嬭瘯SSH杩炴帴: ssh -T git@github.com")
                
                self.logger.info("\n馃敼 绔嬪嵆鎿嶄綔:")
                self.logger.info("  1. 浣跨敤'鍒囨崲鍒癝SH'鎸夐挳")
                self.logger.info("  2. 浣跨敤'鎵嬪姩鎺ㄩ€丟it'鎸夐挳")
                self.logger.info("  3. 妫€鏌ョ綉缁滆繛鎺ュ悗閲嶈瘯")
                
                self.logger.success("\n?璇婃柇瀹屾垚?)
                
            except Exception as e:
                self.logger.error(f"璇婃柇杩囩▼涓嚭鐜板紓? {str(e)}")
        
        thread = threading.Thread(target=_diagnose)
        thread.daemon = True
        thread.start()
    
    def switch_to_ssh(self):
        """鍒囨崲鍒癝SH鏂瑰紡"""
        self.logger.info("?姝ｅ湪鍒囨崲鍒癝SH鏂瑰紡...")
        
        import threading
        
        def _switch_ssh():
            try:
                # 1. 鏄剧ず褰撳墠閰嶇疆
                self.logger.info("褰撳墠杩滅▼浠撳簱閰嶇疆:")
                success_remote, output_remote = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "-v"]
                )
                
                if success_remote:
                    self.logger.info(output_remote)
                else:
                    self.logger.error("鏃犳硶鑾峰彇杩滅▼浠撳簱閰嶇疆")
                    return
                
                # 2. 鍒囨崲鍒癝SH
                self.logger.info("\n姝ｅ湪淇敼杩滅▼URL涓篠SH...")
                success_switch, output_switch = self.deployment_manager.run_command(
                    self.deployment_manager.git_path,
                    ["remote", "set-url", "origin", "git@github.com:juemin7-star/toothmen-docs.git"]
                )
                
                if success_switch:
                    self.logger.success("?宸插垏鎹㈠埌SSH鏂瑰紡")
                    
                    # 3. 鏄剧ず鏂伴厤?                    self.logger.info("\n鏂扮殑杩滅▼浠撳簱閰嶇疆:")
                    success_new, output_new = self.deployment_manager.run_command(
                        self.deployment_manager.git_path,
                        ["remote", "-v"]
                    )
                    
                    if success_new:
                        self.logger.info(output_new)
                    else:
                        self.logger.warning("鏃犳硶鑾峰彇鏂伴厤?)
                    
                    # 4. 娴嬭瘯SSH杩炴帴
                    self.logger.info("\n娴嬭瘯SSH杩炴帴...")
                    success_test, output_test = self.deployment_manager.run_command(
                        "ssh",
                        ["-T", "git@github.com"]
                    )
                    
                    if success_test:
                        self.logger.success("?SSH杩炴帴鎴愬姛")
                        self.logger.info(output_test)
                    else:
                        self.logger.warning("鈿狅笍 SSH杩炴帴娴嬭瘯澶辫触")
                        self.logger.info("鍙兘闇€瑕佽缃甋SH瀵嗛挜:")
                        self.logger.info("  1. 鐢熸垚SSH瀵嗛挜: ssh-keygen -t ed25519 -C \"your_email\"")
                        self.logger.info("  2. 娣诲姞鍏挜鍒癎itHub")
                        self.logger.info("  3. 鍚姩ssh-agent: eval \"$(ssh-agent -s)\"")
                        self.logger.info("  4. 娣诲姞绉侀挜: ssh-add ~/.ssh/id_ed25519")
                    
                    # 5. 璇㈤棶鏄惁绔嬪嵆鎺?                    self.logger.info("\n馃挕 寤鸿:")
                    self.logger.info("  鐜板湪鍙互浣跨敤'鎵嬪姩鎺ㄩ€丟it'鎸夐挳杩涜鎺?)
                    self.logger.info("  鎴栫◢鍚庢墽? git push origin master")
                    
                else:
                    self.logger.error(f"?鍒囨崲鍒癝SH澶辫触: {output_switch}")
                    
            except Exception as e:
                self.logger.error(f"鍒囨崲鍒癝SH杩囩▼涓嚭鐜板紓? {str(e)}")
        
        thread = threading.Thread(target=_switch_ssh)
        thread.daemon = True
        thread.start()
    
    def clear_npm_cache(self):
        """娓呴櫎npm缂撳瓨"""
        self.logger.info("姝ｅ湪娓呴櫎npm缂撳瓨...")
        
        import threading
        
        def _clear_cache():
            try:
                success, output = self.deployment_manager.run_command(
                    self.deployment_manager.npm_path,
                    ["cache", "clean", "--force"]
                )
                
                if success:
                    self.logger.success("?npm缂撳瓨娓呴櫎鎴愬姛")
                    self.logger.info(output)
                else:
                    self.logger.error(f"?npm缂撳瓨娓呴櫎澶辫触: {output}")
                    
            except Exception as e:
                self.logger.error(f"娓呴櫎npm缂撳瓨寮傚父: {str(e)}")
        
        thread = threading.Thread(target=_clear_cache)
        thread.daemon = True
        thread.start()
    
    def check_config(self):
        """妫€鏌ラ厤?""
        self.logger.info("姝ｅ湪妫€鏌ラ厤?..")
        
        try:
            # 浣跨敤涓荤▼搴忕殑config锛岃€屼笉鏄痙eployment_manager鐨刢onfig
            config = self.config
            
            self.logger.info("褰撳墠閰嶇疆:")
            self.logger.info(f"椤圭洰璺緞: {config.get('project_path', '鏈?)}")
            self.logger.info(f"docs鏂囦欢? {config.get('docs_folder', '鏈?)}")
            self.logger.info(f"npm璺緞: {config.get('npm_path', '鏈?)}")
            self.logger.info(f"git璺緞: {config.get('git_path', '鏈?)}")
            self.logger.info(f"渚ц竟鏍忚矾? {config.get('sidebars_path', '鏈?)}")
            
            # 妫€鏌ヨ矾寰勬槸鍚﹀瓨?            import os
            project_path = config.get('project_path', '')
            if project_path and os.path.exists(project_path):
                self.logger.success("?椤圭洰璺緞瀛樺湪")
                
                # 妫€鏌ュ叧閿矾寰勶紙鐩稿浜庨」鐩矾寰勶級
                project_dir = Path(project_path)
                
                # docs鏂囦欢?                docs_folder_rel = config.get('docs_folder', '')
                if docs_folder_rel:
                    docs_folder_abs = project_dir / docs_folder_rel
                    if docs_folder_abs.exists():
                        self.logger.success(f"?docs鏂囦欢澶瑰瓨? {docs_folder_abs}")
                    else:
                        self.logger.error(f"?docs鏂囦欢澶逛笉瀛樺湪: {docs_folder_abs}")
                        self.logger.info(f"  鐩稿璺緞: {docs_folder_rel}")
                else:
                    self.logger.error("?docs鏂囦欢澶规湭璁剧疆")
                
                # 渚ц竟鏍忔枃?                sidebars_path_rel = config.get('sidebars_path', '')
                if sidebars_path_rel:
                    sidebars_path_abs = project_dir / sidebars_path_rel
                    if sidebars_path_abs.exists():
                        self.logger.success(f"?渚ц竟鏍忔枃浠跺瓨? {sidebars_path_abs}")
                        self.logger.info(f"  璇存槑: 杩欐槸Docusaurus鐨勪晶杈规爮閰嶇疆鏂囦欢锛岀敤浜庤嚜鍔ㄧ敓鎴愭枃妗ｅ?)
                    else:
                        self.logger.error(f"?渚ц竟鏍忔枃浠朵笉瀛樺湪: {sidebars_path_abs}")
                        self.logger.info(f"  鐩稿璺緞: {sidebars_path_rel}")
                        self.logger.info(f"  璇存槑: 杩欐槸Docusaurus鐨勪晶杈规爮閰嶇疆鏂囦欢锛岀▼搴忎細鑷姩鍒涘缓")
                else:
                    self.logger.error("?渚ц竟鏍忔枃浠舵湭璁剧疆")
                
                # 妫€鏌ユ枃浠跺す鍒嗙被閰嶇疆
                folder_config = config.get('folder_classification', {})
                if folder_config:
                    self.logger.info("\n鏂囦欢澶瑰垎绫婚厤?")
                    reverse_folders = folder_config.get('reverse_order_folders', [])
                    if reverse_folders:
                        self.logger.info(f"鍊掑簭鎺掑簭鏂囦欢? {', '.join(reverse_folders)}")
                    else:
                        self.logger.warning("鈿狅笍 鏈厤缃€掑簭鎺掑簭鏂囦欢?)
                    
                    sort_by_prefix = folder_config.get('sort_by_number_prefix', True)
                    self.logger.info(f"鎸夋暟瀛楀墠缂€鎺掑簭: {'? if sort_by_prefix else '?}")
                    
                    clean_prefix = folder_config.get('clean_number_prefix', True)
                    self.logger.info(f"娓呯悊鏁板瓧鍓嶇紑: {'? if clean_prefix else '?}")
                else:
                    self.logger.warning("鈿狅笍 鏈厤缃枃浠跺す鍒嗙被璁剧疆")
                
            else:
                self.logger.error(f"?椤圭洰璺緞涓嶅瓨? {project_path}")
                
        except Exception as e:
            self.logger.error(f"妫€鏌ラ厤缃紓? {str(e)}")
    
    # ========== 閮ㄧ讲娴佺▼鎺у埗鏂规硶 ==========
    
    def start_deployment_flow(self):
        """寮€濮嬮儴缃叉祦?""
        self.deployment_started = True
        self.deployment_step = 0
        
        # 绂佺敤寮€濮嬫寜閽紝鍚敤缁撴潫鎸夐挳
        self.btn_start_deploy.config(state="disabled")
        self.btn_end_deploy.config(state="normal")
        
        # 鍚敤绗竴涓儴缃叉?        self.enable_deployment_step(0)
        
        self.logger.info("閮ㄧ讲娴佺▼宸插紑濮嬶紝璇锋寜椤哄簭鎵ц姝ラ")
        self.logger.info("姝ラ1: 鍒锋柊鏂囦欢缁撴瀯 ?姝ラ2: 鐢熸垚渚ц竟??姝ラ3: 鏈湴鏋勫缓娴嬭瘯 ?姝ラ4: 鏈湴棰勮 ?姝ラ5: 鑷姩閮ㄧ讲")
    
    def end_deployment_flow(self):
        """缁撴潫閮ㄧ讲娴佺▼"""
        self.deployment_started = False
        
        # 鍚敤寮€濮嬫寜閽紝绂佺敤缁撴潫鎸夐挳
        self.btn_start_deploy.config(state="normal")
        self.btn_end_deploy.config(state="disabled")
        
        # 绂佺敤鎵€鏈夋楠ゆ寜?        for i in range(len(self.deployment_buttons)):
            self.disable_deployment_step(i)
        
        self.logger.info("閮ㄧ讲娴佺▼宸茬粨?)
    
    def enable_deployment_step(self, step_index):
        """鍚敤鎸囧畾姝ラ鐨勬寜?""
        if 0 <= step_index < len(self.deployment_buttons):
            button_name = self.deployment_buttons[step_index][0]
            button = getattr(self, f"btn_{button_name.replace(' ', '_')}")
            button.config(state="normal")
    
    def disable_deployment_step(self, step_index):
        """绂佺敤鎸囧畾姝ラ鐨勬寜?""
        if 0 <= step_index < len(self.deployment_buttons):
            button_name = self.deployment_buttons[step_index][0]
            button = getattr(self, f"btn_{button_name.replace(' ', '_')}")
            button.config(state="disabled")
    
    def next_deployment_step(self):
        """杩涘叆涓嬩竴涓儴缃叉?""
        if self.deployment_started and self.deployment_step < len(self.deployment_buttons) - 1:
            # 绂佺敤褰撳墠姝ラ
            self.disable_deployment_step(self.deployment_step)
            
            # 鍚敤涓嬩竴涓?            self.deployment_step += 1
            self.enable_deployment_step(self.deployment_step)
            
            self.logger.info(f"宸茶В閿佹?{self.deployment_step+1}: {self.deployment_buttons[self.deployment_step][0]}")
    
    def update_button_state(self, button_name, state):
        """鏇存柊鎸夐挳鐘?""
        # 鑾峰彇鎸夐挳瀵硅薄
        button_attr_name = button_name.replace(' ', '_')
        button = getattr(self, f"btn_{button_attr_name}")
        
        colors = {
            "normal": ("SystemButtonFace", "black"),
            "running": ("yellow", "black"),
            "success": ("green", "white"),
            "error": ("red", "white")
        }
        
        bg_color, fg_color = colors.get(state, colors["normal"])
        
        # 鏇存柊鎸夐挳棰滆壊
        button.config(background=bg_color, foreground=fg_color)
        
        # 濡傛灉鏄垚鍔熺姸鎬侊紝瑙ｉ攣涓嬩竴涓?        if state == "success" and self.deployment_started:
            # 鎵惧埌褰撳墠鎸夐挳鐨勭储?            for i, (name, _, _) in enumerate(self.deployment_buttons):
                if name == button_name:
                    # 濡傛灉鏄嚜鍔ㄩ儴缃叉垚鍔燂紝2绉掑悗缁撴潫娴佺▼
                    if button_name == "鑷姩閮ㄧ讲":
                        self.root.after(2000, self.end_deployment_flow)
                    else:
                        # 瑙ｉ攣涓嬩竴涓?                        self.root.after(1000, self.next_deployment_step)
                    break
            
            # 3绉掑悗鎭㈠棰滆壊
            self.root.after(3000, lambda: button.config(
                background=colors["normal"][0],
                foreground=colors["normal"][1]
            ))
        
        # 濡傛灉鏄敊璇姸鎬侊紝3绉掑悗鎭㈠棰滆壊
        elif state == "error":
            self.root.after(3000, lambda: button.config(
                background=colors["normal"][0],
                foreground=colors["normal"][1]
            ))

def main():
    """涓诲嚱?""
    root = tk.Tk()
    app = ToothMenDocsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()


