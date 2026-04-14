@echo off
chcp 65001 >nul
echo 🚀 启动修复版EXE程序...
echo.

cd /d "%~dp0dist"
start "" "ToothMenDocsManager_simple_fixed.exe"

echo ✅ 程序已启动，请检查GUI窗口是否正常显示
echo.
pause