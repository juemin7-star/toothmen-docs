@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档管理系统 - 测试运行
echo ========================================
echo.
echo 这个脚本将测试程序是否能正常运行。
echo 如果出现Windows Defender警告，请选择"更多信息" -> "仍要运行"
echo.

REM 检查文件是否存在
if not exist "disc\ToothMenDocsManager.exe" (
    echo ❌ 错误: 找不到 disc\ToothMenDocsManager.exe
    echo 请确保程序已正确打包。
    pause
    exit /b 1
)

echo ✅ 程序文件找到: disc\ToothMenDocsManager.exe
echo.

REM 显示文件信息
for %%F in ("disc\ToothMenDocsManager.exe") do (
    echo 文件大小: %%~zF 字节 (约 %%~zF / 1048576 MB)
    echo 修改时间: %%~tF
)
echo.

echo 正在尝试运行程序...
echo 如果程序窗口出现，表示打包成功！
echo 程序将在10秒后自动关闭...
echo.

REM 运行程序
start "" "disc\ToothMenDocsManager.exe"

REM 等待10秒
timeout /t 10 /nobreak >nul

echo.
echo 检查程序是否在运行...
tasklist /fi "imagename eq ToothMenDocsManager.exe" | findstr ToothMenDocsManager.exe >nul
if %errorLevel% equ 0 (
    echo ✅ 程序正在运行！打包成功！
    echo.
    echo 现在可以：
    echo 1. 手动关闭程序窗口
    echo 2. 或运行 install.bat 进行完整安装
) else (
    echo ❌ 程序未运行
    echo.
    echo 可能的原因：
    echo 1. Windows Defender阻止了程序运行
    echo 2. 程序启动失败
    echo.
    echo 解决方案：
    echo 1. 右键点击 disc\ToothMenDocsManager.exe -> 属性 -> 勾选"解除锁定"
    echo 2. 运行 install.bat 安装程序
)

echo.
echo ========================================
echo  测试完成
echo ========================================
echo.
pause