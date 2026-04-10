@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档管理系统 v2.0 - 安装程序
echo ========================================
echo.
echo 全新版本功能：
echo 1. 文件夹分类管理（按数字前缀排序）
echo 2. 树形文件夹结构显示
echo 3. 特殊文件夹倒序排序（补丁更新日志）
echo 4. 自动侧边栏生成
echo.

echo 1. 停止正在运行的程序...
taskkill /f /im ToothMenDocsManager_v2.exe >nul 2>&1
taskkill /f /im ToothMenDocsManager.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 2. 复制程序文件...
if exist "disc\ToothMenDocsManager_v2.exe" (
    copy "disc\ToothMenDocsManager_v2.exe" "ToothMenDocsManager_v2.exe" /Y
    echo   ✅ 程序文件已复制
) else (
    echo   ❌ 找不到程序文件
    pause
    exit /b 1
)

echo.
echo 3. 解除文件锁定属性（解决Windows Defender警告）...
powershell -Command "Unblock-File -Path 'ToothMenDocsManager_v2.exe'" >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✅ 文件锁定已解除
) else (
    echo   ⚠️ 解除锁定失败（可能需要管理员权限）
)

echo.
echo 4. 创建桌面快捷方式...
set SHORTCUT_PATH=%USERPROFILE%\Desktop\ToothMen文档管理系统_v2.lnk
set TARGET_PATH=%CD%\ToothMenDocsManager_v2.exe
set ICON_PATH=%CD%\ToothMenDocsManager_v2.exe

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
set START_MENU_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ToothMen文档管理系统_v2.lnk
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
echo 📁 桌面快捷方式: ToothMen文档管理系统_v2.lnk
echo 🚀 开始菜单快捷方式: ToothMen文档管理系统_v2
echo.
echo 📂 文档文件夹结构要求：
echo   1. 所有文档放在: D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple\docs
echo   2. 文件夹命名: 数字-名称（如: 1-产品文档）
echo   3. 文件命名: 数字-名称.mdx（如: 1-产品介绍.mdx）
echo   4. 特殊文件夹: 补丁更新日志（自动倒序排序）
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
start "" "ToothMenDocsManager_v2.exe"

exit /b 0