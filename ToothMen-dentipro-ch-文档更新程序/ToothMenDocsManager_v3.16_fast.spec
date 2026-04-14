# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_fast_start.py'],
    pathex=[],
    binaries=[],
    datas=[('config_new.json', '.'), ('deployment_manager_new.py', '.'), ('mdx_checker.py', '.'), ('logger.py', '.'), ('sort_config.json', '.'), ('版本信息_v3.16.md', '.')],
    hiddenimports=['tkinter', 'pathlib', 'json', 're', 'threading', 'subprocess', 'os', 'sys', 'time', 'shutil', 'webbrowser', 'urllib.parse', 'urllib.request', 'urllib.error', 'unicodedata'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'sklearn', 'PIL', 'pygame', 'sqlite3', 'test', 'unittest', 'pydoc', 'doctest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ToothMenDocsManager_v3.16_fast',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
