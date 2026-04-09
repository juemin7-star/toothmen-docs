@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ToothMen文档管理工具 - 打包脚本
echo ========================================
echo.

REM 检查系统Python
echo 步骤1: 检查系统Python...
set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_PATH%" (
    echo [错误] 系统Python未找到: %PYTHON_PATH%
    echo 请安装Python 3.12到默认位置
    pause
    exit /b 1
)

echo [成功] Python找到: %PYTHON_PATH%
"%PYTHON_PATH%" --version

REM 检查PyInstaller
echo.
echo 步骤2: 检查PyInstaller...
set "PYINSTALLER_PATH=%LOCALAPPDATA%\Programs\Python\Python312\Scripts\pyinstaller.exe"

if not exist "%PYINSTALLER_PATH%" (
    echo [警告] PyInstaller未安装，正在安装...
    "%PYTHON_PATH%" -m pip install pyinstaller
    
    if errorlevel 1 (
        echo [错误] PyInstaller安装失败
        pause
        exit /b 1
    )
    echo [成功] PyInstaller安装完成
)

echo [成功] PyInstaller找到: %PYINSTALLER_PATH%

REM 创建spec文件
echo.
echo 步骤3: 创建spec文件...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis(
echo     ['main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ('config.json', '.'),
echo         ('requirements.txt', '.'),
echo     ],
echo     hiddenimports=[],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     noarchive=False,
echo     optimize=0,
echo )
echo.
echo pyz = PYZ(a.pure)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.datas,
echo     [],
echo     name='ToothMenDocsManager',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo )
) > toothmen_docs_manager.spec

if errorlevel 1 (
    echo [错误] 创建spec文件失败
    pause
    exit /b 1
)

echo [成功] spec文件创建完成

REM 执行打包
echo.
echo 步骤4: 开始打包为EXE...
echo 这可能需要几分钟时间，请耐心等待...
echo.

"%PYINSTALLER_PATH%" toothmen_docs_manager.spec --noconfirm --clean

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo [成功] 打包完成！

REM 复制到disc目录
echo.
echo 步骤5: 复制到disc目录...

if not exist "disc" mkdir disc

if exist "dist\ToothMenDocsManager.exe" (
    copy "dist\ToothMenDocsManager.exe" "disc\" >nul
    copy "config.json" "disc\" >nul
    copy "README.md" "disc\" >nul
    
    echo [成功] EXE文件已复制到 disc\ToothMenDocsManager.exe
    
    REM 显示文件信息
    for %%F in ("disc\ToothMenDocsManager.exe") do (
        set "filesize=%%~zF"
        set /a filesize_mb=!filesize! / 1048576
        set /a filesize_kb=!filesize! / 1024
        echo 文件大小: !filesize_mb! MB (!filesize_kb! KB)
    )
) else (
    echo [错误] 未找到生成的EXE文件
    pause
    exit /b 1
)

REM 清理临时文件
echo.
echo 步骤6: 清理临时文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.spec" del "*.spec"
if exist "*.log" del "*.log"

echo [成功] 临时文件清理完成

REM 完成
echo.
echo ========================================
echo   打包流程完成！
echo ========================================
echo.
echo 生成的EXE文件位置:
echo   disc\ToothMenDocsManager.exe
echo.
echo 配置文件位置:
echo   disc\config.json
echo.
echo 使用方法:
echo   1. 双击运行 ToothMenDocsManager.exe
echo   2. 确保项目路径配置正确
echo   3. 开始管理您的文档
echo.
echo 注意: 首次运行可能需要管理员权限
echo.
pause