# ToothMen文档快速更新指南

## 🚀 3分钟快速更新流程

### 前提条件
- 已配置GitHub仓库并完成首次部署
- 本地开发环境正常

### 快速更新步骤

#### 1. 编辑文档（1分钟）
- 打开文件：`docs\intro.mdx`
- 修改您需要更新的内容
- 保存文件

#### 2. 本地测试（30秒）
```bash
# 方法A：使用批处理脚本（最简单）
双击 UPDATE-AND-DEPLOY.bat

# 方法B：手动命令
npm run build
npm start
```

#### 3. 查看预览
- 打开浏览器访问：http://localhost:3001/docs/intro
- 确认修改正确

#### 4. 部署上线（1分钟）
```bash
# 提交更改
git add .
git commit -m "更新文档内容"

# 推送到GitHub
git push

# 部署到GitHub Pages
npm run deploy
```

## 📝 常用更新场景

### 场景1：更新文本内容
1. 直接编辑`intro.mdx`中的文本
2. 保存后本地预览
3. 部署上线

### 场景2：更新图片
1. 将新图片放入`static\img\`目录
2. 在`intro.mdx`中更新图片路径
3. 保存并部署

### 场景3：更新视频链接
1. 编辑`intro.mdx`中的视频iframe
2. 更新`src`属性为新的视频链接
3. 保存并部署

### 场景4：更新联系方式
1. 修改"联系我们"部分的电话、邮箱、地址
2. 保存并部署

## ⚡ 一键更新脚本

### 使用批处理脚本
1. 双击`UPDATE-AND-DEPLOY.bat`
2. 按照提示操作
3. 脚本会自动完成构建和部署

### 脚本功能
- 自动停止旧服务器
- 构建项目
- 可选本地测试
- 一键部署到GitHub Pages

## 🔧 配置更新

### 更新网站信息
编辑`docusaurus.config.js`：
```javascript
title: '新的网站标题',
tagline: '新的标语',
```

### 更新公司Logo
1. 替换`static\img\toothmen-logo.svg`
2. 替换`static\img\toothmen-logo-dark.svg`
3. 重新构建部署

### 更新导航栏
编辑`docusaurus.config.js`中的`navbar`配置：
```javascript
navbar: {
  title: '新的公司名称',
  // ... 其他配置
}
```

## 🌐 部署后检查

### 访问您的网站
- GitHub Pages：https://your-username.github.io/toothmen-docs/
- 自定义域名：https://docs.toothmen.com（如果已配置）

### 常见问题
1. **页面未更新**：清除浏览器缓存（Ctrl+F5）
2. **404错误**：检查`baseUrl`配置是否正确
3. **样式错乱**：确认构建成功，重新部署

## 📊 版本管理

### 创建新版本
```bash
# 创建v1.1.0版本
npm run docusaurus docs:version 1.1.0

# 提交并部署
git add .
git commit -m "发布v1.1.0"
git push
npm run deploy
```

### 版本切换
- 用户可以在右上角切换版本
- "Next"版本：正在开发的内容
- "v1.0.0"版本：已发布的稳定内容

## 🆘 紧急恢复

### 回滚到上一个版本
```bash
# 查看提交历史
git log --oneline

# 回滚到指定提交
git reset --hard <commit-hash>

# 强制推送到GitHub
git push -f origin main

# 重新部署
npm run deploy
```

### 恢复误删文件
```bash
# 从Git恢复文件
git checkout HEAD -- docs/intro.mdx
```

## 📞 快速帮助

### 本地开发问题
```bash
# 清理缓存
npm run clear

# 重新安装依赖
npm install

# 重新构建
npm run build
```

### 部署问题
1. 检查GitHub仓库设置
2. 确认`docusaurus.config.js`配置正确
3. 查看GitHub Actions日志

### 网络问题
- 确保网络连接正常
- GitHub Pages可能需要几分钟生效
- 使用CDN刷新工具（如cloudflare.com）

---

**记住**：所有内容都在`docs\intro.mdx`一个文件中，修改这个文件就是更新整个网站！

**更新频率建议**：
- 小更新：随时进行
- 大更新：创建新版本
- 定期备份：提交到GitHub

**最后提示**：部署后请等待2-5分钟让CDN缓存更新，然后清除浏览器缓存查看最新版本。