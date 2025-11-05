#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版登录脚本 v2.0 - 解决多账号登录问题
"""

import os
import time
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    ElementClickInterceptedException
)

def setup_chrome_options():
    """设置Chrome选项"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    
    # 添加用户代理
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    # 禁用自动化检测
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options

def create_driver():
    """创建WebDriver实例"""
    try:
        chrome_options = setup_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(15)
        
        # 进一步隐藏自动化特征
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver
    except Exception as e:
        print(f"❌ 创建浏览器失败: {str(e)}")
        traceback.print_exc()
        return None

def safe_find_element(driver, selectors, description):
    """安全查找元素，尝试多个选择器"""
    for i, (by, value) in enumerate(selectors, 1):
        try:
            element = driver.find_element(by, value)
            print(f"✅ [{i}/{len(selectors)}] 找到{description}: {by}={value}")
            return element
        except NoSuchElementException:
            print(f"❌ [{i}/{len(selectors)}] 选择器失败: {by}={value}")
            continue
        except Exception as e:
            print(f"⚠️ [{i}/{len(selectors)}] 选择器异常: {by}={value}, 错误: {str(e)[:50]}...")
            continue
    
    print(f"❌ 所有选择器都无法找到{description}")
    return None

def login_account(driver, username, password, account_num):
    """登录单个账号"""
    print(f"\n{'=' * 60}")
    print(f"账号 {account_num}: {username}")
    print(f"{'=' * 60}")
    
    try:
        # 访问网站
        print("📥 正在访问网站...")
        driver.get('https://www.netlib.re/')
        time.sleep(3)
        print("✅ 网站访问成功")
        
        # 点击登录按钮
        print("🔍 正在查找登录按钮...")
        login_selectors = [
            (By.LINK_TEXT, 'Login'),
            (By.XPATH, '//a[contains(text(), "Login")]'),
            (By.XPATH, '//a[@href="/login"]'),
            (By.CSS_SELECTOR, 'a[href*="login"]')
        ]
        
        login_btn = safe_find_element(driver, login_selectors, "登录按钮")
        if not login_btn:
            print("❌ 无法找到登录按钮，尝试直接访问登录页面")
            driver.get('https://www.netlib.re/login')
            time.sleep(3)
        else:
            login_btn.click()
            print("✅ 登录按钮点击成功")
            time.sleep(3)
        
        # 输入用户名
        print("🔍 正在查找用户名输入框...")
        username_selectors = [
            (By.XPATH, '//input[@placeholder="Username"]'),
            (By.XPATH, '//input[@name="username"]'),
            (By.XPATH, '//input[type="text"]'),
            (By.XPATH, '//form//input[1]'),
            (By.XPATH, '//label[text()="Username"]/following-sibling::input')
        ]
        
        username_field = safe_find_element(driver, username_selectors, "用户名输入框")
        if not username_field:
            return False
            
        username_field.clear()
        username_field.send_keys(username)
        print(f"✅ 用户名输入成功: {username}")
        time.sleep(2)
        
        # 输入密码
        print("🔍 正在查找密码输入框...")
        password_selectors = [
            (By.XPATH, '//input[@placeholder="Password"]'),
            (By.XPATH, '//input[@name="password"]'),
            (By.XPATH, '//input[type="password"]'),
            (By.XPATH, '//form//input[2]'),
            (By.XPATH, '//label[text()="Password"]/following-sibling::input'),
            (By.XPATH, '//div[contains(text(), "Password")]/following-sibling::input')
        ]
        
        password_field = safe_find_element(driver, password_selectors, "密码输入框")
        if not password_field:
            return False
            
        password_field.clear()
        password_field.send_keys(password)
        print("✅ 密码输入成功")
        time.sleep(2)
        
        # 提交登录
        print("🔍 正在查找提交按钮...")
        submit_selectors = [
            (By.XPATH, '//button[text()="Validate"]'),
            (By.XPATH, '//button[@type="submit"]'),
            (By.XPATH, '//input[@type="submit"]'),
            (By.XPATH, '//button[contains(text(), "Submit")]'),
            (By.XPATH, '//form//button')
        ]
        
        submit_btn = safe_find_element(driver, submit_selectors, "提交按钮")
        if not submit_btn:
            return False
            
        submit_btn.click()
        print("✅ 登录提交成功")
        time.sleep(5)
        
        # 检查登录状态
        print("🔍 正在检查登录状态...")
        try:
            # 检查是否还有登录按钮
            driver.find_element(By.LINK_TEXT, 'Login')
            print("❌ 登录失败 - 页面上仍有登录按钮")
            
            # 尝试查找错误信息
            try:
                error_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "error") or contains(text(), "Error") or contains(text(), "error")]')
                for error_elem in error_elements:
                    if error_elem.text.strip():
                        print(f"❌ 错误信息: {error_elem.text.strip()}")
            except:
                pass
                
            return False
        except NoSuchElementException:
            print("✅ 登录成功 - 页面上没有登录按钮")
            return True
        except Exception as e:
            print(f"⚠️  检查登录状态时出错: {str(e)}")
            # 即使检查失败，也继续，可能登录成功了
            return True
            
    except TimeoutException:
        print("❌ 操作超时 - 页面可能加载缓慢")
        traceback.print_exc()
        return False
    except ElementClickInterceptedException:
        print("❌ 点击被拦截 - 可能有弹窗或其他元素遮挡")
        traceback.print_exc()
        return False
    except WebDriverException as e:
        print(f"❌ 浏览器异常: {str(e)}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 登录过程异常: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("增强版登录脚本 v2.0")
    print(f"运行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查环境变量
    print("\n1. 环境变量检查:")
    accounts_str = os.environ.get('NETLIB_ACCOUNTS')
    
    if not accounts_str:
        print("❌ NETLIB_ACCOUNTS 环境变量未设置")
        sys.exit(1)
    
    print(f"✅ NETLIB_ACCOUNTS 设置 (长度: {len(accounts_str)})")
    
    # 解析账号
    try:
        accounts = accounts_str.split(',')
        print(f"✅ 解析出 {len(accounts)} 个账号")
        
        valid_accounts = []
        for i, account in enumerate(accounts, 1):
            account = account.strip()
            if ':' in account:
                username, password = account.split(':', 1)
                username = username.strip()
                password = password.strip()
                if username and password:
                    valid_accounts.append((username, password))
                    print(f"   账号 {i}: {username}")
                else:
                    print(f"❌ 账号 {i} 格式错误: 用户名或密码为空")
            else:
                print(f"❌ 账号 {i} 格式错误: {account} (缺少冒号分隔符)")
                
        if not valid_accounts:
            print("❌ 没有有效的账号配置")
            sys.exit(1)
                
    except Exception as e:
        print(f"❌ 解析账号失败: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    # 创建浏览器实例
    print("\n2. 浏览器初始化:")
    driver = create_driver()
    if not driver:
        print("❌ 无法初始化浏览器，脚本退出")
        sys.exit(1)
    
    # 登录每个账号
    print(f"\n3. 开始登录 {len(valid_accounts)} 个账号:")
    results = []
    all_success = True
    
    for i, (username, password) in enumerate(valid_accounts, 1):
        # 为每个账号使用新的浏览器实例，避免会话冲突
        if i > 1:
            print(f"\n🔄 为账号 {i} 创建新的浏览器实例...")
            driver.quit()
            driver = create_driver()
            if not driver:
                print(f"❌ 无法为账号 {i} 创建浏览器，跳过")
                results.append((username, False))
                all_success = False
                continue
        
        # 登录前等待，避免被检测
        wait_time = 5 + (i * 2)  # 账号越多，等待时间越长
        print(f"\n⏰ 等待 {wait_time} 秒后登录账号 {i}...")
        time.sleep(wait_time)
        
        success = login_account(driver, username, password, i)
        results.append((username, success))
        if not success:
            all_success = False
    
    # 清理资源
    if driver:
        driver.quit()
        print("\n🔒 所有浏览器实例已关闭")
    
    # 生成结果报告
    print(f"\n{'=' * 60}")
    print("登录结果汇总")
    print(f"{'=' * 60}")
    print(f"总账号数: {len(results)}")
    print(f"成功登录: {sum(1 for _, success in results if success)} 个")
    print(f"登录失败: {sum(1 for _, success in results if not success)} 个")
    
    print(f"\n详细结果:")
    for i, (username, success) in enumerate(results, 1):
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  账号 {i}: {username} - {status}")
    
    print(f"\n{'=' * 60}")
    
    if all_success:
        print("🎉 所有账号登录成功！")
        sys.exit(0)
    elif sum(1 for _, success in results if success) > 0:
        print("⚠️  部分账号登录成功")
        sys.exit(2)
    else:
        print("❌ 所有账号登录失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
