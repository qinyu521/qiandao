#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版登录脚本 - 确保能运行
"""

import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def main():
    """主函数"""
    print("=" * 60)
    print("最终版登录脚本")
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
        
        for i, account in enumerate(accounts, 1):
            if ':' in account:
                username, password = account.split(':', 1)
                username = username.strip()
                password = password.strip()
                print(f"   账号 {i}: {username}")
            else:
                print(f"❌ 账号 {i} 格式错误: {account}")
                
    except Exception as e:
        print(f"❌ 解析账号失败: {e}")
        sys.exit(1)
    
    # 配置浏览器
    print("\n2. 配置浏览器:")
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        print("✅ 浏览器配置成功")
        
    except Exception as e:
        print(f"❌ 浏览器配置失败: {e}")
        sys.exit(1)
    
    # 登录每个账号
    print("\n3. 开始登录:")
    for i, account in enumerate(accounts, 1):
        if ':' not in account:
            continue
            
        username, password = account.split(':', 1)
        username = username.strip()
        password = password.strip()
        
        print(f"\n{'=' * 50}")
        print(f"账号 {i}: {username}")
        print(f"{'=' * 50}")
        
        try:
            # 访问网站
            driver.get('https://www.netlib.re/')
            print("✅ 访问网站成功")
            time.sleep(2)
            
            # 点击登录
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Login'))
            )
            login_btn.click()
            print("✅ 点击登录按钮成功")
            time.sleep(2)
            
            # 输入用户名
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Username"]'))
            )
            username_field.clear()
            username_field.send_keys(username)
            print("✅ 输入用户名成功")
            
            # 尝试多种方式输入密码
            password_found = False
            password_selectors = [
                '//input[@placeholder="Password"]',
                '//input[@name="password"]', 
                '//input[type="password"]',
                '//form//input[2]'
            ]
            
            for selector in password_selectors:
                try:
                    password_field = driver.find_element(By.XPATH, selector)
                    password_field.clear()
                    password_field.send_keys(password)
                    print(f"✅ 使用选择器 {selector} 输入密码成功")
                    password_found = True
                    break
                except Exception as e:
                    print(f"❌ 选择器 {selector} 失败: {e}")
                    continue
            
            if not password_found:
                print("❌ 所有密码选择器都失败")
                continue
            
            # 提交登录
            submit_btn = driver.find_element(By.XPATH, '//button[text()="Validate"]')
            submit_btn.click()
            print("✅ 提交登录成功")
            time.sleep(3)
            
            # 检查登录状态
            try:
                driver.find_element(By.LINK_TEXT, 'Login')
                print("❌ 登录失败 - 仍有登录按钮")
            except:
                print("✅ 登录成功 - 无登录按钮")
                
        except Exception as e:
            print(f"❌ 登录过程出错: {e}")
            continue
    
    # 清理
    driver.quit()
    print("\n✅ 浏览器已关闭")
    print("=" * 60)
    print("脚本执行完成")

if __name__ == "__main__":
    main()
