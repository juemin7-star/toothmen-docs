// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ToothMen Documentation',
  tagline: 'Professional Dental Management Solution',
  favicon: 'img/favicon.ico',

  // Future flags
  future: {
    v4: true,
  },

  // Production URL - 请替换为您的域名
url: 'https://juemin7-star.github.io',
baseUrl: '/toothmen-docs/',


  // GitHub pages deployment config - 请替换为您的信息
organizationName: 'juemin7-star',
projectName: 'toothmen-docs',

  onBrokenLinks: 'warn',

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false, // 禁用博客功能
        theme: {
          customCss: './src/css/custom.css',
        },
        // 启用搜索功能
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // 主题模式配置
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      // 导航栏 - 包含公司logo、名称和搜索
      navbar: {
        hideOnScroll: true,
        title: 'ToothMen',
        logo: {
          alt: 'ToothMen Logo',
          src: 'img/toothmen-logo.svg',
          srcDark: 'img/toothmen-logo-dark.svg',
          width: 32,
          height: 32,
        },
        items: [
          {
            type: 'doc',
            docId: 'intro',
            position: 'left',
            label: '文档',
          },
          {
            type: 'search',
            position: 'right',
          },
        ],
      },
      // 页脚
      footer: {
        style: 'dark',
        links: [],
        copyright: '© 2024 ToothMen Documentation',
      },
      // 侧边栏配置
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
      // 代码高亮主题
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      // Algolia DocSearch 配置
      algolia: {
        // Algolia 应用ID
        appId: 'YOUR_APP_ID',
        // 公开API密钥：可以安全提交到代码库
        apiKey: 'YOUR_SEARCH_API_KEY',
        // 索引名称
        indexName: 'YOUR_INDEX_NAME',
        // 搜索参数
        searchParameters: {},
        // 搜索页面路径
        searchPagePath: 'search',
        // 是否启用洞察功能
        insights: false,
      },

    }),
};

export default config;