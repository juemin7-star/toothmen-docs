@echo off
echo ========================================
echo ToothMen文档网站更新和部署脚本
echo ========================================
echo.

REM 检查是否在正确目录
if not exist "package.json" (
    echo 错误：请在ToothMen-Docs-Simple目录下运行此脚本
    pause
    exit /b 1
)

echo 步骤1：停止正在运行的开发服务器
taskkill /F /IM node.exe 2>nul
echo.

echo 步骤2：构建项目
call npm run build
if %errorlevel% neq 0 (
    echo 构建失败！请检查错误信息
    pause
    exit /b 1
)
echo 构建成功！
echo.

echo 步骤3：本地测试（可选）
set /p test="是否启动本地测试服务器？(y/n): "
if /i "%test%"=="y" (
    echo 启动本地测试服务器...
    start cmd /k "npm start -- --port 3001"
    echo 测试服务器已启动：http://localhost:3001/
    echo 按任意键继续部署...
    pause >nul
)

echo.
echo 步骤4：部署到GitHub Pages
echo 注意：请确保已配置GitHub仓库和部署设置
set /p deploy="是否部署到GitHub Pages？(y/n): "
if /i "%deploy%"=="y" (
    echo 开始部署...
    call npm run deploy
    if %errorlevel% neq 0 (
        echo 部署失败！请检查错误信息
        pause
        exit /b 1
    )
    echo 部署成功！
    echo.
    echo 您的网站已发布到：
    echo - GitHub Pages: https://your-username.github.io/toothmen-docs/
    echo - 文档页面: https://your-username.github.io/toothmen-docs/docs/intro
) else (
    echo 跳过部署步骤
)

echo.
echo 步骤5：完成
echo 更新流程已完成！
echo.
echo 重要提醒：
echo 1. 如果使用自定义域名，请更新docusaurus.config.js中的url配置
echo 2. 部署后可能需要几分钟才能生效
echo 3. 清除浏览器缓存以查看最新版本
echo.
pause