# ToothMen 文档网站快速指南

## ⚡ 5分钟快速更新

### 场景1: 添加新文档
```bash
# 1. 创建文档
echo "---" > docs/NEW-$(date +%Y%m%d)-描述.mdx
echo "title: NEW-$(date +%Y%m%d)-描述" >> docs/NEW-$(date +%Y%m%d)-描述.mdx
echo "sidebar_position: 3" >> docs/NEW-$(date +%Y%m%d)-描述.mdx
echo "---" >> docs/NEW-$(date +%Y%m%d)-描述.mdx
echo "" >> docs/NEW-$(date +%Y%m%d)-描述.mdx
echo "# 新文档标题" >> docs/NEW-$(date +%Y%m%d)-描述.mdx

# 2. 更新侧边栏 (编辑 sidebars.js)
# 添加新文档到 tutorialSidebar 数组

# 3. 本地测试
npm run build

# 4. 推送部署
git add .
git commit -m "添加新文档"
git push origin master
```

### 场景2: 更新现有文档
```bash
# 1. 编辑文档
# 修改 docs/NEW-26040801-补丁.mdx 或 docs/NEW-260400901-补丁.mdx

# 2. 本地测试
npm run build

# 3. 推送部署
git add .
git commit -m "更新文档内容"
git push origin master
```

### 场景3: 修改配置
```bash
# 1. 编辑配置文件
# - docusaurus.config.js (主配置)
# - sidebars.js (侧边栏)
# - src/css/custom.css (样式)

# 2. 测试
npm run build
npm run serve

# 3. 部署
git add .
git commit -m "更新配置"
git push origin master
```

## 🎯 常用操作速查

### 文档 frontmatter 模板
```yaml
---
title: 文档标题
description: 文档描述
sidebar_position: 1  # 显示顺序
---
```

### 侧边栏配置模板
```javascript
{
  type: 'doc',
  id: '文档ID',      // 与文件名一致（不含扩展名）
  label: '显示名称',  // 侧边栏显示的名称
}
```

### Markdown 增强语法
```markdown
# 标题
## 二级标题

**粗体** *斜体*

- 列表项1
- 列表项2

1. 有序列表1
2. 有序列表2

`行内代码`

```代码块
console.log('Hello');
```

[链接文本](https://example.com)

![图片描述](/img/image.png)
```

## 🚨 紧急修复

### 构建失败时
```bash
# 1. 清除缓存
npm run clear

# 2. 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 3. 重新构建
npm run build
```

### 部署失败时
1. 检查 Cloudflare Pages 构建日志
2. 回滚到上一个可用版本
3. 手动触发重新构建

## 📱 移动端优化提示

### 图片优化
- 使用适当尺寸的图片
- 添加 alt 描述
- 考虑使用 WebP 格式

### 内容结构
- 使用清晰的标题层级
- 段落不宜过长
- 重要内容放在前面

## 🔄 工作流总结

```
编写文档 → 本地测试 → 提交代码 → 自动部署 → 验证上线
    ↓          ↓          ↓          ↓          ↓
  .mdx文件   npm build   git push   Cloudflare  访问网站
```

## ⏱️ 时间预估
- **小更新**: 2-5分钟
- **中更新**: 5-15分钟  
- **大更新**: 15-30分钟
- **部署时间**: 3-5分钟（Cloudflare 自动化）

## 📞 紧急联系
- **技术问题**: 查看 DEPLOYMENT.md
- **部署问题**: Cloudflare Pages 仪表板
- **代码问题**: GitHub 仓库 Issues

---

**提示**: 每次更新前建议先运行 `npm run build` 测试构建是否成功。