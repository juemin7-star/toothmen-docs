#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复 docusaurus.config.js 配置文件
确保文件是JavaScript格式，不是MDX格式
"""

import os
import re
from pathlib import Path

def check_and_fix_docusaurus_config(project_path):
    """
    检查并修复 docusaurus.config.js 文件
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        (fixed, message): 是否修复成功，消息
    """
    config_path = Path(project_path) / "docusaurus.config.js"
    
    if not config_path.exists():
        return False, f"配置文件不存在: {config_path}"
    
    try:
        # 读取文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否是MDX格式（包含YAML frontmatter）
        if content.strip().startswith('---'):
            print("⚠️  检测到 docusaurus.config.js 被写入了MDX内容")
            print("🔄 正在恢复为正确的JavaScript配置...")
            
            # 创建正确的JavaScript配置
            fixed_content = create_correct_config()
            
            # 备份原文件
            backup_path = config_path.with_suffix('.js.mdx_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📁 已备份原文件到: {backup_path}")
            
            # 写入修复后的文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return True, "配置文件已从MDX格式修复为JavaScript格式"
        
        # 检查是否是有效的JavaScript
        if not is_valid_javascript(content):
            print("⚠️  检测到 docusaurus.config.js 格式可能有问题")
            print("🔄 正在修复JavaScript配置...")
            
            # 尝试修复
            fixed_content = fix_javascript_config(content)
            
            # 备份原文件
            backup_path = config_path.with_suffix('.js.invalid_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📁 已备份原文件到: {backup_path}")
            
            # 写入修复后的文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return True, "配置文件已修复为有效的JavaScript格式"
        
        return False, "配置文件已经是正确的JavaScript格式"
        
    except Exception as e:
        return False, f"检查配置文件失败: {str(e)}"

def is_valid_javascript(content):
    """检查是否是有效的JavaScript配置"""
    # 检查是否包含基本的JavaScript结构
    checks = [
        ('const config =', '缺少 config 定义'),
        ('module.exports = config', '缺少 module.exports'),
        ('title:', '缺少 title 配置'),
        ('presets:', '缺少 presets 配置'),
    ]
    
    for check_str, error_msg in checks:
        if check_str not in content:
            print(f"❌ {error_msg}")
            return False
    
    return True

def fix_javascript_config(content):
    """修复JavaScript配置"""
    # 尝试从原内容中提取有用的部分
    navbar_items = extract_navbar_items(content)
    
    # 创建新的配置
    fixed_content = create_correct_config(navbar_items)
    
    return fixed_content

def extract_navbar_items(content):
    """从原内容中提取导航栏项目"""
    navbar_items = []
    
    # 查找 items: [ ... ] 部分
    pattern = r'items:\s*\[(.*?)\]'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        items_content = match.group(1)
        # 提取每个项目
        item_pattern = r'\{[^}]*type:\s*[\'"](doc|search)[\'"][^}]*\}'
        items = re.findall(item_pattern, items_content, re.DOTALL)
        
        for item in items:
            # 提取标签和文档ID
            label_match = re.search(r'label:\s*[\'"]([^\'"]+)[\'"]', item)
            doc_id_match = re.search(r'docId:\s*[\'"]([^\'"]+)[\'"]', item)
            type_match = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', item)
            position_match = re.search(r'position:\s*[\'"]([^\'"]+)[\'"]', item)
            
            if label_match and type_match:
                item_data = {
                    'type': type_match.group(1),
                    'label': label_match.group(1),
                }
                
                if doc_id_match:
                    item_data['docId'] = doc_id_match.group(1)
                
                if position_match:
                    item_data['position'] = position_match.group(1)
                
                navbar_items.append(item_data)
    
    return navbar_items

def create_correct_config(navbar_items=None):
    """创建正确的JavaScript配置"""
    if navbar_items is None:
        navbar_items = [
            {
                'type': 'doc',
                'docId': 'Denti-Pro安装总教程/main-program-installation-guide',
                'position': 'left',
                'label': '总文档中心',
            },
            {
                'type': 'doc',
                'docId': 'Denti-Pro更新日志/changelog-index',
                'position': 'left',
                'label': '更新日志',
            },
            {
                'type': 'search',
                'position': 'right',
            },
        ]
    
    # 构建导航栏项目字符串
    items_lines = []
    for item in navbar_items:
        if item['type'] == 'doc':
            items_lines.append(f"""          {{
            type: 'doc',
            docId: '{item['docId']}',
            position: '{item['position']}',
            label: '{item['label']}',
          }},""")
        elif item['type'] == 'search':
            items_lines.append(f"""          {{
            type: 'search',
            position: '{item['position']}',
          }},""")
    
    items_content = "\n".join(items_lines)
    
    config = f"""// @ts-check
// `@ts-check` 启用TypeScript类型检查（可选）

/** @type {{import('@docusaurus/types').Config}} */
const config = {{
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
  onBrokenMarkdownLinks: 'warn',

  // 即使你使用国际化的英文网站，也可以保留这个配置
  i18n: {{
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  }},

  presets: [
    [
      'classic',
      /** @type {{import('@docusaurus/preset-classic').Options}} */
      ({{
        docs: {{
          sidebarPath: require.resolve('./sidebars.js'),
          // 如果需要，可以取消注释下面的配置
          // routeBasePath: '/', // 将docs设置为根路径
          // editUrl: 'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        }},
        blog: false, // 禁用博客功能
        theme: {{
          customCss: require.resolve('./src/css/custom.css'),
        }},
      }}),
    ],
  ],

  themeConfig:
    /** @type {{import('@docusaurus/preset-classic').ThemeConfig}} */
    ({{
      // 替换为你的项目社交链接
      navbar: {{
        title: 'ToothMen文档',
        logo: {{
          alt: 'ToothMen Logo',
          src: 'img/logo.svg',
        }},
        items: [
{items_content}
        ],
      }},
      footer: {{
        style: 'dark',
        links: [
          {{
            title: '文档',
            items: [
              {{
                label: '文档首页',
                to: '/docs',
              }},
            ],
          }},
        ],
        copyright: `Copyright © ${{new Date().getFullYear()}} ToothMen. Built with Docusaurus.`,
      }},
    }}),

  plugins: [
    // 本地搜索插件
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      {{
        hashed: true,
        language: ["en", "zh"],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      }},
    ],
  ],
}};

module.exports = config;"""
    
    return config

def main():
    """主函数"""
    project_path = r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple"
    
    print("[检查] 检查 docusaurus.config.js 配置文件...")
    print(f"项目路径: {project_path}")
    print("=" * 60)
    
    fixed, message = check_and_fix_docusaurus_config(project_path)
    
    if fixed:
        print(f"[成功] {message}")
    else:
        print(f"[信息] {message}")
    
    print("=" * 60)
    print("检查完成！")

if __name__ == "__main__":
    main()