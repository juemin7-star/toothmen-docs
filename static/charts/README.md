# 图表目录说明

此目录用于存放文档中使用的图表文件。

## 支持的图表类型

### 1. 矢量图表 (推荐)
- **SVG** - 最佳选择，无限缩放不失真
- **PDF** - 高质量矢量图

### 2. 位图图表
- **PNG** - 无损压缩，支持透明
- **JPG** - 有损压缩，适合复杂图表

### 3. 数据可视化
- 性能对比图
- 趋势分析图
- 统计分布图
- 流程图
- 架构图

## 创建图表的工具推荐

### 免费工具
1. **Draw.io** - 在线流程图工具，支持导出SVG
2. **Excalidraw** - 手绘风格图表工具
3. **Google Charts** - 数据可视化库
4. **Chart.js** - JavaScript图表库

### 专业工具
1. **Microsoft Visio** - 专业图表工具
2. **Lucidchart** - 在线图表工具
3. **Adobe Illustrator** - 矢量图形设计

## 图表设计指南

### 颜色规范
- 使用品牌色系：主色、辅助色、强调色
- 确保足够的对比度
- 避免使用过多颜色

### 字体规范
- 使用系统字体或Web安全字体
- 标题：14-16px
- 正文：12-14px
- 标签：10-12px

### 布局规范
- 保持一致的边距和间距
- 使用网格对齐
- 添加清晰的图例和标签

## 示例图表命名

```
[图表类型]-[描述]-[版本].[扩展名]
```

**示例：**
- `flowchart-profile-system-v2.svg`
- `performance-comparison-2024Q1.png`
- `architecture-system-overview.pdf`

## 在MDX中使用图表

### 基本用法
```markdown
![系统架构图](/charts/architecture-system-overview.svg)
```

### 带样式的图表
```markdown
<div style={{textAlign: 'center', backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px'}}>
  <img 
    src="/charts/performance-comparison.png" 
    alt="性能对比图表"
    width="900"
    style={{maxWidth: '100%', height: 'auto'}}
  />
  <p style={{marginTop: '15px', color: '#495057', fontStyle: 'italic'}}>
    图1：各项功能性能优化对比（2024年第一季度）
  </p>
</div>
```

### 响应式图表
```markdown
<img 
  src="/charts/responsive-flowchart.svg" 
  alt="响应式流程图"
  style={{width: '100%', maxWidth: '800px', height: 'auto', margin: '0 auto', display: 'block'}}
/>
```

## 最佳实践

1. **优先使用SVG格式** - 更好的缩放性和文件大小
2. **添加alt文本** - 提高可访问性
3. **保持简洁** - 避免图表过于复杂
4. **使用一致的样式** - 保持品牌一致性
5. **测试不同尺寸** - 确保在移动设备上可读

## 工具使用示例

### Draw.io 导出设置
1. 文件 → 导出为 → SVG
2. 勾选"包含复制到剪贴板的工具提示"
3. 取消勾选"包含阴影"
4. 设置边距为10px

### 颜色代码参考
```css
/* 品牌色 */
--primary-color: #007bff;    /* 蓝色 */
--secondary-color: #6c757d;  /* 灰色 */
--success-color: #28a745;    /* 绿色 */
--warning-color: #ffc107;    /* 黄色 */
--danger-color: #dc3545;     /* 红色 */
```