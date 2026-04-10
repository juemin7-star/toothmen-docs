# 修复版程序复制脚本
Write-Host "ToothMen文档管理系统 - 修复版程序复制" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 停止正在运行的程序
Write-Host "1. 停止正在运行的程序..." -ForegroundColor Yellow
taskkill /f /im ToothMenDocsManager_v2_with_debug.exe >nul 2>&1
Start-Sleep -Seconds 2

# 2. 检查dist目录中的修复版程序
Write-Host "2. 检查dist目录中的修复版程序..." -ForegroundColor Yellow
if (Test-Path "dist\ToothMenDocsManager_v2_with_debug.exe") {
    Write-Host "   ✅ 找到修复版程序文件" -ForegroundColor Green
} else {
    Write-Host "   ❌ 找不到修复版程序文件" -ForegroundColor Red
    Write-Host "   请先运行打包命令" -ForegroundColor Yellow
    pause
    exit 1
}

# 3. 复制修复版程序到disc目录
Write-Host "3. 复制修复版程序到disc目录..." -ForegroundColor Yellow
try {
    Copy-Item -Path "dist\ToothMenDocsManager_v2_with_debug.exe" -Destination "disc\ToothMenDocsManager_v2_with_debug.exe" -Force
    Write-Host "   ✅ 修复版程序已复制" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 复制失败，文件可能被占用" -ForegroundColor Red
    Write-Host "   请手动关闭程序后重试" -ForegroundColor Yellow
    pause
    exit 1
}

# 4. 显示文件信息
Write-Host "4. 显示文件信息..." -ForegroundColor Yellow
$file = Get-Item "disc\ToothMenDocsManager_v2_with_debug.exe"
Write-Host "   文件名: $($file.Name)" -ForegroundColor White
Write-Host "   文件大小: $($file.Length) 字节" -ForegroundColor White
Write-Host "   修改时间: $($file.LastWriteTime)" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "修复版程序复制完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ 修复内容：" -ForegroundColor Green
Write-Host "   1. 修复MDX检测错误：使用for循环遍历MDX文件" -ForegroundColor White
Write-Host "   2. 使用check_single_file方法检测单个文件" -ForegroundColor White
Write-Host "   3. 文件夹结构默认展开" -ForegroundColor White
Write-Host "   4. 加大文件树左侧按钮" -ForegroundColor White
Write-Host "   5. 右侧有上下滑块控制" -ForegroundColor White
Write-Host "   6. 操作日志有滚动条" -ForegroundColor White
Write-Host "   7. 调试工具在日志右侧" -ForegroundColor White
Write-Host ""

Write-Host "🚀 现在可以测试MDX语法检测功能：" -ForegroundColor Cyan
Write-Host "   1. 点击'🔍 检测MDX语法'按钮" -ForegroundColor White
Write-Host "   2. 应该不再出现错误" -ForegroundColor White
Write-Host "   3. 正常显示检测结果" -ForegroundColor White
Write-Host ""

Write-Host "按任意键启动修复版程序..." -ForegroundColor Yellow
pause

Write-Host ""
Write-Host "正在启动修复版程序..." -ForegroundColor Cyan
Start-Process "disc\ToothMenDocsManager_v2_with_debug.exe"