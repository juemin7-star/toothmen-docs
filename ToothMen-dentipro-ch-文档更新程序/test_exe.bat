@echo off
echo 测试EXE启动...
echo.

echo 1. 测试超简单版本:
start "" "dist\ToothMenDocsManager_ultra_simple.exe"
timeout /t 5
taskkill /f /im ToothMenDocsManager_ultra_simple.exe >nul 2>&1

echo.
echo 2. 测试简单修复版本:
start "" "dist\ToothMenDocsManager_simple_fixed.exe"
timeout /t 5
taskkill /f /im ToothMenDocsManager_simple_fixed.exe >nul 2>&1

echo.
echo 测试完成
pause