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

  // Production URL - 使用您的自定义域名
url: 'https://toothmen.com',
baseUrl: '/',

  // GitHub pages deployment config - 请替换为您的信息
organizationName: 'juemin7-star',
projectName: 'toothmen-docs',
trailingSlash: false,

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

  // 添加插件
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        // 在开发模式下也启用重定向
        createRedirects: function(routePath) {
          // 这里可以添加动态重定向逻辑
          // 返回undefined表示不创建重定向
          return undefined;
        },
        redirects: [
          // 防止重定向到不存在的文档
          {
            from: '/docs/NEW-26040801-补丁',
            to: '/',
          },
          // 中文文档重定向：从旧URL（文件夹/文件名）到新URL（完整路径）
          // 未编码版本
          {
            from: '/docs/主程序安装/主程序安装说明',
            to: '/docs/安装教程/main-program-installation-guide',
          },
          {
            from: '/docs/云更新服务/云更新服务注册说明',
            to: '/docs/云更新服务说明/cloud-update-service-registration-guide',
          },
          {
            from: '/docs/云更新服务/注册规则特殊说明',
            to: '/docs/云更新服务说明/special-registration-rules',
          },
          {
            from: '/docs/补丁更新日志/NEW-26040101',
            to: '/docs/补丁更新日志/patch-new-26040101',
          },
          {
            from: '/docs/补丁更新日志/NEW-26040902',
            to: '/docs/补丁更新日志/patch-new-26040902',
          },
          // URL编码版本
          {
            from: '/docs/%E4%B8%BB%E7%A8%8B%E5%BA%8F%E5%AE%89%E8%A3%85/%E4%B8%BB%E7%A8%8B%E5%BA%8F%E5%AE%89%E8%A3%85%E8%AF%B4%E6%98%8E',
            to: '/docs/%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B/main-program-installation-guide',
          },
          {
            from: '/docs/%E4%BA%91%E6%9B%B4%E6%96%B0%E6%9C%8D%E5%8A%A1/%E4%BA%91%E6%9B%B4%E6%96%B0%E6%9C%8D%E5%8A%A1%E6%B3%A8%E5%86%8C%E8%AF%B4%E6%98%8E',
            to: '/docs/%E4%BA%91%E6%9B%B4%E6%96%B0%E6%9C%8D%E5%8A%A1%E8%AF%B4%E6%98%8E/cloud-update-service-registration-guide',
          },
          {
            from: '/docs/%E4%BA%91%E6%9B%B4%E6%96%B0%E6%9C%8D%E5%8A%A1/%E6%B3%A8%E5%86%8C%E8%A7%84%E5%88%99%E7%89%B9%E6%AE%8A%E8%AF%B4%E6%98%8E',
            to: '/docs/%E4%BA%91%E6%9B%B4%E6%96%B0%E6%9C%8D%E5%8A%A1%E8%AF%B4%E6%98%8E/special-registration-rules',
          },
          {
            from: '/docs/%E8%A1%A5%E4%B8%81%E6%97%A5%E5%BF%97/NEW-26040101',
            to: '/docs/%E8%A1%A5%E4%B8%81%E6%9B%B4%E6%96%B0%E6%97%A5%E5%BF%97/patch-new-26040101',
          },
          {
            from: '/docs/%E8%A1%A5%E4%B8%81%E6%97%A5%E5%BF%97/NEW-26040902',
            to: '/docs/%E8%A1%A5%E4%B8%81%E6%9B%B4%E6%96%B0%E6%97%A5%E5%BF%97/patch-new-26040902',
          },

        ],
      },
    ],
    [
      '@easyops-cn/docusaurus-search-local',
      {
        // 中文搜索支持
        language: ['en', 'zh'],
        // 忽略文件
        ignoreFiles: ['**/node_modules/**', '**/__tests__/**'],
        // 中文搜索优化 - 只使用已知支持的选项
        hashed: true,
        // 搜索结果数量
        searchResultLimits: 10,
      },
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
            docId: '安装教程/main-program-installation-guide',
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
      // Algolia DocSearch 配置（已禁用，使用本地搜索）
      // algolia: {
      //   // Algolia 应用ID
      //   appId: 'YOUR_APP_ID',
      //   // 公开API密钥：可以安全提交到代码库
      //   apiKey: 'YOUR_SEARCH_API_KEY',
      //   // 索引名称
      //   indexName: 'YOUR_INDEX_NAME',
      //   // 搜索参数
      //   searchParameters: {},
      //   // 搜索页面路径
      //   searchPagePath: 'search',
      //   // 是否启用洞察功能
      //   insights: false,
      // },

    }),
};

export default config;