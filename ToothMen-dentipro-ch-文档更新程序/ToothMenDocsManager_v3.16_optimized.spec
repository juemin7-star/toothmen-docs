# -*- mode: python ; coding: utf-8 -*-
"""
优化版的spec文件，解决启动跳动问题
"""

block_cipher = None

a = Analysis(
    ['main_restored_layout.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config_new.json', '.'),
        ('deployment_manager_new.py', '.'),
        ('mdx_checker.py', '.'),
        ('logger.py', '.'),
        ('sort_config.json', '.'),
        ('版本信息_v3.16.md', '.')
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'pathlib',
        'json',
        're',
        'threading',
        'subprocess',
        'os',
        'sys',
        'time',
        'shutil',
        'webbrowser',
        'urllib.parse',
        'urllib.request',
        'urllib.error',
        'unicodedata',
        'datetime',
        'typing',
        'collections',
        'collections.abc',
        'inspect',
        'hashlib',
        'base64',
        'html',
        'html.parser',
        'html.entities',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 排除不必要的图形库
        'numpy',       # 排除科学计算库
        'pandas',      # 排除数据分析库
        'scipy',       # 排除科学计算库
        'sklearn',     # 排除机器学习库
        'PIL',         # 排除图像处理库（如果不需要）
        'pygame',      # 排除游戏库
        'sqlite3',     # 排除数据库（如果不需要）
        'test',        # 排除测试模块
        'unittest',    # 排除单元测试
        'pydoc',       # 排除文档生成
        'doctest',     # 排除文档测试
    ],
    noarchive=False,
    optimize=1,  # 优化级别1（平衡优化）
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ToothMenDocsManager_v3.16_optimized',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 窗口模式，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

# 可选：收集额外的文件
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ToothMenDocsManager_v3.16_optimized',
)