#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简环境变量测试脚本
用于验证 GitHub Secrets 是否正确传递
"""

import os
import sys

def main():
    """主函数"""
    print("=" * 60)
    print("极简环境变量测试脚本")
    print(f"运行时间: {os.popen('date').read().strip()}")
    print(f"Python 版本: {sys.version}")
    print("=" * 60)
    
    # 测试所有可能的环境变量
    print("\n1. 检查所有 NETLIB_ 环境变量:")
    
    test_vars = [
        'NETLIB_ACCOUNTS',
        'NETLIB_USERNAME1',
        'NETLIB_PASSWORD1',
        'NETLIB_USERNAME2',
        'NETLIB_PASSWORD2',
        'NETLIB_USERNAME',
        'NETLIB_PASSWORD',
    ]
    
    found_any = False
    for var_name in test_vars:
        value = os.environ.get(var_name)
        if value is not None:
            print(f"✅ {var_name}")
            print(f"   - 存在: 是")
            print(f"   - 长度: {len(value)} 字符")
            if 'PASSWORD' not in var_name:
                print(f"   - 内容前20字符: {value[:20]}...")
            else:
                print(f"   - 内容: ******")
            found_any = True
        else:
            print(f"❌ {var_name}")
            print(f"   - 存在: 否")
        print()
    
    # 2. 检查系统环境变量
    print("\n2. 系统环境变量检查:")
    print(f"   当前目录: {os.getcwd()}")
    print(f"   用户: {os.environ.get('USER', 'unknown')}")
    print(f"   PATH 长度: {len(os.environ.get('PATH', ''))}")
    
    # 3. 检查 GitHub 环境
    print("\n3. GitHub 环境检查:")
    github_vars = [
        'GITHUB_REPOSITORY',
        'GITHUB_WORKFLOW',
        'GITHUB_JOB',
        'GITHUB_RUN_ID',
    ]
    
    for var in github_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: {value}")
        else:
            print(f"   {var}: 未设置")
    
    # 4. 最终结果
    print("\n" + "=" * 60)
    if found_any:
        print("✅ 成功！至少找到一个环境变量")
        print("环境变量传递正常")
        sys.exit(0)
    else:
        print("❌ 失败！未找到任何 NETLIB_ 环境变量")
        print("\n可能的原因:")
        print("1. GitHub Secrets 未正确设置")
        print("2. Secrets 名称与工作流中的名称不匹配")
        print("3. 工作流文件未正确传递环境变量")
        print("4. Secrets 权限问题")
        print("\n解决方案:")
        print("1. 确保 Secrets 名称正确 (NETLIB_ACCOUNTS)")
        print("2. 检查工作流文件中的 env 配置")
        print("3. 验证 Secrets 确实存在")
        print("4. 检查仓库权限设置")
        sys.exit(1)

if __name__ == "__main__":
    main()
