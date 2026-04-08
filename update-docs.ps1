# ToothMen 文档更新脚本
# 使用方法：.\update-docs.ps1 "提交信息"

param(
    [string]$CommitMessage = "更新文档"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ToothMen 文档网站更新工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查是否在正确目录
if (-not (Test-Path "docusaurus.config.js")) {
    Write-Host "错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 步骤1：显示当前状态
Write-Host "`n[1/5] 检查当前状态..." -ForegroundColor Yellow
git status

# 步骤2：构建网站
Write-Host "`n[2/5] 构建网站..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "构建失败！请检查错误信息" -ForegroundColor Red
    exit 1
}

Write-Host "构建成功！" -ForegroundColor Green

# 步骤3：本地测试
Write-Host "`n[3/5] 本地测试..." -ForegroundColor Yellow
Write-Host "启动本地服务器进行测试..." -ForegroundColor Gray
Write-Host "按 Ctrl+C 停止测试并继续" -ForegroundColor Gray

# 在后台启动服务器
$serverJob = Start-Job -ScriptBlock {
    cd $using:PWD
    npm run serve
}

# 等待2秒让服务器启动
Start-Sleep -Seconds 2

Write-Host "`n网站运行在：http://localhost:3000" -ForegroundColor Green
Write-Host "请打开浏览器检查网站是否正常" -ForegroundColor Gray

$choice = Read-Host "`n网站是否正常？(y/n)"
Stop-Job $serverJob
Remove-Job $serverJob

if ($choice -ne "y") {
    Write-Host "请修复问题后重新运行脚本" -ForegroundColor Red
    exit 1
}

# 步骤4：提交更改
Write-Host "`n[4/5] 提交更改..." -ForegroundColor Yellow
git add .

if ($CommitMessage -eq "更新文档") {
    $CommitMessage = Read-Host "请输入提交信息"
}

git commit -m $CommitMessage

# 步骤5：推送并部署
Write-Host "`n[5/5] 推送并部署..." -ForegroundColor Yellow
git push origin main

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ 更新完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n部署进度：" -ForegroundColor Cyan
Write-Host "1. 代码已推送到 GitHub" -ForegroundColor Gray
Write-Host "2. GitHub Actions 自动触发" -ForegroundColor Gray
Write-Host "3. 构建和部署约需 2-5 分钟" -ForegroundColor Gray
Write-Host "4. Cloudflare CDN 缓存更新约需 1-10 分钟" -ForegroundColor Gray
Write-Host "`n监控部署：" -ForegroundColor Cyan
Write-Host "• GitHub Actions: https://github.com/您的用户名/toothmen-docs/actions" -ForegroundColor Gray
Write-Host "• 访问网站: https://docs.toothmen.com" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Green