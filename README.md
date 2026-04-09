# ToothMen 文档网站

基于 Docusaurus 构建的专业文档网站，部署在 Cloudflare Pages，使用自定义域名 `docs.toothmen.com`。

## 🎯 项目状态

✅ **在线访问**: https://docs.toothmen.com  
✅ **自动化部署**: GitHub → Cloudflare Pages  
✅ **自定义域名**: docs.toothmen.com  
✅ **SSL 证书**: 已启用  
✅ **文档数量**: 3 个（可扩展）

## 📚 当前文档

1. **NEW-26040801-补丁** - 系统概述和快速开始
2. **NEW-26040901-补丁** - 详细功能说明
3. **NEW-26040902** - 最新更新内容

## 🚀 快速开始

### 环境要求
- Node.js 18+
- npm 或 yarn

### 安装依赖
```bash
npm install
```

### 本地开发
```bash
npm start
```
访问 http://localhost:3000

### 生产构建
```bash
npm run build
```

### 本地预览构建结果
```bash
npm run serve
```

## 🔗 相关资源

### 访问地址
- **主站**: https://docs.toothmen.com
- **文档1**: https://docs.toothmen.com/docs/NEW-26040801-补丁
- **文档2**: https://docs.toothmen.com/docs/NEW-260400901-补丁

### 管理界面
- **GitHub 仓库**: https://github.com/juemin7-star/toothmen-docs
- **Cloudflare Pages**: https://dash.cloudflare.com/

### 文档指南
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 完整部署指南
- [QUICK-START.md](./QUICK-START.md) - 快速操作指南

## 🏗️ 技术架构

- **框架**: Docusaurus v3
- **部署**: Cloudflare Pages
- **CDN**: Cloudflare 全球网络
- **域名**: Cloudflare 管理
- **自动化**: GitHub 推送触发部署

## 📁 项目结构
```
ToothMen-Docs-Simple/
├── docs/                    # 文档内容
├── src/                    # 源代码
├── static/                # 静态资源
├── sidebars.js           # 侧边栏配置
├── docusaurus.config.js  # 主配置
└── package.json          # 依赖管理
```

## 🔄 工作流程

1. **编写文档** → 在 `docs/` 目录创建 `.mdx` 文件
2. **更新侧边栏** → 编辑 `sidebars.js`
3. **本地测试** → `npm run build`
4. **提交代码** → `git add . && git commit -m "更新"`
5. **推送部署** → `git push origin master`
6. **自动部署** → Cloudflare Pages 构建并发布

## 📞 支持

- **部署问题**: 查看 [DEPLOYMENT.md](./DEPLOYMENT.md)
- **快速操作**: 查看 [QUICK-START.md](./QUICK-START.md)
- **技术文档**: [Docusaurus 官方文档](https://docusaurus.io/)

---

**最后更新**: 2024-12-01  
**版本**: v1.0.0  
**维护**: ToothMen 技术团队
