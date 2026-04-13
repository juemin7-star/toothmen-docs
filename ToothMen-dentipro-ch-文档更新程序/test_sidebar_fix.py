#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试侧边栏修复
"""

from pathlib import Path
import sys
sys.path.append('.')
from deployment_manager_new import DeploymentManager

def test_sidebar_generation():
    """测试侧边栏生成"""
    print("=== 测试侧边栏生成 ===")
    
    project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
    manager = DeploymentManager(project_path)
    
    # 生成侧边栏内容
    print("\n1. 生成侧边栏内容...")
    sidebar_content = manager.generate_sidebar_content()
    
    print("\n2. 检查生成的侧边栏...")
    print("-" * 60)
    print(sidebar_content)
    print("-" * 60)
    
    # 检查是否为空
    if "tutorialSidebar: [" in sidebar_content and "]," in sidebar_content:
        # 提取侧边栏内容
        start = sidebar_content.find("tutorialSidebar: [") + len("tutorialSidebar: [")
        end = sidebar_content.find("],", start)
        sidebar_inner = sidebar_content[start:end].strip()
        
        if not sidebar_inner:
            print("❌ 错误：侧边栏为空！")
            return False
        else:
            print("✅ 侧边栏生成成功，包含内容！")
            
            # 统计项目数量
            category_count = sidebar_content.count("type: 'category'")
            item_count = sidebar_content.count("'")
            
            print(f"   类别数量: {category_count}")
            print(f"   项目数量: {item_count // 2}")  # 每个项目有开始和结束引号
            
            return True
    else:
        print("❌ 错误：侧边栏格式不正确！")
        return False

def test_doc_id_extraction():
    """测试文档ID提取"""
    print("\n=== 测试文档ID提取 ===")
    
    project_path = Path(r"D:\magicdental开发备忘录\toothmen-官方说明文档系统\ToothMen-Docs-Simple")
    manager = DeploymentManager(project_path)
    
    # 测试所有MDX文件
    test_files = [
        project_path / "docs" / "安装教程" / "主程序安装教程.mdx",
        project_path / "docs" / "云更新服务说明" / "注册说明.mdx",
        project_path / "docs" / "云更新服务说明" / "特殊补充.mdx",
        project_path / "docs" / "补丁更新日志" / "new-26040101.mdx",
        project_path / "docs" / "补丁更新日志" / "new-26040902.mdx",
    ]
    
    all_success = True
    for file_path in test_files:
        print(f"\n测试文件: {file_path.name}")
        
        if not file_path.exists():
            print(f"  ❌ 文件不存在: {file_path}")
            all_success = False
            continue
            
        doc_id = manager.get_doc_id_from_mdx(file_path)
        if doc_id:
            print(f"  ✅ 文档ID: {doc_id}")
        else:
            print(f"  ❌ 无法获取文档ID")
            all_success = False
    
    return all_success

def main():
    """主函数"""
    print("ToothMen文档更新程序 - 侧边栏修复测试")
    print("=" * 60)
    
    # 测试1：文档ID提取
    test1_success = test_doc_id_extraction()
    
    # 测试2：侧边栏生成
    test2_success = test_sidebar_generation()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"  文档ID提取测试: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"  侧边栏生成测试: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("\n🎉 所有测试通过！侧边栏生成功能正常。")
        print("   请运行新版本的程序进行测试。")
    else:
        print("\n⚠️  测试失败，请检查问题。")

if __name__ == "__main__":
    main()