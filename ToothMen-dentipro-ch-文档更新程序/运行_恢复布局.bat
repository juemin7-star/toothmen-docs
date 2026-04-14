@echo off
chcp 65001 >nul
title ToothMen文档管理工具 v3.16 - 恢复原始布局版

echo.
echo ========================================
echo   ToothMen文档管理工具 v3.16
echo   恢复原始布局版
echo ========================================
echo.
echo 布局说明:
echo   1. 上面: 文件列表 (可以右侧排序)
echo   2. 中间: 管理按钮区域
echo   3. 下面: 日志区域 (左侧)
echo   4. 右下: 调试工具区域 (右侧)
echo.
echo 正在启动程序...
echo.

python main_restored_layout.py

if errorlevel 1 (
    echo.
    echo 程序启动失败，请检查Python环境。
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

echo.
echo 程序已退出。
echo 按任意键关闭窗口...
pause >nul