#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极环境变量测试工具
用于彻底诊断多账号配置问题
"""

import os
import sys
import json
import traceback

def print_separator(title):
    """打印分隔符"""
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_all_aspects():
    """测试所有方面"""
    print_separator("终极环境变量诊断工具 v1.0")
    
    # 1. 系统信息
    print_separator("1. 系统信息")
    print(f"Python 版本: {sys.version}")
    print(f"操作系统: {sys.platform}")
    print(f"当前用户: {os.environ.get('USER', os.environ.get('USERNAME', '未知'))}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python 路径: {sys.executable}")
    
    # 2. 环境变量全面扫描
    print_separator("2. 环境变量全面扫描")
    
    # 扫描所有相关环境变量
    netlib_vars = {}
    all_vars = os.environ.copy()
    
    for var_name in sorted(all_vars.keys()):
        var_value = all_vars[var_name]
        # 检查是否包含相关关键词
        if any(keyword in var_name.upper() for keyword in 
               ['NETLIB', 'USER', 'PASS', 'ACCOUNT', 'LOGIN', 'EMAIL']):
            netlib_vars[var_name] = var_value
    
    if netlib_vars:
        print(f"找到 {len(netlib_vars)} 个相关环境变量:")
        for var_name, var_value in netlib_vars.items():
            if any(sensitive in var_name.upper() for sensitive in ['PASS', 'KEY', 'SECRET']):
                print(f"  {var_name}: ****** (长度: {len(var_value)})")
                # 显示前2个字符用于调试
                if len(var_value) >= 2:
                    print(f"           前2字符: {var_value[:2]}")
            else:
                print(f"  {var_name}: {var_value}")
                print(f"           长度: {len(var_value)}")
    else:
        print("❌ 未找到任何相关环境变量！")
    
    # 3. 特定变量测试
    print_separator("3. 特定变量详细测试")
    
    test_cases = [
        ('NETLIB_ACCOUNTS', '多账号组合字符串'),
        ('NETLIB_USERNAME1', '账号1用户名'),
        ('NETLIB_PASSWORD1', '账号1密码'),
        ('NETLIB_USERNAME2', '账号2用户名'),
        ('NETLIB_PASSWORD2', '账号2密码'),
        ('NETLIB_USERNAME', '单个账号用户名'),
        ('NETLIB_PASSWORD', '单个账号密码'),
        ('NETLIB_ACCOUNTS_JSON', 'JSON格式账号'),
    ]
    
    for var_name, description in test_cases:
        value = os.environ.get(var_name)
        if value:
            print(f"✅ {var_name}: {description}")
            print(f"   - 存在: 是")
            print(f"   - 类型: {type(value).__name__}")
            print(f"   - 长度: {len(value)} 字符")
            print(f"   - 空字符: {value.isspace() if value else 'N/A'}")
            print(f"   - 编码: {value.encode('utf-8')[:20]}...")
            
            if 'PASSWORD' not in var_name:
                print(f"   - 内容前30字符: {value[:30]}...")
            else:
                print(f"   - 内容: ******")
                if len(value) >= 2:
                    print(f"   - 前2字符: {value[:2]}...")
        else:
            print(f"❌ {var_name}: {description}")
            print(f"   - 存在: 否")
            print(f"   - 类型: None")
        
        print()
    
    # 4. 多账号解析测试
    print_separator("4. 多账号解析测试")
    
    # 测试 NETLIB_ACCOUNTS 解析
    accounts_str = os.environ.get('NETLIB_ACCOUNTS')
    if accounts_str:
        print("NETLIB_ACCOUNTS 解析测试:")
        try:
            # 尝试多种分隔符
            separators = [',', ';', '|', ' ']
            for sep in separators:
                if sep in accounts_str:
                    accounts = accounts_str.split(sep)
                    print(f"  使用分隔符 '{sep}' 分割得到 {len(accounts)} 个账号:")
                    for i, acc in enumerate(accounts, 1):
                        acc = acc.strip()
                        if acc:
                            if ':' in acc:
                                user, pwd = acc.split(':', 1)
                                print(f"    账号{i}: user='{user.strip()}', pass=***")
                            else:
                                print(f"    账号{i}: 格式错误 (缺少冒号)")
                    break
            else:
                print(f"  未找到合适的分隔符，视为单个账号")
                if ':' in accounts_str:
                    user, pwd = accounts_str.split(':', 1)
                    print(f"  单个账号: user='{user.strip()}', pass=***")
                else:
                    print(f"  格式错误: 缺少冒号分隔符")
                    
        except Exception as e:
            print(f"  解析错误: {e}")
            traceback.print_exc()
    
    # 5. 配置建议
    print_separator("5. 智能配置建议")
    
    suggestions = []
    
    if os.environ.get('NETLIB_ACCOUNTS'):
        suggestions.append("✅ 推荐使用 NETLIB_ACCOUNTS 方式")
        suggestions.append("   格式正确，包含多账号信息")
    elif os.environ.get('NETLIB_USERNAME1') and os.environ.get('NETLIB_PASSWORD1'):
        suggestions.append("✅ 推荐使用数字后缀方式")
        suggestions.append("   账号1配置完整")
        if os.environ.get('NETLIB_USERNAME2') and os.environ.get('NETLIB_PASSWORD2'):
            suggestions.append("   账号2配置完整")
        else:
            suggestions.append("   ⚠️  账号2配置不完整")
    elif os.environ.get('NETLIB_USERNAME') and os.environ.get('NETLIB_PASSWORD'):
        suggestions.append("⚠️ 当前使用单个账号方式")
        suggestions.append("   如需多账号，请使用 NETLIB_ACCOUNTS")
    else:
        suggestions.append("❌ 未检测到有效配置")
        suggestions.append("   请按照以下格式配置:")
        suggestions.append("   方式1: NETLIB_ACCOUNTS=user1:pass1,user2:pass2")
        suggestions.append("   方式2: NETLIB_USERNAME1=user1, NETLIB_PASSWORD1=pass1")
    
    for suggestion in suggestions:
        print(suggestion)
    
    # 6. GitHub Actions 特定测试
    print_separator("6. GitHub Actions 环境测试")
    
    github_vars = [
        'GITHUB_REPOSITORY',
        'GITHUB_WORKFLOW',
        'GITHUB_JOB',
        'GITHUB_RUN_ID',
        'GITHUB_ACTOR',
        'GITHUB_SHA',
    ]
    
    github_env_found = False
    for var_name in github_vars:
        value = os.environ.get(var_name)
        if value:
            print(f"  {var_name}: {value}")
            github_env_found = True
    
    if not github_env_found:
        print("  未检测到 GitHub Actions 环境变量")
        print("  可能不是在 GitHub Actions 中运行")
    
    # 7. 文件系统测试
    print_separator("7. 文件系统测试")
    
    try:
        # 测试当前目录文件
        import glob
        files = glob.glob('./*')
        print(f"当前目录文件数量: {len(files)}")
        print("主要文件:")
        for f in files[:10]:
            if any(ext in f for ext in ['.py', '.yml', '.md']):
                print(f"  - {f}")
        
        # 测试写权限
        test_file = 'test_write_permission.txt'
        try:
            with open(test_file, 'w') as f:
                f.write('Test write permission')
            os.remove(test_file)
            print("  ✅ 写权限测试通过")
        except Exception as e:
            print(f"  ❌ 写权限测试失败: {e}")
            
    except Exception as e:
        print(f"文件系统测试错误: {e}")
    
    # 8. 最终诊断
    print_separator("8. 最终诊断结果")
    
    issues = []
    warnings = []
    
    # 检查是否有任何账号配置
    has_config = any([
        os.environ.get('NETLIB_ACCOUNTS'),
        (os.environ.get('NETLIB_USERNAME1') and os.environ.get('NETLIB_PASSWORD1')),
        (os.environ.get('NETLIB_USERNAME') and os.environ.get('NETLIB_PASSWORD'))
    ])
    
    if not has_config:
        issues.append("未找到任何有效的账号配置")
    
    # 检查 NETLIB_ACCOUNTS 格式
    if os.environ.get('NETLIB_ACCOUNTS'):
        accounts_str = os.environ.get('NETLIB_ACCOUNTS')
        if ':' not in accounts_str:
            warnings.append("NETLIB_ACCOUNTS 格式可能错误，缺少冒号分隔符")
        if len(accounts_str.split(',')) > 1 and accounts_str.count(':') != accounts_str.count(',') + 1:
            warnings.append("NETLIB_ACCOUNTS 中账号数量与冒号数量不匹配")
    
    # 检查数字后缀账号完整性
    if os.environ.get('NETLIB_USERNAME1') and not os.environ.get('NETLIB_PASSWORD1'):
        warnings.append("NETLIB_USERNAME1 已设置，但 NETLIB_PASSWORD1 未设置")
    if os.environ.get('NETLIB_PASSWORD1') and not os.environ.get('NETLIB_USERNAME1'):
        warnings.append("NETLIB_PASSWORD1 已设置，但 NETLIB_USERNAME1 未设置")
    
    # 输出诊断结果
    if issues:
        print("❌ 发现问题:")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print("⚠️  发现警告:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not issues and not warnings:
        print("✅ 未发现明显问题")
    
    # 9. 解决方案建议
    print_separator("9. 解决方案建议")
    
    if not has_config:
        print("问题: 未找到任何账号配置")
        print("解决方案:")
        print("选项1 (推荐): 使用 NETLIB_ACCOUNTS")
        print("  在 GitHub Secrets 中创建:")
        print("  名称: NETLIB_ACCOUNTS")
        print("  值: qinyu521:qinyu0123456789,laoqin:laoqin123123123123")
        print()
        print("选项2: 使用数字后缀")
        print("  创建以下 Secrets:")
        print("  NETLIB_USERNAME1 = qinyu521")
        print("  NETLIB_PASSWORD1 = qinyu0123456789")
        print("  NETLIB_USERNAME2 = laoqin")
        print("  NETLIB_PASSWORD2 = laoqin123123123123")
    
    elif warnings:
        print("请根据警告信息修正配置格式")
    
    else:
        print("配置看起来正确，可以运行登录脚本")
        print("建议使用: python enhanced_login.py")
    
    print_separator("诊断完成")

if __name__ == "__main__":
    try:
        test_all_aspects()
    except Exception as e:
        print(f"诊断工具运行出错: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "=" * 80)
        print("诊断工具执行完毕")
