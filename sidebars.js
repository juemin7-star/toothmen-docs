// 由「生成侧边栏」根据 docs/ 与 sort_config.json 生成；可手改，下次生成会覆盖。
// 文档 id 与磁盘路径一致：文件夹名/文件名（无扩展名）。
const sidebars = {
  installSidebar: [
    'install/install',
    {
      type: 'category',
      label: '硬件要求',
      items: [
        'install/硬件要求/电脑硬件要求',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: '黑金版安装流程',
      items: [
        'install/黑金版安装流程/ToothMen-Dentipro-黑金版安装总流程',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: '社区版安装流程',
      items: [
        'install/社区版安装流程/ToothMen-Dentipro-社区版安装总流程',
      ],
      collapsed: false,
    },
  ],
  updateSidebar: [
    'cloud/cloud',
    {
      type: 'category',
      label: '常规注册说明',
      items: [
        'cloud/常规注册说明/注册流程',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: '注册限流或封禁规则',
      items: [
        'cloud/注册限流或封禁规则/限流与封禁规则',
      ],
      collapsed: false,
    },
  ],
  tutorialSidebar: [
    'tutorial/tutorial',
    {
      type: 'category',
      label: '软件基础教程',
      items: [
        'tutorial/软件基础教程/软件基础教程',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Ai颌骨提取教程',
      items: [
        'tutorial/Ai颌骨提取教程/Ai颌骨提取教程',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: '3D钛网教程',
      items: [
        'tutorial/3D钛网教程/3D钛网教程',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: '组合导板教程',
      items: [
        'tutorial/组合导板教程/组合导板教程',
      ],
      collapsed: false,
    },
  ],
  changelogSidebar: [
    'changelog/changelog',
    {
      type: 'category',
      label: '2026',
      items: [
        'changelog/2026/20260327',
        'changelog/2026/20260321',
        'changelog/2026/20260314',
        'changelog/2026/20260309',
        'changelog/2026/20260107',
        'changelog/2026/20260228',
        'changelog/2026/20260117',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: '2025',
      items: [
        'changelog/2025/20251229',
        'changelog/2025/20251228',
        'changelog/2025/20251223',
        'changelog/2025/20251220',
      ],
      collapsed: false,
    },
  ],
};

export default sidebars;