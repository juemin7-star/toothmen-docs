// 由「生成侧边栏」根据 docs/ 与 sort_config.json 生成；可手改，下次生成会覆盖。
// 文档 id 与磁盘路径一致：文件夹名/文件名（无扩展名）。
const sidebars = {
  installSidebar: [
    {
      type: 'category',
      label: '硬件要求',
      items: [
        'install/硬件要求/电脑硬件要求',
      ],
      collapsed: true,
    },
    {
      type: 'category',
      label: '安装流程',
      items: [
        'install/安装流程/ToothMen-Dentipro安装总流程',
      ],
      collapsed: true,
    },
  ],
  updateSidebar: [
    {
      type: 'category',
      label: '常规注册说明',
      items: [
        'cloud/常规注册说明/注册流程',
      ],
      collapsed: true,
    },
    {
      type: 'category',
      label: '注册限流或封禁规则',
      items: [
        'cloud/注册限流或封禁规则/限流与封禁规则',
      ],
      collapsed: true,
    },
  ],
  tutorialSidebar: [
    {
      type: 'category',
      label: '软件基础教程',
      items: [
        'tutorial/软件基础教程/软件基础教程',
      ],
      collapsed: true,
    },
    {
      type: 'category',
      label: '3D钛网教程',
      items: [
        'tutorial/3D钛网教程/3D钛网教程',
      ],
      collapsed: true,
    },
    {
      type: 'category',
      label: 'Ai颌骨提取教程',
      items: [
        'tutorial/Ai颌骨提取教程/Ai颌骨提取教程',
      ],
      collapsed: true,
    },
  ],
  changelogSidebar: [
    {
      type: 'category',
      label: '2026',
      items: [
        'changelog/2026/2026-04',
        'changelog/2026/2026-03',
      ],
      collapsed: true,
    },
    {
      type: 'category',
      label: '2025',
      items: [
        'changelog/2025/2025-02',
        'changelog/2025/2025-01',
      ],
      collapsed: true,
    },
  ],
};

export default sidebars;