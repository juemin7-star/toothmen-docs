const sidebars = {
  installSidebar: [
    {
      type: 'category',
      label: '主程序安装',
      items: [
        'install/index',
      ],
      collapsed: true,
    },
  ],
  updateSidebar: [
    {
      type: 'category',
      label: '云更新服务说明',
      items: [
        'cloud/registration',
        'cloud/special',
      ],
      collapsed: true,
    },
  ],
  tutorialSidebar: [
    {
      type: 'category',
      label: '学习教程',
      items: [
        'tutorial/index',
      ],
      collapsed: true,
    },
  ],
  changelogSidebar: [
    {
      type: 'category',
      label: 'Denti-Pro 更新日志',
      items: [
        'changelog/index',
      {
        type: 'category',
        label: '2026年',
        items: [
          'changelog/2026/2026-04',
          'changelog/2026/2026-03',
        ],
        collapsed: true,
      },
      {
        type: 'category',
        label: '2025年',
        items: [
          'changelog/2025/2025-02',
          'changelog/2025/2025-01',
        ],
        collapsed: true,
      },
      ],
      collapsed: true,
    },
  ],
};

export default sidebars;