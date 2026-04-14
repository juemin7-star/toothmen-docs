@echo off
chcp 65001 >nul
title ToothMen文档管理工具 - 简单打包流程

echo.
echo ========================================
echo   ToothMen文档管理工具 v3.16
echo   简单打包流程
echo ========================================
echo.

echo 步骤1: 检查系统Python
echo.
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.12
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ 找到Python
python --version

echo.
echo 步骤2: 安装PyInstaller
echo.
pip install pyinstaller --upgrade

echo.
echo 步骤3: 打包程序
echo.
echo 正在打包，请稍候...
echo.

REM 使用最简单的打包命令
pyinstaller --name=ToothMenDocsManager_v3.16_simple ^
  --windowed ^
  --onefile ^
  --add-data="config_new.json;." ^
  --add-data="deployment_manager_new.py;." ^
  --add-data="mdx_checker.py;." ^
  --add-data="logger.py;." ^
  --add-data="sort_config.json;." ^
  --add-data="版本信息_v3.16.md;." ^
  main_restored_layout.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 打包成功！
    echo.
    echo 📁 EXE文件位置: dist\ToothMenDocsManager_v3.16_simple.exe
    echo.
    dir "dist\ToothMenDocsManager_v3.16_simple.exe"
) else (
    echo.
    echo ❌ 打包失败
)

echo.
echo ========================================
echo   打包完成
echo ========================================
echo.
echo 使用方法:
echo 1. 双击 dist\ToothMenDocsManager_v3.16_simple.exe 启动程序
echo 2. 或使用 启动EXE程序.bat
echo.
pause