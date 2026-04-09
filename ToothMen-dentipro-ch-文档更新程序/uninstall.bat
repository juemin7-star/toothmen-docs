@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档更新程序 卸载脚本
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理员权限运行此脚本
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo 正在卸载 ToothMen文档更新程序...
echo.

REM 删除桌面快捷方式
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\ToothMen文档更新程序.lnk"
if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo 删除桌面快捷方式...
)

REM 删除开始菜单快捷方式
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ToothMen"
if exist "%START_MENU%\ToothMen文档更新程序.lnk" (
    del "%START_MENU%\ToothMen文档更新程序.lnk"
    echo 删除开始菜单快捷方式...
)

REM 删除开始菜单文件夹（如果为空）
if exist "%START_MENU%" (
    dir "%START_MENU%" /b | findstr "." >nul
    if errorlevel 1 (
        rmdir "%START_MENU%"
        echo 删除开始菜单文件夹...
    )
)

REM 删除程序目录
set "PROGRAM_DIR=%ProgramFiles%\ToothMenDocsManager"
if exist "%PROGRAM_DIR%" (
    rmdir /s /q "%PROGRAM_DIR%"
    echo 删除程序目录: %PROGRAM_DIR%
)

echo.
echo ========================================
echo  卸载完成！
echo ========================================
echo.
echo ToothMen文档更新程序已从系统中移除。
echo.
echo 按任意键退出...
pause >nul
