#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
netlib.re 多账号自动登录脚本
每天定时登录多个账户以保持活跃
"""

import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('login_logs.log'),
        logging.StreamHandler()
    ]
)

class NetlibLoginBot:
    def __init__(self, username, password, account_name=None):
        self.username = username
        self.password = password
        self.account_name = account_name or username  # 账号别名，用于日志区分
        self.login_url = 'https://www.netlib.re/'
        self.driver = None
        self.login_success = False
        
    def setup_driver(self):
        """设置Chrome浏览器选项"""
        try:
            chrome_options = Options()
            # 无头模式运行，不显示浏览器窗口
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--log-level=3')
            
            # 设置用户代理
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            )
            
            # 初始化驱动
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logging.info(f"[{self.account_name}] 浏览器驱动初始化成功")
            return True
            
        except WebDriverException as e:
            logging.error(f"[{self.account_name}] 浏览器驱动初始化失败: {str(e)}")
            return False
    
    def navigate_to_login(self):
        """导航到登录页面"""
        try:
            self.driver.get(self.login_url)
            logging.info(f"[{self.account_name}] 成功访问: {self.login_url}")
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'Login'))
            )
            
            # 点击Login按钮
            login_button = self.driver.find_element(By.LINK_TEXT, 'Login')
            login_button.click()
            logging.info(f"[{self.account_name}] 点击Login按钮成功")
            
            # 等待登录表单出现
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//label[text()="Username"]'))
            )
            logging.info(f"[{self.account_name}] 登录表单加载成功")
            return True
            
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logging.error(f"[{self.account_name}] 导航到登录页面失败: {str(e)}")
            return False
    
    def enter_credentials(self):
        """输入用户名和密码"""
        try:
            # 输入用户名
            username_field = self.driver.find_element(By.XPATH, '//input[@placeholder="Username"]')
            username_field.clear()
            username_field.send_keys(self.username)
            logging.info(f"[{self.account_name}] 用户名输入成功")
            
            # 输入密码
            password_field = self.driver.find_element(By.XPATH, '//input[@placeholder="Password"]')
            password_field.clear()
            password_field.send_keys(self.password)
            logging.info(f"[{self.account_name}] 密码输入成功")
            
            return True
            
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(f"[{self.account_name}] 输入凭据失败: {str(e)}")
            return False
    
    def click_login(self):
        """点击登录按钮"""
        try:
            login_button = self.driver.find_element(By.XPATH, '//button[text()="Validate"]')
            login_button.click()
            logging.info(f"[{self.account_name}] 点击登录按钮成功")
            
            # 等待登录完成
            time.sleep(3)
            
            # 检查登录是否成功（通过检查是否有Logout链接或其他登录后的元素）
            try:
                # 如果页面包含'Login'链接，说明登录失败（仍然在登录页面）
                self.driver.find_element(By.LINK_TEXT, 'Login')
                logging.warning(f"[{self.account_name}] 登录可能失败，仍在登录页面")
                return False
            except NoSuchElementException:
                # 如果找不到Login链接，说明可能登录成功
                logging.info(f"[{self.account_name}] 登录成功")
                self.login_success = True
                return True
                
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(f"[{self.account_name}] 点击登录按钮失败: {str(e)}")
            return False
    
    def check_logs(self):
        """检查页面日志信息"""
        try:
            logs_element = self.driver.find_element(By.XPATH, '//div[contains(text(), "Logs")]/following-sibling::div')
            logs_text = logs_element.text
            logging.info(f"[{self.account_name}] 页面日志: {logs_text}")
            return logs_text
        except NoSuchElementException:
            logging.warning(f"[{self.account_name}] 未找到日志元素")
            return None
    
    def cleanup(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info(f"[{self.account_name}] 浏览器驱动已关闭")
            except WebDriverException as e:
                logging.error(f"[{self.account_name}] 关闭浏览器驱动失败: {str(e)}")
    
    def run_login(self):
        """执行完整的登录流程"""
        logging.info(f"[{self.account_name}] " + "=" * 40)
        logging.info(f"[{self.account_name}] 开始登录流程 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"[{self.account_name}] " + "=" * 40)
        
        success = False
        try:
            if self.setup_driver():
                if self.navigate_to_login():
                    if self.enter_credentials():
                        if self.click_login():
                            self.check_logs()
                            success = True
                            
        except Exception as e:
            logging.error(f"[{self.account_name}] 登录流程发生意外错误: {str(e)}", exc_info=True)
        finally:
            self.cleanup()
            logging.info(f"[{self.account_name}] " + "=" * 40)
            logging.info(f"[{self.account_name}] 登录流程结束 - 成功: {success}")
            logging.info(f"[{self.account_name}] " + "=" * 40)
            logging.info("")
            
        return success

def get_accounts_from_env():
    """从环境变量获取账号列表"""
    accounts = []
    
    # 支持两种格式的环境变量
    # 格式1: NETLIB_ACCOUNTS=username1:password1,username2:password2
    # 格式2: NETLIB_USERNAME1=xxx, NETLIB_PASSWORD1=xxx, NETLIB_USERNAME2=xxx, NETLIB_PASSWORD2=xxx
    
    # 先尝试格式1
    accounts_str = os.environ.get('NETLIB_ACCOUNTS')
    if accounts_str:
        try:
            account_pairs = accounts_str.split(',')
            for i, pair in enumerate(account_pairs):
                if ':' in pair:
                    username, password = pair.split(':', 1)
                    accounts.append({
                        'username': username.strip(),
                        'password': password.strip(),
                        'name': f'Account_{i+1}'
                    })
            logging.info(f"从 NETLIB_ACCOUNTS 加载了 {len(accounts)} 个账号")
        except Exception as e:
            logging.error(f"解析 NETLIB_ACCOUNTS 失败: {e}")
    
    # 如果格式1没有获取到账号，尝试格式2
    if not accounts:
        i = 1
        while True:
            username = os.environ.get(f'NETLIB_USERNAME{i}')
            password = os.environ.get(f'NETLIB_PASSWORD{i}')
            
            if username and password:
                accounts.append({
                    'username': username,
                    'password': password,
                    'name': f'Account_{i}'
                })
                i += 1
            else:
                break
        
        # 检查是否有默认账号
        if i == 1:  # 没有找到带数字后缀的账号
            default_username = os.environ.get('NETLIB_USERNAME')
            default_password = os.environ.get('NETLIB_PASSWORD')
            if default_username and default_password:
                accounts.append({
                    'username': default_username,
                    'password': default_password,
                    'name': 'Default_Account'
                })
        
        logging.info(f"从环境变量加载了 {len(accounts)} 个账号")
    
    return accounts

def main():
    """主函数"""
    logging.info("=" * 60)
    logging.info(f"多账号登录脚本启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    # 获取账号列表
    accounts = get_accounts_from_env()
    
    if not accounts:
        logging.error("未配置任何账号信息！请设置环境变量。")
        logging.error("支持的格式:")
        logging.error("1. NETLIB_ACCOUNTS=username1:password1,username2:password2")
        logging.error("2. NETLIB_USERNAME1=xxx, NETLIB_PASSWORD1=xxx, NETLIB_USERNAME2=xxx, NETLIB_PASSWORD2=xxx")
        logging.error("3. NETLIB_USERNAME=xxx, NETLIB_PASSWORD=xxx (单个账号)")
        exit(1)
    
    logging.info(f"总共要登录 {len(accounts)} 个账号")
    logging.info("账号列表:")
    for i, account in enumerate(accounts, 1):
        logging.info(f"  {i}. {account['name']}: {account['username']}")
    
    logging.info("")
    
    # 记录结果
    results = []
    all_success = True
    
    # 逐个登录账号
    for account in accounts:
        bot = NetlibLoginBot(
            username=account['username'],
            password=account['password'],
            account_name=account['name']
        )
        
        success = bot.run_login()
        results.append({
            'account': account['name'],
            'username': account['username'],
            'success': success,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        if not success:
            all_success = False
        
        # 登录间隔，避免被检测为机器人
        if account != accounts[-1]:
            logging.info("等待5秒后登录下一个账号...")
            time.sleep(5)
    
    # 生成汇总报告
    logging.info("=" * 60)
    logging.info("多账号登录结果汇总")
    logging.info("=" * 60)
    
    success_count = sum(1 for result in results if result['success'])
    failure_count = len(results) - success_count
    
    logging.info(f"总账号数: {len(results)}")
    logging.info(f"成功登录: {success_count} 个")
    logging.info(f"登录失败: {failure_count} 个")
    
    if success_count > 0:
        logging.info("\n成功登录的账号:")
        for result in results:
            if result['success']:
                logging.info(f"  ✅ {result['account']} ({result['username']})")
    
    if failure_count > 0:
        logging.info("\n登录失败的账号:")
        for result in results:
            if not result['success']:
                logging.info(f"  ❌ {result['account']} ({result['username']})")
    
    # 记录最终结果到状态文件
    with open('last_login_status.txt', 'w', encoding='utf-8') as f:
        f.write(f"多账号登录报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总账号数: {len(results)}\n")
        f.write(f"成功登录: {success_count} 个\n")
        f.write(f"登录失败: {failure_count} 个\n")
        f.write("\n详细结果:\n")
        for result in results:
            status = "成功" if result['success'] else "失败"
            f.write(f"{result['account']} ({result['username']}): {status} - {result['timestamp']}\n")
    
    logging.info("\n登录状态已保存到 last_login_status.txt")
    logging.info("=" * 60)
    
    if not all_success:
        logging.error("部分账号登录失败，请检查日志文件")
        exit(1)
    
    logging.info("🎉 所有账号登录成功！")

if __name__ == "__main__":
    main()
