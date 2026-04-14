@echo off
chcp 65001 >nul
title ToothMen文档管理工具 - 一键打包

echo.
echo ========================================
echo   ToothMen文档管理工具 v3.16
echo   一键打包脚本
echo ========================================
echo.

echo 步骤1: 检查Python环境
echo.
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python
    echo 请先安装Python 3.12
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

echo.
echo 步骤2: 检查PyInstaller
echo.
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller未安装，正在安装...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller已安装
)

echo.
echo 步骤3: 清理旧文件
echo.
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
del /q *.spec 2>nul

echo.
echo 步骤4: 开始打包
echo.
echo 正在打包，这可能需要几分钟...
echo.

REM 最简单的打包命令
pyinstaller ^
  --name=ToothMenDocsManager ^
  --windowed ^
  --onefile ^
  --icon=icon.ico ^
  --add-data="config_new.json;." ^
  --add-data="deployment_manager_new.py;." ^
  --add-data="mdx_checker.py;." ^
  --add-data="logger.py;." ^
  --add-data="sort_config.json;." ^
  main_simple_fixed.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 打包成功！
    echo.
    echo 📁 EXE文件: dist\ToothMenDocsManager.exe
    echo.
    
    REM 显示文件信息
    for %%f in (dist\ToothMenDocsManager.exe) do (
        set size=%%~zf
        set /a sizeMB=!size! / 1048576
        echo 文件大小: !sizeMB! MB
    )
    
    echo.
    echo 🚀 启动方法:
    echo 1. 直接双击 dist\ToothMenDocsManager.exe
    echo 2. 或运行: start dist\ToothMenDocsManager.exe
    echo.
    
    REM 创建启动脚本
    echo @echo off > 启动程序.bat
    echo start "" "dist\ToothMenDocsManager.exe" >> 启动程序.bat
    echo ✅ 已创建启动脚本: 启动程序.bat
    
) else (
    echo.
    echo ❌ 打包失败
    echo 请检查错误信息
)

echo.
echo ========================================
echo   打包完成
echo ========================================
echo.
pause