# ToothMen文档更新程序 - 使用说明

## 程序功能
这是一个用于管理ToothMen文档系统的桌面应用程序，主要功能包括：
- MDX语法检测和自动修复
- 侧边栏自动更新
- 本地构建测试
- 本地预览服务器
- 自动部署到Git和Cloudflare

## 解决Windows Defender SmartScreen警告

当您运行程序时，可能会看到Windows Defender SmartScreen的警告："Windows已保护你的电脑"。这是正常的，因为程序没有数字签名。

### 解决方案1：手动运行（推荐）
1. 右键点击 disc\ToothMenDocsManager.exe 文件
2. 选择"属性"
3. 在"常规"选项卡底部，找到"安全"部分
4. 勾选"解除锁定"复选框
5. 点击"应用"，然后点击"确定"
6. 现在可以正常运行程序了

### 解决方案2：使用安装程序（更安全）
1. 右键点击 install.bat 文件
2. 选择"以管理员身份运行"
3. 按照提示完成安装
4. 程序将被安装到 C:\Program Files\ToothMenDocsManager\
5. 桌面上会创建快捷方式

### 解决方案3：临时解决方案
1. 点击警告窗口中的"更多信息"
2. 点击"仍要运行"
3. 程序将正常启动

## 安装说明

### 使用安装脚本
1. 右键点击 install.bat
2. 选择"以管理员身份运行"
3. 等待安装完成

安装完成后，您可以在：
- 桌面：ToothMen文档更新程序.lnk
- 开始菜单：ToothMen > ToothMen文档更新程序

### 手动安装
1. 将 disc\ToothMenDocsManager.exe 复制到任意目录
2. 右键点击文件，选择"属性"
3. 勾选"解除锁定"
4. 创建快捷方式到桌面

## 卸载程序
1. 右键点击 uninstall.bat
2. 选择"以管理员身份运行"
3. 等待卸载完成

## 程序结构
- main.py - 主程序源代码
- mdx_checker.py - MDX语法检测器
- disc\ToothMenDocsManager.exe - 可执行文件
- install.bat - 安装脚本
- uninstall.bat - 卸载脚本

## 注意事项
1. 程序需要访问网络进行Git操作和Cloudflare部署
2. 首次运行可能需要配置文档路径
3. 确保系统已安装Python 3.12（仅用于开发，运行EXE不需要）

## 技术支持
如有问题，请检查日志输出或联系开发人员。

版本: 1.0.0
更新日期: 2026-04-09
