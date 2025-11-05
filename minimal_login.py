#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简登录脚本 v1.0
只包含最基本的登录功能
"""

import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """设置浏览器"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"浏览器设置失败: {e}")
        return None

def login_single_account(username, password):
    """登录单个账号"""
    print(f"\n开始登录账号: {username}")
    print("-" * 40)
    
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        # 访问网站
        driver.get('https://www.netlib.re/')
        print("访问网站成功")
        time.sleep(2)
        
        # 点击登录按钮
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Login'))
        )
        login_btn.click()
        print("点击登录按钮成功")
        time.sleep(2)
        
        # 输入用户名
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Username"]'))
        )
        username_field.clear()
        username_field.send_keys(username)
        print("输入用户名成功")
        
        # 输入密码
        password_field = driver.find_element(By.XPATH, '//input[@placeholder="Password"]')
        password_field.clear()
        password_field.send_keys(password)
        print("输入密码成功")
        
        # 提交登录
        submit_btn = driver.find_element(By.XPATH, '//button[text()="Validate"]')
        submit_btn.click()
        print("提交登录成功")
        time.sleep(3)
        
        # 检查登录状态
        try:
            driver.find_element(By.LINK_TEXT, 'Login')
            print("❌ 登录失败 - 仍能找到登录按钮")
            return False
        except:
            print("✅ 登录成功 - 未找到登录按钮")
            return True
            
    except Exception as e:
        print(f"❌ 登录过程出错: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")

def main():
    """主函数"""
    print("=" * 60)
    print("极简登录脚本 v1.0")
    print("=" * 60)
    
    # 检查环境变量
    print("\n1. 检查环境变量:")
    
    # 方式1: NETLIB_ACCOUNTS
    accounts_str = os.environ.get('NETLIB_ACCOUNTS')
    if accounts_str:
        print(f"使用 NETLIB_ACCOUNTS: {accounts_str}")
        try:
            accounts = accounts_str.split(',')
            print(f"找到 {len(accounts)} 个账号")
            
            for i, account in enumerate(accounts, 1):
                if ':' in account:
                    username, password = account.split(':', 1)
                    username = username.strip()
                    password = password.strip()
                    print(f"\n账号 {i}: {username}")
                    success = login_single_account(username, password)
                    if not success:
                        print(f"账号 {i} 登录失败")
                else:
                    print(f"账号 {i} 格式错误: {account}")
                    
        except Exception as e:
            print(f"解析账号失败: {e}")
    
    # 方式2: 单个账号
    elif os.environ.get('NETLIB_USERNAME') and os.environ.get('NETLIB_PASSWORD'):
        username = os.environ.get('NETLIB_USERNAME')
        password = os.environ.get('NETLIB_PASSWORD')
        print(f"使用单个账号: {username}")
        login_single_account(username, password)
    
    else:
        print("❌ 未找到任何账号配置")
        print("请设置 NETLIB_ACCOUNTS 或 NETLIB_USERNAME/NETLIB_PASSWORD")
        sys.exit(1)

if __name__ == "__main__":
    main()
