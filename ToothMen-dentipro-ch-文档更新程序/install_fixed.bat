@echo off
chcp 65001 >nul
echo ========================================
echo   ToothMen文档管理系统 - 修复版安装程序
echo ========================================
echo.

echo 1. 停止正在运行的程序...
taskkill /f /im ToothMenDocsManager_v2_with_debug.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo 2. 检查dist目录中的修复版程序...
if exist "dist\ToothMenDocsManager_v2_with_debug.exe" (
    echo   ✅ 找到修复版程序文件
) else (
    echo   ❌ 找不到修复版程序文件
    echo   请先运行打包命令
    pause
    exit /b 1
)

echo 3. 复制修复版程序到disc目录...
copy "dist\ToothMenDocsManager_v2_with_debug.exe" "disc\ToothMenDocsManager_v2_with_debug.exe" /Y
if %errorLevel% equ 0 (
    echo   ✅ 修复版程序已复制
) else (
    echo   ❌ 复制失败，文件可能被占用
    echo   请手动关闭程序后重试
    pause
    exit /b 1
)

echo 4. 解除文件锁定属性...
powershell -Command "Unblock-File -Path 'disc\ToothMenDocsManager_v2_with_debug.exe'" >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✅ 文件锁定已解除
) else (
    echo   ⚠️ 解除锁定失败（可能需要管理员权限）
)

echo.
echo 5. 显示文件信息...
echo   文件名: ToothMenDocsManager_v2_with_debug.exe
for %%F in ("disc\ToothMenDocsManager_v2_with_debug.exe") do (
    echo   文件大小: %%~zF 字节
    echo   修改时间: %%~tF
)

echo.
echo ========================================
echo   修复版安装完成！
echo ========================================
echo.
echo ✅ 修复内容：
echo   1. 修复MDX检测错误：'MDXChecker' object has no attribute 'check_file'
echo   2. 使用正确的check_all_mdx_files方法
echo   3. 文件夹结构默认展开
echo   4. 加大文件树左侧按钮
echo   5. 右侧有上下滑块控制
echo   6. 操作日志有滚动条
echo   7. 调试工具在日志右侧
echo.
echo 🚀 现在可以测试MDX语法检测功能：
echo   1. 点击"🔍 检测MDX语法"按钮
echo   2. 应该不再出现错误
echo   3. 正常显示检测结果
echo.
echo 按任意键启动修复版程序...
pause >nul

echo.
echo 正在启动修复版程序...
start "" "disc\ToothMenDocsManager_v2_with_debug.exe"

exit /b 0