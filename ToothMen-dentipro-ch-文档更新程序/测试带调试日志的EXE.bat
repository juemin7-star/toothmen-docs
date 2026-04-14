@echo off
chcp 65001 >nul
echo 🚀 测试带调试日志的EXE程序...
echo.

echo 📁 程序监控的文件夹路径：
echo   D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs
echo.

echo 📊 实际文件夹内容：
dir "D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs" /B
echo.

echo 🔍 启动带调试日志的EXE程序...
echo   注意：程序日志区域会显示调试信息
echo.

cd /d "%~dp0dist"
start "" "ToothMenDocsManager_simple_fixed.exe"

echo.
echo ✅ 程序已启动，请检查：
echo   1. GUI窗口是否正常显示
echo   2. 日志区域是否显示调试信息
echo   3. 文件夹列表是否显示内容
echo.
pause