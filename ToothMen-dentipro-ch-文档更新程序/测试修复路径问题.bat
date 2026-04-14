@echo off
chcp 65001 >nul
echo 🚀 测试修复路径问题的EXE程序...
echo.

echo 📁 检查监控的文件夹路径：
echo   程序监控: D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs
echo.

echo 📊 文件夹内容：
dir "D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs" /B
echo.

echo 🔍 启动修复后的EXE程序...
cd /d "%~dp0dist"
start "" "ToothMenDocsManager_simple_fixed.exe"

echo.
echo ✅ 程序已启动，请检查：
echo   1. GUI窗口是否正常显示
echo   2. 文件夹列表是否显示3个文件夹
echo   3. 每个文件夹下是否显示文件
echo.
pause