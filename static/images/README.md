# 图片目录说明

此目录用于存放文档中使用的图片文件。

## 目录结构建议

```
images/
├── screenshots/          # 系统截图
│   ├── dashboard/        # 仪表板截图
│   ├── profile-system/   # 剖面系统截图
│   └── tools/           # 工具界面截图
├── diagrams/            # 架构图、流程图
│   ├── system-architecture/  # 系统架构图
│   ├── workflow/        # 工作流程图
│   └── data-flow/       # 数据流程图
├── charts/              # 数据图表
│   ├── performance/     # 性能图表
│   ├── comparison/      # 对比图表
│   └── statistics/      # 统计图表
└── icons/               # 图标文件
    ├── features/        # 功能图标
    ├── tools/           # 工具图标
    └── status/          # 状态图标
```

## 命名规范

建议使用以下命名格式：

```
[功能]-[描述]-[日期].[扩展名]
```

**示例：**
- `profile-system-architecture-20240409.png`
- `dashboard-overview-screenshot.jpg`
- `performance-comparison-chart.svg`

## 图片规格建议

| 用途 | 推荐宽度 | 推荐格式 | 压缩要求 |
|------|----------|----------|----------|
| 界面截图 | 800-1200px | PNG/JPG | 质量80%以上 |
| 架构图 | 600-800px | SVG/PNG | 无损压缩 |
| 数据图表 | 600-800px | SVG/PNG | 无损压缩 |
| 图标 | 32-64px | SVG/PNG | 无损压缩 |

## 使用示例

在MDX文件中引用图片：

```markdown
![系统仪表板截图](/images/screenshots/dashboard/main-dashboard.png)
```

```markdown
<img 
  src="/images/diagrams/system-architecture/profile-system.svg" 
  alt="剖面系统架构图"
  width="800"
/>
```