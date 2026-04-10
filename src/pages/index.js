import React from 'react';
import { Redirect } from '@docusaurus/router';

export default function Home() {
  // 直接重定向到文档首页（使用现有的文档）
  return <Redirect to="/docs/主程序安装/主程序安装说明" />;
}