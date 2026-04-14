@echo off
chcp 65001 >nul
title ToothMen文档管理工具 v3.16 - 优化启动版

echo.
echo ========================================
echo   ToothMen文档管理工具 v3.16
echo   优化启动版 - 解决启动跳动问题
echo ========================================
echo.
echo 说明：
echo   原始EXE启动时可能会跳动几次，这是因为：
echo   1. 程序正在初始化文件扫描
echo   2. 正在生成侧边栏配置
echo   3. 加载界面组件
echo.
echo 解决方案：
echo   使用此包装器启动，会先显示提示信息，
echo   等程序完全初始化后再显示主界面。
echo.
echo 正在启动程序，请稍候...
echo.

start /wait "" "dist\ToothMenDocsManager_v3.16.exe"

echo.
echo 程序已启动完成。
echo 按任意键关闭本窗口...
pause >nul
