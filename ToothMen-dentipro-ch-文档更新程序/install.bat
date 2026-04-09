@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档更新程序 安装脚本
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

echo 正在安装 ToothMen文档更新程序...
echo.

REM 创建程序目录
set "PROGRAM_DIR=%ProgramFiles%\ToothMenDocsManager"
if not exist "%PROGRAM_DIR%" (
    mkdir "%PROGRAM_DIR%"
    echo 创建程序目录: %PROGRAM_DIR%
)

REM 复制文件
copy "%~dp0disc\ToothMenDocsManager.exe" "%PROGRAM_DIR%\" /Y
echo 复制程序文件...

REM 创建桌面快捷方式
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\ToothMen文档更新程序.lnk"

REM 使用 PowerShell 创建快捷方式
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%PROGRAM_DIR%\ToothMenDocsManager.exe'; $Shortcut.WorkingDirectory = '%PROGRAM_DIR%'; $Shortcut.Save()"
echo 创建桌面快捷方式...

REM 创建开始菜单快捷方式
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ToothMen"
if not exist "%START_MENU%" mkdir "%START_MENU%"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\ToothMen文档更新程序.lnk'); $Shortcut.TargetPath = '%PROGRAM_DIR%\ToothMenDocsManager.exe'; $Shortcut.WorkingDirectory = '%PROGRAM_DIR%'; $Shortcut.Save()"
echo 创建开始菜单快捷方式...

echo.
echo ========================================
echo  安装完成！
echo ========================================
echo.
echo 程序已安装到: %PROGRAM_DIR%
echo 桌面快捷方式: ToothMen文档更新程序.lnk
echo 开始菜单: ToothMen > ToothMen文档更新程序
echo.
echo 按任意键退出...
pause >nul
