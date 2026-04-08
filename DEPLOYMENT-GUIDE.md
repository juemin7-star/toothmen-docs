# ToothMen文档网站部署指南

## 📋 项目概述
这是一个基于Docusaurus的极简文档网站，只包含一个文档文件(`intro.mdx`)，支持版本控制和主题切换。

## 🚀 快速部署步骤

### 前提条件
1. **GitHub账号**：如果没有，请先注册 https://github.com
2. **Node.js环境**：已安装Node.js 18+（项目已配置）
3. **Git客户端**：已安装Git

### 步骤1：创建GitHub仓库
1. 登录GitHub
2. 点击右上角"+" → "New repository"
3. 填写仓库信息：
   - Repository name: `toothmen-docs`（或其他名称）
   - Description: ToothMen Documentation Website
   - 选择Public（公开）
   - 不勾选"Initialize this repository with a README"
4. 点击"Create repository"

### 步骤2：配置本地项目
1. 打开`docusaurus.config.js`文件
2. 更新以下配置：
```javascript
// 第20-25行附近
url: 'https://your-username.github.io', // 替换为您的GitHub用户名
baseUrl: '/toothmen-docs/', // 替换为您的仓库名称

// 第27-29行附近
organizationName: 'your-github-username', // 替换为您的GitHub用户名
projectName: 'toothmen-docs', // 替换为您的仓库名称
```

### 步骤3：初始化Git并推送代码
```bash
# 进入项目目录
cd "d:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "初始提交：ToothMen文档网站"

# 添加远程仓库（替换your-username和repository-name）
git remote add origin https://github.com/your-username/toothmen-docs.git

# 推送代码
git push -u origin main
```

### 步骤4：部署到GitHub Pages
```bash
# 构建项目
npm run build

# 部署到GitHub Pages
npm run deploy
```

## 🌐 访问您的网站

### GitHub Pages地址
- **主站点**：https://your-username.github.io/toothmen-docs/
- **文档页面**：https://your-username.github.io/toothmen-docs/docs/intro

### 自定义域名（可选）
1. 购买域名（如：docs.toothmen.com）
2. 在域名注册商处添加CNAME记录：
   ```
   docs.toothmen.com CNAME your-username.github.io
   ```
3. 在GitHub仓库设置中启用自定义域名
4. 在`docusaurus.config.js`中更新`url`：
   ```javascript
   url: 'https://docs.toothmen.com',
   baseUrl: '/',
   ```

## 🔄 更新文档流程

### 日常更新步骤
1. **编辑文档**：
   - 打开并修改`docs/intro.mdx`文件
   - 本地预览：http://localhost:3001/docs/intro

2. **测试更改**：
   ```bash
   npm run build  # 构建测试
   npm start      # 本地预览
   ```

3. **提交并推送**：
   ```bash
   git add .
   git commit -m "更新文档内容"
   git push
   ```

4. **重新部署**：
   ```bash
   npm run deploy
   ```

### 创建新版本
当有重大更新时，可以创建新版本：
```bash
# 创建v1.1.0版本
npm run docusaurus docs:version 1.1.0

# 提交并推送
git add .
git commit -m "发布v1.1.0版本"
git push

# 部署
npm run deploy
```

## ⚙️ 配置说明

### 项目结构
```
ToothMen-Docs-Simple/
├── docs/intro.mdx          # 唯一文档文件（所有内容在这里）
├── docusaurus.config.js    # 主配置文件
├── sidebars.js            # 侧边栏配置
├── package.json           # 项目依赖
└── build/                 # 构建输出目录
```

### 关键配置项
1. **网站信息**：`docusaurus.config.js`中的`title`、`tagline`
2. **公司Logo**：替换`static/img/`目录下的logo文件
3. **导航栏**：`navbar`配置中的公司名称和菜单
4. **搜索功能**：需要配置Algolia API密钥（可选）

## 🔧 故障排除

### 常见问题
1. **构建失败**：
   ```bash
   # 清理缓存
   npm run clear
   # 重新安装依赖
   npm install
   # 重新构建
   npm run build
   ```

2. **部署失败**：
   - 检查GitHub Pages设置是否正确
   - 确认仓库是Public（公开）
   - 检查`docusaurus.config.js`中的URL配置

3. **页面404错误**：
   - 确认`baseUrl`配置正确
   - 检查GitHub Pages的发布分支（应为`gh-pages`）

### 本地开发
```bash
# 启动开发服务器
npm start

# 构建生产版本
npm run build

# 本地测试生产版本
npm run serve
```

## 📞 支持与帮助

### 文档资源
- Docusaurus官方文档：https://docusaurus.io
- GitHub Pages文档：https://pages.github.com
- Vercel文档：https://vercel.com/docs

### 问题反馈
如果在部署过程中遇到问题，请检查：
1. 控制台错误信息
2. GitHub Actions日志
3. 浏览器开发者工具控制台

## 🎯 最佳实践

### 文档维护
1. **定期备份**：定期提交代码到GitHub
2. **版本控制**：重要更新时创建新版本
3. **测试先行**：本地测试后再部署

### 性能优化
1. **图片优化**：压缩图片文件
2. **代码分割**：Docusaurus自动处理
3. **CDN加速**：使用GitHub Pages或Vercel的全球CDN

### 安全建议
1. **不提交敏感信息**：不要在代码中提交API密钥
2. **使用环境变量**：敏感配置使用环境变量
3. **定期更新**：保持依赖包更新到最新版本

---

**最后更新**：2024-12-01  
**维护团队**：ToothMen技术文档组  
**更新频率**：根据文档更新情况调整