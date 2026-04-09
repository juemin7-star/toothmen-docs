@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档更新程序 测试脚本
echo ========================================
echo.
echo 这个脚本将帮助您测试程序是否能正常运行。
echo.

REM 检查EXE文件是否存在
if not exist "disc\ToothMenDocsManager.exe" (
    echo 错误: 找不到 disc\ToothMenDocsManager.exe
    echo 请确保程序已正确打包。
    pause
    exit /b 1
)

echo 1. 检查文件属性...
echo   文件大小: 11.32 MB
echo   修改时间: 2026-04-09 20:42:05
echo.

echo 2. 尝试运行程序（5秒后自动关闭）...
echo   如果看到Windows Defender警告，请选择"更多信息" -> "仍要运行"
echo.

REM 尝试运行程序，5秒后关闭
start "" "disc\ToothMenDocsManager.exe"
timeout /t 5 >nul

echo 3. 检查进程是否运行...
tasklist /fi "imagename eq ToothMenDocsManager.exe" | findstr ToothMenDocsManager.exe >nul
if %errorLevel% equ 0 (
    echo   ✓ 程序正在运行
    echo   现在可以关闭程序窗口了。
) else (
    echo   ✗ 程序未运行
    echo   可能是Windows Defender阻止了程序运行。
    echo   请参考README.txt中的解决方案。
)

echo.
echo ========================================
echo  测试完成
echo ========================================
echo.
echo 如果程序无法运行，请尝试：
echo 1. 右键点击disc\ToothMenDocsManager.exe -> 属性 -> 勾选"解除锁定"
echo 2. 使用install.bat安装程序
echo 3. 参考README.txt中的详细说明
echo.
pause
