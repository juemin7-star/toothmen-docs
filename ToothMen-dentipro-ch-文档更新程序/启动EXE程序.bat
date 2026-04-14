@echo off
chcp 65001 >nul
title ToothMen文档管理工具 v3.16 - EXE版启动器

echo.
echo ========================================
echo   ToothMen文档管理工具 v3.16
echo   EXE独立版启动器
echo ========================================
echo.
echo 程序信息:
echo   版本: v3.16 (恢复原始布局 + 排序按钮版)
echo   文件: ToothMenDocsManager_v3.16.exe
echo   大小: 11.89 MB
echo   类型: 独立可执行文件 (无需Python)
echo.
echo 功能特性:
echo   1. ✅ 原始布局恢复 (上面文件列表，中间管理，下面日志)
echo   2. ✅ 排序控制按钮 (文件夹/文件上下移动)
echo   3. ✅ 完整工作流系统 (清理缓存+自动检测+构建)
echo   4. ✅ 缓存清理功能
echo.
echo 正在启动程序...
echo.

cd /d "%~dp0"
start "" "dist\ToothMenDocsManager_v3.16.exe"

echo.
echo 程序已启动，请查看弹出的窗口。
echo 按任意键关闭本窗口...
pause >nul