// @ts-check
// `@ts-check` 启用TypeScript类型检查（可选）

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ToothMen文档系统',
  tagline: 'ToothMen官方说明文档',
  favicon: 'img/favicon.ico',

  // 设置生产环境的URL
  url: 'https://your-docusaurus-site.example.com',
  // 设置基础URL路径（如果部署在子路径下）
  baseUrl: '/',

  // GitHub pages部署配置
  organizationName: 'toothmen', // 通常是你的GitHub用户名
  projectName: 'toothmen-docs', // 通常是你的仓库名

  onBrokenLinks: 'warn',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  // 即使你使用国际化的英文网站，也可以保留这个配置
  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // 如果需要，可以取消注释下面的配置
          // routeBasePath: '/', // 将docs设置为根路径
          // editUrl: 'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false, // 禁用博客功能
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // 替换为你的项目社交链接
      navbar: {
        title: 'ToothMen-DentiPro',
        logo: {
          alt: 'ToothMen Logo',
          src: 'img/toothmenlogo.png',
          href: '/docs',
        },
        items: [          {
            type: 'doc',
            docId: 'install/index',
            position: 'left',
            label: '总文档中心',
          },
          {
            type: 'doc',
            docId: 'changelog/index',
            position: 'left',
            label: '更新日志',
          },
          {
            type: 'search',
            position: 'right',
          },],
      },
      footer: {
        style: 'dark',
        logo: {
          alt: 'ToothMen Logo',
          src: 'img/toothmenlogo.png',
          width: 48,
          height: 48,
          href: '/docs',
        },
        links: [],
        copyright: `Copyright © ${new Date().getFullYear()} ToothMen. Built with Docusaurus.`,
      },
    }),

  plugins: [
    // /docs 入口为 docs/index.mdx（文档门户）
    // 本地搜索插件
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      {
        hashed: true,
        language: ["en", "zh"],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],
};

module.exports = config;
