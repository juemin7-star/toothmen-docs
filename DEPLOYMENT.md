# ToothMen 文档网站部署指南

## 📋 项目概述
这是一个基于 Docusaurus 的文档网站，部署在 Cloudflare Pages，使用自定义域名 `docs.toothmen.com`。

## 🚀 当前部署状态

### 访问地址
- **主站**: https://docs.toothmen.com
- **文档1**: https://docs.toothmen.com/docs/NEW-26040801-补丁
- **文档2**: https://docs.toothmen.com/docs/NEW-260400901-补丁

### 技术栈
- **框架**: Docusaurus v3
- **部署**: Cloudflare Pages
- **域名**: docs.toothmen.com (Cloudflare 管理)
- **仓库**: https://github.com/juemin7-star/toothmen-docs

## 🔧 部署架构

### DNS 配置
```
toothmen.com:
  - @ → public.r2.dev (R2 存储桶)
  - docs → toothmen-docs.pages.dev (Pages 文档站)
```

### 自动化流程
```
本地修改 → 推送 GitHub → Cloudflare 自动构建 → 全球 CDN 部署
```

## 📝 添加/更新文档流程

### 1. 创建新文档
```bash
# 在 docs/ 目录创建 .mdx 文件
docs/NEW-YYYYMMDD-描述.mdx
```

### 2. 更新侧边栏
编辑 `sidebars.js`:
```javascript
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'NEW-26040801-补丁',
      label: 'NEW-26040801-补丁',
    },
    {
      type: 'doc',
      id: 'NEW-260400901-补丁',
      label: 'NEW-260400901-补丁',
    },
    // 添加新文档
    {
      type: 'doc',
      id: 'NEW-YYYYMMDD-描述',
      label: 'NEW-YYYYMMDD-描述',
    },
  ],
};
```

### 3. 设置文档顺序
在文档 frontmatter 中添加:
```yaml
---
title: NEW-YYYYMMDD-描述
sidebar_position: 3  # 控制显示顺序
---
```

### 4. 本地测试
```bash
npm run build    # 构建测试
npm run serve    # 本地预览
```

### 5. 推送部署
```bash
git add .
git commit -m "添加新文档: NEW-YYYYMMDD-描述"
git push origin master
```

## ⚙️ 本地开发

### 环境要求
- Node.js 18+
- npm 或 yarn

### 常用命令
```bash
npm install          # 安装依赖
npm start            # 开发模式 (http://localhost:3000)
npm run build        # 生产构建
npm run serve        # 本地预览构建结果
npm run clear        # 清除缓存
```

## 🏗️ 项目结构
```
ToothMen-Docs-Simple/
├── docs/                    # 文档内容
│   ├── NEW-26040801-补丁.mdx
│   └── NEW-260400901-补丁.mdx
├── src/                    # 源代码
│   ├── components/        # 组件
│   ├── css/              # 样式
│   └── pages/            # 页面
├── static/                # 静态资源
│   └── img/              # 图片
├── sidebars.js           # 侧边栏配置
├── docusaurus.config.js  # 主配置文件
├── package.json          # 依赖配置
└── README.md            # 项目说明
```

## 🔍 故障排除

### 构建失败
1. 检查 `npm run build` 错误信息
2. 清除缓存: `npm run clear`
3. 检查文档 frontmatter 格式

### 部署失败
1. 查看 Cloudflare Pages 构建日志
2. 检查 GitHub 仓库权限
3. 验证 DNS 配置

### 访问问题
1. DNS 传播: 等待 5-30 分钟
2. SSL 证书: 等待 2-5 分钟
3. 浏览器缓存: Ctrl+F5 强制刷新

## 📊 监控和维护

### 监控地址
- **Cloudflare Pages**: https://dash.cloudflare.com/
- **GitHub 仓库**: https://github.com/juemin7-star/toothmen-docs
- **构建状态**: Cloudflare Pages 仪表板

### 定期维护
1. 更新 Docusaurus 版本
2. 检查依赖安全更新
3. 备份重要文档内容

## 🔗 相关链接
- [Docusaurus 文档](https://docusaurus.io/)
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [GitHub 仓库](https://github.com/juemin7-star/toothmen-docs)

---

**最后更新**: 2024-12-01  
**维护团队**: ToothMen 技术文档组  
**部署方式**: Cloudflare Pages 自动化部署