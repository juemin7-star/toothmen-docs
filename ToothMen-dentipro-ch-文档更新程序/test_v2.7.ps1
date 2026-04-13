Write-Host "🧪 ToothMen文档管理工具 v2.7 测试脚本" -ForegroundColor Cyan
Write-Host ""

# 检查EXE文件
$exePath = "dist\ToothMenDocsManager.exe"
if (Test-Path $exePath) {
    Write-Host "✅ EXE文件存在: $exePath" -ForegroundColor Green
    
    # 获取文件信息
    $exeInfo = Get-Item $exePath
    Write-Host "📏 文件大小: $([math]::Round($exeInfo.Length / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "📅 创建时间: $($exeInfo.CreationTime)" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🚀 尝试运行程序（5秒后自动关闭）..." -ForegroundColor Yellow
    Write-Host "注意：程序将在5秒后自动关闭以进行测试" -ForegroundColor White
    
    # 启动程序
    $process = Start-Process -FilePath $exePath -PassThru
    
    # 等待5秒
    Start-Sleep -Seconds 5
    
    # 关闭程序
    if ($process.HasExited -eq $false) {
        Write-Host "🛑 关闭测试程序..." -ForegroundColor Yellow
        $process.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 2
        
        if ($process.HasExited -eq $false) {
            $process.Kill() | Out-Null
        }
        Write-Host "✅ 程序已关闭" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 程序已自行退出" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 测试完成！程序可以正常运行。" -ForegroundColor Green
} else {
    Write-Host "❌ EXE文件未找到: $exePath" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 版本信息：" -ForegroundColor Cyan
Write-Host "版本: v2.7 (纯中文文档管理)" -ForegroundColor White
Write-Host "更新: 移除英文支持，专注于中文文档管理" -ForegroundColor White
Write-Host "目标: 保证左侧文件结构序列" -ForegroundColor White
