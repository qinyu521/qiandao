#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
netlib.re 自动登录脚本
每天定时登录以保持账户活跃
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
    def __init__(self):
        self.username = os.environ.get('NETLIB_USERNAME', 'qinyu521')
        self.password = os.environ.get('NETLIB_PASSWORD', 'qinyu0123456789')
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
            logging.info("浏览器驱动初始化成功")
            return True
            
        except WebDriverException as e:
            logging.error(f"浏览器驱动初始化失败: {str(e)}")
            return False
    
    def navigate_to_login(self):
        """导航到登录页面"""
        try:
            self.driver.get(self.login_url)
            logging.info(f"成功访问: {self.login_url}")
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'Login'))
            )
            
            # 点击Login按钮
            login_button = self.driver.find_element(By.LINK_TEXT, 'Login')
            login_button.click()
            logging.info("点击Login按钮成功")
            
            # 等待登录表单出现
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//label[text()="Username"]'))
            )
            logging.info("登录表单加载成功")
            return True
            
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logging.error(f"导航到登录页面失败: {str(e)}")
            return False
    
    def enter_credentials(self):
        """输入用户名和密码"""
        try:
            # 输入用户名
            username_field = self.driver.find_element(By.XPATH, '//input[@placeholder="Username"]')
            username_field.clear()
            username_field.send_keys(self.username)
            logging.info("用户名输入成功")
            
            # 输入密码
            password_field = self.driver.find_element(By.XPATH, '//input[@placeholder="Password"]')
            password_field.clear()
            password_field.send_keys(self.password)
            logging.info("密码输入成功")
            
            return True
            
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(f"输入凭据失败: {str(e)}")
            return False
    
    def click_login(self):
        """点击登录按钮"""
        try:
            login_button = self.driver.find_element(By.XPATH, '//button[text()="Validate"]')
            login_button.click()
            logging.info("点击登录按钮成功")
            
            # 等待登录完成
            time.sleep(3)
            
            # 检查登录是否成功（通过检查是否有Logout链接或其他登录后的元素）
            try:
                # 如果页面包含'Login'链接，说明登录失败（仍然在登录页面）
                self.driver.find_element(By.LINK_TEXT, 'Login')
                logging.warning("登录可能失败，仍在登录页面")
                return False
            except NoSuchElementException:
                # 如果找不到Login链接，说明可能登录成功
                logging.info("登录成功")
                self.login_success = True
                return True
                
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(f"点击登录按钮失败: {str(e)}")
            return False
    
    def check_logs(self):
        """检查页面日志信息"""
        try:
            logs_element = self.driver.find_element(By.XPATH, '//div[contains(text(), "Logs")]/following-sibling::div')
            logs_text = logs_element.text
            logging.info(f"页面日志: {logs_text}")
            return logs_text
        except NoSuchElementException:
            logging.warning("未找到日志元素")
            return None
    
    def cleanup(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("浏览器驱动已关闭")
            except WebDriverException as e:
                logging.error(f"关闭浏览器驱动失败: {str(e)}")
    
    def run_login(self):
        """执行完整的登录流程"""
        logging.info("=" * 50)
        logging.info(f"开始登录流程 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 50)
        
        success = False
        try:
            if self.setup_driver():
                if self.navigate_to_login():
                    if self.enter_credentials():
                        if self.click_login():
                            self.check_logs()
                            success = True
                            
        except Exception as e:
            logging.error(f"登录流程发生意外错误: {str(e)}", exc_info=True)
        finally:
            self.cleanup()
            logging.info("=" * 50)
            logging.info(f"登录流程结束 - 成功: {success}")
            logging.info("=" * 50)
            logging.info("")
            
        return success

def main():
    """主函数"""
    bot = NetlibLoginBot()
    success = bot.run_login()
    
    # 记录最终结果到状态文件
    with open('last_login_status.txt', 'w', encoding='utf-8') as f:
        f.write(f"Last login attempt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Login successful: {success}\n")
        f.write(f"Username used: {bot.username}\n")
    
    if not success:
        logging.error("登录失败，请检查凭据和网络连接")
        exit(1)
    
    logging.info("登录脚本执行完成")

if __name__ == "__main__":
    main()
