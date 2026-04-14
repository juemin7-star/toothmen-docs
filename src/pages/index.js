import React from 'react';
import { Redirect } from '@docusaurus/router';

export default function Home() {
  // 与 docs/index.mdx、navbar 一致：进入主程序安装说明（旧路径 主程序安装/主程序安装说明 已废弃）
  return (
    <Redirect to="/docs/Denti-Pro安装总教程/main-program-installation-guide" />
  );
}