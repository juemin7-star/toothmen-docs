@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档管理系统 - 安装程序
echo ========================================
echo.

echo 1. 停止正在运行的程序...
taskkill /f /im ToothMenDocsManager.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 2. 复制程序文件...
if exist "disc\ToothMenDocsManager.exe" (
    copy "disc\ToothMenDocsManager.exe" "ToothMenDocsManager.exe" /Y
    echo   ✅ 程序文件已复制
) else (
    echo   ❌ 找不到程序文件
    pause
    exit /b 1
)

echo.
echo 3. 解除文件锁定属性（解决Windows Defender警告）...
powershell -Command "Unblock-File -Path 'ToothMenDocsManager.exe'" >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✅ 文件锁定已解除
) else (
    echo   ⚠️ 解除锁定失败（可能需要管理员权限）
)

echo.
echo 4. 创建桌面快捷方式...
set SHORTCUT_PATH=%USERPROFILE%\Desktop\ToothMen文档管理系统.lnk
set TARGET_PATH=%CD%\ToothMenDocsManager.exe
set ICON_PATH=%CD%\ToothMenDocsManager.exe

powershell -Command "
$WshShell = New-Object -ComObject WScript.Shell;
$Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%');
$Shortcut.TargetPath = '%TARGET_PATH%';
$Shortcut.WorkingDirectory = '%CD%';
$Shortcut.IconLocation = '%ICON_PATH%,0';
$Shortcut.Save();
" >nul 2>&1

if exist "%SHORTCUT_PATH%" (
    echo   ✅ 桌面快捷方式已创建
) else (
    echo   ⚠️ 创建快捷方式失败
)

echo.
echo 5. 创建开始菜单快捷方式...
set START_MENU_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ToothMen文档管理系统.lnk
powershell -Command "
$WshShell = New-Object -ComObject WScript.Shell;
$Shortcut = $WshShell.CreateShortcut('%START_MENU_PATH%');
$Shortcut.TargetPath = '%TARGET_PATH%';
$Shortcut.WorkingDirectory = '%CD%';
$Shortcut.IconLocation = '%ICON_PATH%,0';
$Shortcut.Save();
" >nul 2>&1

if exist "%START_MENU_PATH%" (
    echo   ✅ 开始菜单快捷方式已创建
) else (
    echo   ⚠️ 创建开始菜单快捷方式失败
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo ✅ 程序已安装到当前目录: %CD%
echo 📁 桌面快捷方式: ToothMen文档管理系统.lnk
echo 🚀 开始菜单快捷方式: ToothMen文档管理系统
echo.
echo 💡 如果Windows Defender仍然阻止程序运行:
echo   1. 右键点击程序 → 属性 → 常规 → 解除锁定
echo   2. 或点击"更多信息" → "仍要运行"
echo   3. 或将程序添加到Windows Defender排除列表
echo.
echo 按任意键启动程序...
pause >nul

echo.
echo 正在启动程序...
start "" "ToothMenDocsManager.exe"

exit /b 0
