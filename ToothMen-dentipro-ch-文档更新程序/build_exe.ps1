#!/usr/bin/env pwsh
# ToothMen文档管理工具打包脚本
# 使用系统Python和PyInstaller打包为EXE

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { $Green }
        "WARNING" { $Yellow }
        "ERROR" { $Red }
        "INFO" { $Blue }
        default { $Reset }
    }
    
    Write-Host "$color[$timestamp] [$Level] $Message$Reset"
}

# 主函数
function Main {
    Write-Log "开始打包ToothMen文档管理工具" "INFO"
    Write-Log "=" * 60 "INFO"
    
    # 1. 检测系统Python
    Write-Log "步骤1: 检测系统Python" "INFO"
    $systemPython = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    
    if (-not (Test-Path $systemPython)) {
        Write-Log "系统Python未找到，尝试安装..." "WARNING"
        
        # 尝试安装Python 3.12
        try {
            winget install Python.Python.3.12 --accept-package-agreements
            Write-Log "Python安装成功" "SUCCESS"
        } catch {
            Write-Log "Python安装失败，请手动安装Python 3.12" "ERROR"
            exit 1
        }
        
        # 重新检查
        if (-not (Test-Path $systemPython)) {
            Write-Log "Python安装后仍未找到，请检查安装" "ERROR"
            exit 1
        }
    }
    
    # 2. 验证不是Blender Python
    Write-Log "步骤2: 验证Python来源" "INFO"
    if ($systemPython -match "Blender") {
        Write-Log "【致命错误】检测到Blender Python！" "ERROR"
        Write-Log "请使用系统Python：$systemPython" "ERROR"
        exit 1
    }
    
    Write-Log "Python验证通过: $systemPython" "SUCCESS"
    
    # 3. 检查PyInstaller
    Write-Log "步骤3: 检查PyInstaller" "INFO"
    $pyinstallerPath = "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\pyinstaller.exe"
    
    if (-not (Test-Path $pyinstallerPath)) {
        Write-Log "PyInstaller未安装，开始安装..." "WARNING"
        
        # 安装PyInstaller
        try {
            & $systemPython -m pip install pyinstaller
            Write-Log "PyInstaller安装成功" "SUCCESS"
        } catch {
            Write-Log "PyInstaller安装失败" "ERROR"
            exit 1
        }
    }
    
    Write-Log "PyInstaller已就绪: $pyinstallerPath" "SUCCESS"
    
    # 4. 创建spec文件
    Write-Log "步骤4: 创建PyInstaller spec文件" "INFO"
    $specContent = @"
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ToothMenDocsManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 如果有图标文件
)
"@
    
    $specPath = "toothmen_docs_manager.spec"
    Set-Content -Path $specPath -Value $specContent -Encoding UTF8
    Write-Log "Spec文件创建成功: $specPath" "SUCCESS"
    
    # 5. 执行打包
    Write-Log "步骤5: 开始打包为EXE" "INFO"
    Write-Log "这可能需要几分钟时间..." "INFO"
    
    try {
        & $pyinstallerPath $specPath --noconfirm --clean
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "打包成功完成！" "SUCCESS"
        } else {
            Write-Log "打包失败，退出代码: $LASTEXITCODE" "ERROR"
            exit 1
        }
    } catch {
        Write-Log "打包过程中出现错误: $_" "ERROR"
        exit 1
    }
    
    # 6. 复制到disc目录
    Write-Log "步骤6: 复制EXE到disc目录" "INFO"
    
    $distExe = "dist\ToothMenDocsManager.exe"
    $discDir = "disc"
    
    if (Test-Path $distExe) {
        # 确保disc目录存在
        if (-not (Test-Path $discDir)) {
            New-Item -ItemType Directory -Path $discDir | Out-Null
        }
        
        # 复制文件
        Copy-Item -Path $distExe -Destination "$discDir\" -Force
        
        # 复制配置文件
        Copy-Item -Path "config.json" -Destination "$discDir\" -Force
        Copy-Item -Path "README.md" -Destination "$discDir\" -Force
        
        Write-Log "EXE文件已复制到: $discDir\ToothMenDocsManager.exe" "SUCCESS"
        
        # 显示文件信息
        $exeInfo = Get-Item "$discDir\ToothMenDocsManager.exe"
        Write-Log "文件大小: $([math]::Round($exeInfo.Length / 1MB, 2)) MB" "INFO"
        Write-Log "创建时间: $($exeInfo.CreationTime)" "INFO"
    } else {
        Write-Log "未找到生成的EXE文件: $distExe" "ERROR"
        exit 1
    }
    
    # 7. 清理临时文件
    Write-Log "步骤7: 清理临时文件" "INFO"
    
    $tempFiles = @("build", "dist", "__pycache__", "*.spec")
    
    foreach ($pattern in $tempFiles) {
        if (Test-Path $pattern) {
            Remove-Item -Path $pattern -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Log "临时文件清理完成" "SUCCESS"
    
    # 8. 完成
    Write-Log "=" * 60 "INFO"
    Write-Log "打包流程完成！" "SUCCESS"
    Write-Log "" "INFO"
    Write-Log "生成的EXE文件位置:" "INFO"
    Write-Log "  $discDir\ToothMenDocsManager.exe" "INFO"
    Write-Log "" "INFO"
    Write-Log "使用方法:" "INFO"
    Write-Log "  1. 双击运行 ToothMenDocsManager.exe" "INFO"
    Write-Log "  2. 确保项目路径配置正确" "INFO"
    Write-Log "  3. 开始管理您的文档" "INFO"
    Write-Log "" "INFO"
    Write-Log "注意: 首次运行可能需要管理员权限" "WARNING"
}

# 执行主函数
try {
    Main
} catch {
    Write-Host "$Red[ERROR] 脚本执行失败: $_$Reset"
    exit 1
}