@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ToothMen文档管理工具 v3.16
echo ========================================
echo.
echo 正在启动 ToothMenDocsManager_v3.16.exe...
echo.

if exist "dist\ToothMenDocsManager_v3.16.exe" (
    start "" "dist\ToothMenDocsManager_v3.16.exe"
    echo ✅ 程序已启动！
) else (
    echo ❌ 错误: 找不到 ToothMenDocsManager_v3.16.exe
    echo.
    echo 请确保:
    echo 1. 程序已正确打包
    echo 2. dist文件夹中存在 ToothMenDocsManager_v3.16.exe
    echo.
    pause
)

echo.
echo 按任意键退出...
pause >nul