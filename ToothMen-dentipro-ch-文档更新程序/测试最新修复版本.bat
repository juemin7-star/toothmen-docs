@echo off
chcp 65001 >nul
echo 🚀 测试最新修复版本...
echo.

echo 📊 检查Python脚本版本...
python --version
echo.

echo 🔍 运行最新修复的Python脚本...
python main_simple_fixed.py

echo.
echo ✅ 如果程序正常运行，说明修复成功
echo ❌ 如果出现AttributeError错误，说明运行的是旧版本
echo.
pause