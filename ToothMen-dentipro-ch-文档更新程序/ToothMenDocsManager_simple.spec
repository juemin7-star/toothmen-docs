# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_simple_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[('config_new.json', '.'), ('deployment_manager_new.py', '.'), ('mdx_checker.py', '.'), ('logger.py', '.'), ('sort_config.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='ToothMenDocsManager_simple',
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
)
