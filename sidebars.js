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
  // 侧边栏显示三个文档
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'NEW-26040801-补丁',
      label: 'NEW-26040801-补丁',
    },
    {
      type: 'doc',
      id: 'NEW-26040901-补丁',
      label: 'NEW-26040901-补丁',
    },
    {
      type: 'doc',
      id: 'NEW-26040902',
      label: 'NEW-26040902',
    },
  ],
};

export default sidebars;
