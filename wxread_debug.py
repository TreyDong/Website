#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信读书调试脚本
用于本地调试微信读书的Playwright操作
"""

import json
import logging
import os
import time

from playwright.sync_api import sync_playwright

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wxread_debug.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保日志目录存在
# os.makedirs(os.path.dirname("wxread_debug.log"), exist_ok=True)

class WeChatReadingDebugger:
    """微信读书调试类"""
    
    def __init__(self):
        """初始化调试器"""
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.intercepted_request = {
            'headers': None, 
            'cookies': None, 
            'success': False
        }
        self.response_data = None
    
    def setup_browser(self):
        """设置浏览器"""
        logger.info("启动Playwright")
        self.playwright = sync_playwright().start()
        
        logger.info("启动浏览器")
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 设置为True则不显示浏览器界面
            args=['--no-sandbox']
        )
        logger.info("浏览器启动成功")
    
    def create_context(self):
        """创建浏览器上下文"""
        logger.info("创建浏览器上下文")
        self.context = self.browser.new_context()
        
        # 设置请求拦截
        def handle_request(route, request):
            # 记录所有请求的URL
            # logger.info(f"请求URL: {request.url}")
            
            # 只拦截特定API请求
            if "https://weread.qq.com/web/book/read" == request.url:
                logger.info(f"拦截到目标请求: {request.url}")
                # 获取请求头
                headers = request.headers
                logger.info(f"请求头: {headers}")
                # 获取cookies
                cookies = self.context.cookies()
                logger.info(f"请求cookies: {cookies}")
                
                # 存储拦截到的信息
                self.intercepted_request['headers'] = headers
                self.intercepted_request['cookies'] = cookies
                
                # 继续请求
                route.continue_()
            else:
                route.continue_()
        
        # 设置响应拦截
        def handle_response(response):
            # 记录所有响应的URL
            # logger.info(f"响应URL: {response.url}")
            
            if "https://weread.qq.com/web/book/read" ==  response.url:
                logger.info(f"拦截到目标响应: {response.url}")
                try:
                    # 保存响应数据
                    self.response_data = response.text()
                    logger.info(f"响应文本: {self.response_data}")
                    # 解析响应JSON
                    response_json = json.loads(self.response_data)
                    logger.info(f"响应JSON: {response_json}")
                    # 检查响应是否成功
                    if response_json.get('succ') == 1:
                        logger.info("API请求成功 (succ=1)")
                        self.intercepted_request['success'] = True
                    else:
                        logger.warning(f"API请求未成功: {response_json}")
                except Exception as e:
                    logger.error(f"解析响应JSON错误: {str(e)}", exc_info=True)
        
        # 启用请求和响应拦截
        logger.info("启用请求和响应拦截")
        self.context.route("**/*", handle_request)
        self.context.on("response", handle_response)
    
    def navigate_to_login(self):
        """导航到登录页面"""
        logger.info("创建页面并导航到微信读书首页")
        self.page = self.context.new_page()
        self.page.goto("https://weread.qq.com/")
        
        # 等待页面加载完成
        logger.info("等待页面加载")
        time.sleep(5)
        
        # 点击登录按钮
        logger.info("点击登录按钮")
        self.page.wait_for_selector('.wr_index_page_top_section_header_action_link', timeout=30000)
        login_button = self.page.query_selector('.wr_index_page_top_section_header_action_link')
        if login_button:
            login_button.click()
            logger.info("成功点击登录按钮")
        else:
            logger.warning("未找到登录按钮")

        # 获取二维码图片
        logger.info("获取二维码图片")
        qr_code_selector = '.wr_login_modal_qr_img'
        self.page.wait_for_selector(qr_code_selector, timeout=30000)

        # 获取二维码图片
        logger.info("Capturing QR code image")
        qr_code_element = self.page.query_selector(qr_code_selector)
        qr_code_base64 = qr_code_element.get_attribute('src')
        
        logger.info("二维码获取成功")
        return qr_code_base64
    
    def check_login_status(self):
        """检查登录状态"""
        logger.info("检查登录状态")
        cookies = self.context.cookies()
        logger.debug(f"当前cookies: {cookies}")
        
        if not any(cookie['name'] == 'wr_fp' for cookie in cookies):
            logger.warning("未检测到登录状态 (无wr_fp cookie)")
            return False
        
        logger.info("检测到登录状态 (找到wr_fp cookie)")
        return True
    
    def navigate_to_reader(self):
        """导航到阅读页面"""
        self.page = self.context.new_page()
        logger.info("导航到阅读页面")
        self.page.goto("https://weread.qq.com/web/reader/ce032b305a9bc1ce0b0dd2a")
        time.sleep(5)
        # self.page.goto("https://weread.qq.com/web/reader/ce032b305a9bc1ce0b0dd2ak92c3210025c92cc22753209")
        # time.sleep(5)
        try:
            # 滑动到页面底部
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # buttons = self.page.wait_for_selector('.readerTopBar_link')
            login_button = self.page.query_selector_all('.readerTopBar_link')[2]
            # 有多个登录按钮，点击第三个
            if login_button:
                login_button.click()
                logger.info("成功点击登录按钮")
            qr_code_selector = self.page.wait_for_selector('img[alt="扫码登录"]', timeout=30000)
            # qr_code_element = self.page.query_selector(qr_code_selector)
            qr_code_base64 = qr_code_selector.get_attribute('src')
            logger.info("二维码获取成功: %s", qr_code_base64)
        except Exception as e:
            logger.error(f"导航到阅读页面错误: {str(e)}", exc_info=True)
        # 等待页面加载完成
        logger.info("等待页面完全加载")
        # 等待请求被拦截
        logger.info("等待请求被拦截")
        time.sleep(10)
    
    def get_intercepted_data(self):
        """获取拦截到的数据"""
        if not self.intercepted_request['headers'] or not self.intercepted_request['cookies']:
            logger.error("未能拦截到请求头或cookies")
            return None, None
            
        if not self.intercepted_request['success']:
            logger.error("API请求未返回成功状态")
            return None, None
        
        # 获取拦截到的请求头和cookie
        logger.info("成功拦截到请求头和cookies")
        headers = self.intercepted_request['headers']
        cookies = self.intercepted_request['cookies']
        
        # 转换为字符串格式
        logger.info("将headers和cookies转换为字符串格式")
        headers_str = json.dumps(headers)
        cookies_str = json.dumps(cookies)
        
        return headers_str, cookies_str
    
    def close(self):
        """关闭浏览器和Playwright"""
        logger.info("关闭浏览器上下文、浏览器和Playwright")
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def run(self):
        """运行调试流程"""
        try:
            # 设置浏览器
            self.setup_browser()
            
            # 创建上下文
            self.create_context()
            
            # # 导航到登录页面并获取二维码
            # qr_code = self.navigate_to_login()
            #
            # # 保存二维码到文件
            # if qr_code:
            #     with open("qrcode.png", "wb") as f:
            #         import base64
            #         f.write(base64.b64decode(qr_code.split(',')[1]))
            #     logger.info("二维码已保存到qrcode.png")
            #
            # # 等待用户扫码登录
            # logger.info("请使用微信扫描二维码登录")
            # input("登录完成后按回车键继续...")
            #
            # # 检查登录状态
            # if not self.check_login_status():
            #     logger.error("登录失败，请重试")
            #     return
            #
            # 导航到阅读页面
            self.navigate_to_reader()
            
            # 获取拦截到的数据
            headers_str, cookies_str = self.get_intercepted_data()
            
            if headers_str and cookies_str:
                # 保存凭证到文件
                with open("credentials.json", "w") as f:
                    json.dump({
                        "headers": headers_str,
                        "cookies": cookies_str
                    }, f, indent=2)
                logger.info("凭证已保存到credentials.json")
                
                # 打印凭证
                print("\n=== 凭证信息 ===")
                print(f"Headers: {headers_str}")
                print(f"Cookies: {cookies_str}")
                print("================\n")
            else:
                logger.error("未能获取到有效凭证")
        
        except Exception as e:
            logger.error(f"调试过程出错: {str(e)}", exc_info=True)
        
        finally:
            # 关闭浏览器和Playwright
            self.close()

def main():
    """主函数"""
    debugger = WeChatReadingDebugger()
    debugger.run()

if __name__ == "__main__":
    main() 