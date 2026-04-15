// 由「生成侧边栏」根据 docs/ 与 sort_config.json 生成；可手改，下次生成会覆盖。
// 文档 id 与磁盘路径一致：文件夹名/文件名（无扩展名）。
const sidebars = {
  installSidebar: [
    'install/index',
  ],
  updateSidebar: [
    'cloud/registration',
    'cloud/special',
  ],
  tutorialSidebar: [
    'tutorial/index',
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