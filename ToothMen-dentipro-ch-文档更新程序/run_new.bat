@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档管理系统 v2.0 - 启动脚本
echo ========================================
echo.
echo 启动全新版本的文档管理系统...
echo 支持文件夹分类和数字前缀排序
echo.

REM 检查Python
echo 检查Python环境...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    echo 请安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)

REM 检查依赖
echo 检查Python依赖...
pip install -r requirements.txt >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️ 依赖安装失败，尝试继续运行...
)

REM 启动程序
echo.
echo 启动主程序...
python main_new.py

if %errorLevel% neq 0 (
    echo.
    echo ❌ 程序启动失败
    echo 可能的原因：
    echo 1. Python依赖未安装
    echo 2. 配置文件错误
    echo 3. 缺少必要的模块
    echo.
    echo 请检查日志文件：toothmen_docs_manager.log
    pause
    exit /b 1
)

echo.
echo ✅ 程序已正常退出
pause