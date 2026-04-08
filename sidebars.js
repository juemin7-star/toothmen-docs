// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  // 简化版侧边栏，只显示intro文档
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'NEW-26040801-补丁',
    },
  ],
};

export default sidebars;
