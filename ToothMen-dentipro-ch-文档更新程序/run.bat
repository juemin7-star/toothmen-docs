@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ToothMen文档管理工具
echo ========================================
echo.

REM 检查Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查Python版本
python --version
if %errorlevel% neq 0 (
    echo [错误] Python版本检查失败
    pause
    exit /b 1
)

REM 运行主程序
echo.
echo 正在启动ToothMen文档管理工具...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序启动失败
    echo 请检查：
    echo 1. Python是否安装正确
    echo 2. 依赖是否完整
    echo 3. 配置文件是否正确
    pause
    exit /b 1
)

echo.
echo 程序已退出
pause