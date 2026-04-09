# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 - 单文件版
参考: ToothMen-Update-APP 打包逻辑
"""

import os
import sys

block_cipher = None
app_dir = SPECPATH

a = Analysis(
    [os.path.join(app_dir, 'main.py')],
    pathex=[app_dir],
    binaries=[],
    datas=[
        # 包含配置文件
        (os.path.join(app_dir, 'config.json'), '.'),
        (os.path.join(app_dir, 'requirements.txt'), '.'),
    ],
    hiddenimports=[
        # Tkinter 相关
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        
        # 标准库
        'threading',
        'subprocess',
        'json',
        'pathlib',
        'shutil',
        'time',
        'datetime',
        're',
        'os',
        'sys',
        'webbrowser',
        
        # 自定义模块
        'mdx_checker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ToothMenDocsManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果需要图标，可以添加
)
