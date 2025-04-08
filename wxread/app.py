import json
import logging
# Configure logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta

import pymysql
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

from config import DB_CONFIG, APP_CONFIG
from db_init import log_system_event, check_authorization_code
from main import execute_reading

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'wxread.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": APP_CONFIG['CORS_ORIGINS']}})

# Initialize scheduler
scheduler = BackgroundScheduler(
    job_defaults={
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time': 60*60  # 1小时的容错时间
    }
)
logger.info("Initializing BackgroundScheduler")
scheduler.start()
logger.info("BackgroundScheduler started successfully")


def get_db_connection():
    logger.info(f"Connecting to database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']} as {DB_CONFIG['user']}")
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )

def validate_credentials(credentials):
    """Validate WeChat Reading credentials by making a test request"""
    try:
        logger.info("Starting credentials validation")
        headers = credentials.get('headers', {})
        cookies = credentials.get('cookies', {})
    
        logger.debug(f"Raw headers: {headers}")
        logger.debug(f"Raw cookies: {cookies}")
        
        # 如果headers和cookies是字符串，尝试解析为JSON
        if isinstance(headers, str):
            logger.info("Parsing headers from JSON string")
            headers = json.loads(headers)
        if isinstance(cookies, str):
            logger.info("Parsing cookies from JSON string")
            cookies = json.loads(cookies)
            
        # 处理cookies为列表的情况（Playwright格式）
        if isinstance(cookies, list):
            logger.info("Converting cookies from list format to dictionary")
            cookies_dict = {}
            for cookie in cookies:
                if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                    cookies_dict[cookie['name']] = cookie['value']
            cookies = cookies_dict
            
        # 确保headers和cookies是字典类型
        if not isinstance(headers, dict) or not isinstance(cookies, dict):
            logger.error(f"Invalid credentials format: headers={type(headers)}, cookies={type(cookies)}")
            return False
            
        # 将cookies字典转换为cookie字符串
        logger.info("Converting cookies dictionary to cookie string")
        cookie_str = '; '.join([f"{key}={value}" for key, value in cookies.items()])
        logger.debug(f"Cookie string: {cookie_str}")
        
        # 验证凭证是否有效
        logger.info("Sending test request to validate credentials")
        response = requests.get(
            'https://weread.qq.com/web/user/info',
            headers=headers,
            cookies=cookie_str,  # 使用cookie字符串
            timeout=10
        )
        logger.info(f"Test request response status: {response.status_code}")
        logger.debug(f"Test request response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error validating credentials: {str(e)}", exc_info=True)
        return False

def parse_curl(curl_str):
    """Parse curl command to extract headers and cookies"""
    headers = {}
    cookies = {}
    
    # Extract headers
    header_pattern = r"-H '([^']+)'"
    for match in re.finditer(header_pattern, curl_str):
        header = match.group(1)
        if ': ' in header:
            key, value = header.split(': ', 1)
            headers[key] = value
    
    # Extract cookies
    cookie_pattern = r"Cookie: ([^']+)"
    cookie_match = re.search(cookie_pattern, curl_str)
    if cookie_match:
        cookie_str = cookie_match.group(1)
        for cookie in cookie_str.split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key] = value
    
    return {'headers': headers, 'cookies': cookies}

def setup_browser():
    """Setup Playwright browser for automation"""
    try:
        logger.info("Starting Playwright browser setup")
        playwright = sync_playwright().start()
        logger.info("Playwright started successfully")
        
        # 启动浏览器
        logger.info("Launching browser")
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        logger.info("Browser launched successfully")
        
        return playwright, browser
    except Exception as e:
        logger.error(f"Error setting up browser: {str(e)}", exc_info=True)
        raise

@app.route('/api/config/bash', methods=['POST'])
def config_bash():
    """Handle configuration via bash request"""
    data = request.json
    authorization_code = data.get('authorization_code')
    curl_str = data.get('bash_request')
    single_read_time = data.get('single_read_time_seconds')
    run_time_config = data.get('run_time_config')
    
    if not all([authorization_code, curl_str, single_read_time, run_time_config]):
        log_system_event('WARNING', 'Missing required parameters in bash config request', data)
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Validate authorization code
    if not check_authorization_code(authorization_code):
        log_system_event('WARNING', f'Invalid authorization code: {authorization_code}')
        return jsonify({'error': 'Invalid authorization code'}), 403
    
    credentials = parse_curl(curl_str)
    if not validate_credentials(credentials):
        log_system_event('WARNING', 'Invalid credentials in bash config request')
        return jsonify({'error': 'Invalid credentials'}), 400
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO record 
                (authorization_code, single_read_time_seconds, run_time_config, 
                 config_method, credentials)
                VALUES (%s, %s, %s, 'bash', %s)
                ON DUPLICATE KEY UPDATE
                single_read_time_seconds = VALUES(single_read_time_seconds),
                run_time_config = VALUES(run_time_config),
                credentials = VALUES(credentials),
                last_validated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(sql, (
                authorization_code,
                single_read_time,
                run_time_config,
                json.dumps(credentials)
            ))
        connection.commit()
        
        log_system_event('INFO', f'Configuration saved successfully for code: {authorization_code}')
        
        # Schedule the task
        schedule_task(authorization_code, run_time_config)
        
        return jsonify({'message': 'Configuration saved successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error saving bash configuration: {str(e)}")
        log_system_event('ERROR', 'Error saving bash configuration', {'error': str(e)})
        return jsonify({'error': str(e)}), 500

import threading

# 添加一个全局字典来存储会话状态
session_states = {}


def qrcode_login_worker(session_id):
    """后台线程处理二维码登录流程"""
    logger.info(f"Starting QR code login worker for session: {session_id}")
    
    try:
        # 初始化会话状态
        session_states[session_id] = {
            'status': 'initializing',
            'qrcode': None,
            'error': None,
            'headers': None,
            'cookies': None,
            'success': False
        }
        
        # 使用 Playwright 获取登录信息
        playwright, browser = setup_browser()
        context = None
        page = None
        
        try:
            # 创建浏览器上下文
            logger.info(f"Creating browser context for session: {session_id}")
            context = browser.new_context(
                viewport={'width': 1280, 'height': 800}
            )
            
            # 创建一个变量来存储拦截到的请求信息
            intercepted_request = {'headers': None, 'cookies': None, 'success': False}
            
            # 设置请求拦截
            def handle_request(route, request):
                # 记录所有请求的URL
                logger.info(f"Request URL: {request.url}")
                
                # 只拦截特定API请求
                if "https://weread.qq.com/web/book/read" == request.url:
                    logger.info(f"Intercepted request to: {request.url}")
                    # 获取请求头
                    headers = request.headers
                    logger.info(f"Request headers: {headers}")
                    # 获取cookies
                    cookies = context.cookies()
                    logger.info(f"Request cookies: {cookies}")
                    
                    # 存储拦截到的信息
                    intercepted_request['headers'] = headers
                    intercepted_request['cookies'] = cookies
                    
                    # 继续请求
                    route.continue_()
                else:
                    route.continue_()
            
            # 设置响应拦截
            def handle_response(response):
                if "https://weread.qq.com/web/book/read" == response.url:
                    logger.info(f"Intercepted response from: {response.url}")
                    try:
                        # 保存响应数据
                        response_data = response.text()
                        logger.info(f"Response text: {response_data}")
                        # 解析响应JSON
                        response_json = json.loads(response_data)
                        logger.info(f"Response JSON: {response_json}")
                        # 检查响应是否成功
                        if response_json.get('succ') == 1:
                            logger.info("API request successful (succ=1)")
                            intercepted_request['success'] = True
                        else:
                            logger.warning(f"API request not successful: {response_json}")
                    except Exception as e:
                        logger.error(f"Error parsing response JSON: {str(e)}", exc_info=True)
            
            # 启用请求和响应拦截
            logger.info("Enabling request and response interception")
            context.route("**/*", handle_request)
            context.on("response", handle_response)
            
            # 直接访问阅读页面
            logger.info("Navigating directly to reader page")
            page = context.new_page()
            page.goto("https://weread.qq.com/web/reader/ce032b305a9bc1ce0b0dd2a")
            
            # 等待页面加载完成
            logger.info("Waiting for page to load")
            time.sleep(5)
            
            # 检查是否存在登录按钮
            logger.info("Checking for login button")
            login_button = page.query_selector_all('.readerTopBar_link')[2]
            
            if login_button:
                logger.info("Login button found, clicking it")
                login_button.click()
                
                # 等待二维码出现
                logger.info("Waiting for QR code to appear")
                qr_code_base64 = ''
                try:
                    qr_code_selector = page.wait_for_selector('img[alt="扫码登录"]', timeout=30000)
                    logger.info("QR code appeared")
                        # 获取二维码图片
                    logger.info("Capturing QR code image")
                    qr_code_base64 = qr_code_selector.get_attribute('src')
                except Exception as e:
                    logger.error(f"QR code did not appear: {str(e)}")
                    session_states[session_id]['status'] = 'error'
                    session_states[session_id]['error'] = '二维码未出现'
                    return

                # 更新会话状态
                session_states[session_id]['status'] = 'waiting_for_scan'
                session_states[session_id]['qrcode'] = qr_code_base64
                
                # 更新数据库中的二维码
                connection = get_db_connection()
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE qrcode_sessions 
                    SET qrcode_data = %s
                    WHERE session_id = %s
                """, (qr_code_base64, session_id))
                connection.commit()
                cursor.close()
                connection.close()
                
                logger.info("QR code saved to database, waiting for user to scan")
                time.sleep(2)
                # 轮询检查登录状态
                logger.info("Starting to poll for login status")

                max_attempts = 60  # 最多等待60秒
                success_count = 0
                for attempt in range(max_attempts):
                    # 检查会话是否已取消
                    if session_states[session_id]['status'] == 'cancelled':
                        logger.info(f"Session {session_id} was cancelled")
                        return
                    avatar = page.wait_for_selector('.readerTopBar_avatar',state='visible',timeout=30000)
                    if avatar:
                        logger.info("User logged in successfully")
                        session_states[session_id]['status'] = 'logged_in'
                        page.goto("https://weread.qq.com/web/reader/ce032b305a9bc1ce0b0dd2akc9e32940268c9e1074f5bc6")
                        success_count += 1
                        logger.info(f"当前页面内容：{page.content()}")
                        time.sleep(15)
                        break
                    else:
                        time.sleep(1)
                        logger.info(f"Waiting for user to scan QR code... (Attempt {attempt+1}/{max_attempts})")
                if success_count > 0:
                    # 检查是否成功拦截到请求并且响应成功
                    if not intercepted_request['headers'] or not intercepted_request['cookies']:
                        logger.error("Failed to intercept request headers or cookies")
                        session_states[session_id]['status'] = 'error'
                        session_states[session_id]['error'] = '未能获取到请求信息，请重试'
                        return

                    # if not intercepted_request['success']:
                    #     logger.error("API request did not return success status")
                    #     session_states[session_id]['status'] = 'error'
                    #     session_states[session_id]['error'] = 'API请求未返回成功状态，请重试'
                    #     return

                    # 获取拦截到的请求头和cookie
                    logger.info("Successfully intercepted request headers and cookies")
                    headers = intercepted_request['headers']

                    # 转换为字符串格式
                    logger.info("Converting headers and cookies to string format")
                    headers_str = json.dumps(headers)
                    cookies_str = headers.get('cookie','')

                    # 更新会话状态
                    session_states[session_id]['status'] = 'completed'
                    session_states[session_id]['headers'] = headers_str
                    session_states[session_id]['cookies'] = cookies_str
                    session_states[session_id]['success'] = True

                    # 更新数据库中的会话状态
                    connection = get_db_connection()
                    cursor = connection.cursor()
                    cursor.execute("""
                        UPDATE qrcode_sessions 
                        SET status = 'confirmed',
                            credentials = %s
                        WHERE session_id = %s
                    """, (json.dumps({'headers': headers_str, 'cookies': cookies_str}), session_id))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    logger.info("QR code login process completed successfully")
                    return
                else:
                    # 如果没有检测到登录状态
                    logger.warning("Login status not detected after maximum attempts")
                    session_states[session_id]['status'] = 'timeout'
                    session_states[session_id]['error'] = '登录超时，请重试'
            
        finally:
            logger.info("Closing browser context, browser, and playwright")
            if page:
                page.close()
            if context:
                context.close()
            browser.close()
            playwright.stop()
            
    except Exception as e:
        logger.error(f"QR code login worker failed: {str(e)}", exc_info=True)
        session_states[session_id]['status'] = 'error'
        session_states[session_id]['error'] = str(e)

@app.route('/api/config/qrcode', methods=['POST'])
def generate_qrcode():
    """Generate QR code for WeChat Reading login"""
    try:
        logger.info("Starting QR code generation process")
        # 生成唯一的会话ID
        session_id = str(uuid.uuid4())
        logger.debug(f"Generated session ID: {session_id}")
        
        # 保存会话信息到数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 创建会话表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qrcode_sessions (
                session_id VARCHAR(36) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',
                credentials JSON
            )
        """)
        
        # 插入会话记录
        expires_at = datetime.now() + timedelta(seconds=APP_CONFIG['QRCODE_SESSION_TIMEOUT'])
        cursor.execute("""
            INSERT INTO qrcode_sessions (session_id, expires_at)
            VALUES (%s, %s)
        """, (session_id, expires_at))
        
        connection.commit()
        logger.info(f"Session saved to database with ID: {session_id}")
        
        # 启动后台线程处理二维码登录
        thread = threading.Thread(target=qrcode_login_worker, args=(session_id,))
        thread.daemon = True
        thread.start()
        
        # 等待二维码生成
        max_wait = 30  # 最多等待30秒
        for _ in range(max_wait):
            if session_id in session_states and session_states[session_id]['qrcode']:
                break
            time.sleep(1)
        
        # 检查是否成功生成二维码
        if session_id not in session_states or not session_states[session_id]['qrcode']:
            logger.error("Failed to generate QR code")
            return jsonify({'success': False, 'error': '生成二维码失败，请重试'}), 500
        
        # 返回二维码和会话ID
        return jsonify({
            'success': True,
            'session_id': session_id,
            'qrcode': session_states[session_id]['qrcode'],
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成二维码失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/qrcode/status/<session_id>', methods=['GET'])
def check_qrcode_status(session_id):
    """Check QR code login status"""
    try:
        # 检查会话是否存在
        if session_id not in session_states:
            logger.error(f"Session not found: {session_id}")
            return jsonify({'success': False, 'error': '会话不存在或已过期'}), 404
        
        # 获取会话状态
        session_state = session_states[session_id]
        status = session_state['status']
        
        # 根据状态返回不同的响应
        if status == 'initializing':
            return jsonify({
                'success': True,
                'status': 'initializing',
                'message': '正在初始化...'
            })
        elif status == 'waiting_for_scan':
            return jsonify({
                'success': True,
                'status': 'waiting_for_scan',
                'message': '等待扫描二维码...'
            })
        elif status == 'logged_in':
            return jsonify({
                'success': True,
                'status': 'logged_in',
                'message': '已登录，正在获取凭证...'
            })
        elif status == 'completed':
            return jsonify({
                'success': True,
                'status': 'completed',
                'message': '登录完成',
                'headers': session_state['headers'],
                'cookies': session_state['cookies']
            })
        elif status == 'error':
            return jsonify({
                'success': False,
                'status': 'error',
                'error': session_state['error']
            })
        elif status == 'timeout':
            return jsonify({
                'success': False,
                'status': 'timeout',
                'error': '登录超时，请重试'
            })
        elif status == 'cancelled':
            return jsonify({
                'success': False,
                'status': 'cancelled',
                'error': '会话已取消'
            })
        else:
            return jsonify({
                'success': False,
                'status': 'unknown',
                'error': '未知状态'
            })
            
    except Exception as e:
        logger.error(f"检查二维码状态失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/qrcode/cancel/<session_id>', methods=['POST'])
def cancel_qrcode_session(session_id):
    """Cancel QR code session"""
    try:
        # 检查会话是否存在
        if session_id not in session_states:
            logger.error(f"Session not found: {session_id}")
            return jsonify({'success': False, 'error': '会话不存在或已过期'}), 404
        
        # 更新会话状态为已取消
        session_states[session_id]['status'] = 'cancelled'
        
        # 更新数据库中的会话状态
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE qrcode_sessions 
            SET status = 'cancelled'
            WHERE session_id = %s
        """, (session_id,))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': '会话已取消'
        })
        
    except Exception as e:
        logger.error(f"取消会话失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/setup', methods=['POST', 'OPTIONS'])
def setup():
    """Handle setup request from frontend"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        authCode = data.get('authCode')
        readTimeMinutes = data.get('readTimeMinutes')
        scheduleTime = data.get('scheduleTime')
        bashRequest = data.get('bashRequest')
        session_id = data.get('session_id')
        
        if not all([authCode, readTimeMinutes, scheduleTime]):
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
            
        # 验证阅读时间不超过24小时
        try:
            read_time = int(readTimeMinutes)
            if read_time <= 0 or read_time > 1440:  # 1440分钟 = 24小时
                return jsonify({'success': False, 'error': '阅读时间必须在1-1440分钟之间'}), 400
        except ValueError:
            return jsonify({'success': False, 'error': '阅读时间必须是有效的数字'}), 400
            
        # 验证授权码是否存在
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM authorization_codes WHERE code = %s", (authCode,))
        auth_code = cursor.fetchone()
        if not auth_code:
            return jsonify({'success': False, 'error': '无效的授权码'}), 400
            
        # 将分钟转换为秒
        single_read_time_seconds = read_time * 60
        
        # 将时间格式转换为cron表达式
        try:
            hour, minute = scheduleTime.split(':')
            # 确保hour和minute是有效的数字
            hour = int(hour)
            minute = int(minute)
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                return jsonify({'success': False, 'error': '无效的时间格式'}), 400
            run_time_config = f"{minute} {hour} * * *"
            logger.info(f"Converted schedule time '{scheduleTime}' to cron expression: '{run_time_config}'")
        except Exception as e:
            logger.error(f"Error parsing schedule time: {str(e)}")
            return jsonify({'success': False, 'error': '无效的时间格式'}), 400
        
        # 检查是否存在配置
        cursor.execute("SELECT * FROM record WHERE authorization_code = %s", (authCode,))
        existing_record = cursor.fetchone()
        
        credentials = None
        if bashRequest:  # bash模式
            try:
                # 从curl命令中提取headers和cookies
                headers = {}
                cookies = {}
                
                # 提取headers
                header_pattern = r"-H '([^']+)'"
                for match in re.finditer(header_pattern, bashRequest):
                    header = match.group(1)
                    if ': ' in header:
                        key, value = header.split(': ', 1)
                        headers[key] = value
                
                # 提取cookies
                cookie_pattern = r"-b '([^']+)'"
                cookie_match = re.search(cookie_pattern, bashRequest)
                if cookie_match:
                    cookie_str = cookie_match.group(1)
                    for cookie in cookie_str.split('; '):
                        if '=' in cookie:
                            key, value = cookie.split('=', 1)
                            cookies[key] = value
                
                if not headers or not cookies:
                    return jsonify({'success': False, 'error': '无法从bash请求中提取headers和cookies'}), 400
                
                credentials = {
                    'headers': json.dumps(headers),
                    'cookies': json.dumps(cookies)
                }
                
            except Exception as e:
                logging.error(f"解析bash请求失败: {str(e)}")
                return jsonify({'success': False, 'error': '解析bash请求失败'}), 400
                
        else:  # 二维码模式
            if not session_id:
                return jsonify({'success': False, 'error': '二维码模式缺少session_id'}), 400
                
            # 获取会话信息
            cursor.execute("SELECT * FROM qrcode_sessions WHERE session_id = %s", (session_id,))
            session = cursor.fetchone()
            
            if not session:
                return jsonify({'success': False, 'error': '会话不存在或已过期'}), 404
                
            # 使用前端传来的headers和cookies
            headers_str = data.get('headers')
            cookies_str = data.get('cookies')
            
            if not headers_str or not cookies_str:
                return jsonify({'success': False, 'error': '缺少登录凭证信息'}), 400
            credentials = {
                'headers': headers_str,
                'cookies': cookies_str
            }

        # 验证凭证是否有效（尝试执行一次阅读）
        try:
            success = execute_reading(credentials, read_count=1)
            if not success:
                return jsonify({'success': False, 'error': '凭证验证失败，请检查登录信息是否正确'}), 400
        except Exception as e:
            logging.error(f"验证凭证失败: {str(e)}")
            return jsonify({'success': False, 'error': '验证凭证失败，请检查登录信息是否正确'}), 400
        if existing_record:
            # 更新现有配置
            cursor.execute("""
                UPDATE record 
                SET single_read_time_seconds = %s,
                    run_time_config = %s,
                    credentials = %s,
                    last_validated_at = CURRENT_TIMESTAMP,
                    is_active = TRUE
                WHERE authorization_code = %s
            """, (
                single_read_time_seconds,
                run_time_config,
                json.dumps(credentials),
                authCode
            ))
            connection.commit()
            # 更新定时任务
            schedule_task(authCode, run_time_config)
            
            return jsonify({
                'success': True,
                'message': '配置更新成功'
            })
        else:
            # 保存新配置
            try:
                cursor.execute("""
                    INSERT INTO record 
                    (authorization_code, single_read_time_seconds, run_time_config, 
                     config_method, credentials, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (
                    authCode,
                    single_read_time_seconds,
                    run_time_config,
                    'bash' if bashRequest else 'qrcode',
                    json.dumps(credentials)
                ))
                
                # 标记授权码为已使用
                cursor.execute("""
                    UPDATE authorization_codes 
                    SET is_used = TRUE, 
                        used_at = CURRENT_TIMESTAMP,
                        used_by = %s
                    WHERE code = %s
                """, (authCode, authCode))
                
                # 确保事务提交
                connection.commit()
                logger.info(f"Successfully inserted new configuration for auth code: {authCode}")
                
                # 设置定时任务
                schedule_task(authCode, run_time_config)
                
                return jsonify({
                    'success': True,
                    'message': '配置保存成功'
                })
            except Exception as e:
                # 回滚事务
                connection.rollback()
                logger.error(f"Error inserting configuration: {str(e)}", exc_info=True)
                return jsonify({'success': False, 'error': f'保存配置失败: {str(e)}'}), 500
            
    except Exception as e:
        logging.error(f"设置失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def load_scheduled_tasks():
    """从数据库加载所有活动的定时任务"""
    try:
        logger.info("Loading scheduled tasks from database")
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 获取所有活动的配置
        cursor.execute("""
            SELECT authorization_code, run_time_config 
            FROM record 
            WHERE is_active = TRUE
        """)
        active_configs = cursor.fetchall()
        
        logger.info(f"Found {len(active_configs)} active configurations")
        
        # 为每个配置创建定时任务
        for config in active_configs:
            auth_code = config['authorization_code']
            run_time_config = config['run_time_config']
            
            try:
                # 移除现有的任务（如果存在）
                job_id = f"wxread_{auth_code}"
                if scheduler.get_job(job_id):
                    logger.info(f"Removing existing job: {job_id}")
                    scheduler.remove_job(job_id)
                
                # 解析cron表达式
                cron_params = parse_cron_expression(run_time_config)
                logger.info(f"Cron parameters for job {job_id}: {cron_params}")
                
                # 添加新任务
                scheduler.add_job(
                    task_wrapper,
                    'cron',
                    **cron_params,
                    id=job_id,
                    args=[auth_code]  # 传递授权码作为参数
                )
                
                logger.info(f"Successfully scheduled task for authorization code: {auth_code}")
                
            except Exception as e:
                logger.error(f"Error scheduling task for {auth_code}: {str(e)}", exc_info=True)
        
        cursor.close()
        connection.close()
        logger.info("Finished loading scheduled tasks")
        
        # 验证任务是否已加载
        jobs = scheduler.get_jobs()
        logger.info(f"Total scheduled jobs after loading: {len(jobs)}")
        for job in jobs:
            logger.info(f"Loaded job: {job.id}, next run: {job.next_run_time}")
        
    except Exception as e:
        logger.error(f"Error loading scheduled tasks: {str(e)}", exc_info=True)

def task_wrapper(authorization_code):
    """定时任务包装函数"""
    try:
        logger.info(f"Executing scheduled task for authorization code: {authorization_code}")
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 获取配置信息
        cursor.execute("""
            SELECT * FROM record 
            WHERE authorization_code = %s AND is_active = TRUE
        """, (authorization_code,))
        config = cursor.fetchone()
        
        if not config:
            logger.error(f"未找到有效的配置: {authorization_code}")
            return
            
        # 创建执行日志
        cursor.execute("""
            INSERT INTO execution_log 
            (authorization_code, start_time, status)
            VALUES (%s, CURRENT_TIMESTAMP, 'running')
        """, (authorization_code,))
        log_id = cursor.lastrowid
        
        try:
            # 执行阅读任务
            success = execute_reading(
                json.loads(config['credentials']), 
                read_count=config['single_read_time_seconds'] // 30  # 每30秒一次阅读
            )
            
            # 更新执行日志
            cursor.execute("""
                UPDATE execution_log 
                SET end_time = CURRENT_TIMESTAMP,
                    status = %s,
                    details = %s
                WHERE log_id = %s
            """, (
                'success' if success else 'failed',
                '阅读任务执行成功' if success else '阅读任务执行失败',
                log_id
            ))
            
        except Exception as e:
            logger.error(f"执行任务失败: {str(e)}")
            cursor.execute("""
                UPDATE execution_log 
                SET end_time = CURRENT_TIMESTAMP,
                    status = 'failed',
                    details = %s
                WHERE log_id = %s
            """, (str(e), log_id))
            
        connection.commit()
        
    except Exception as e:
        logger.error(f"定时任务执行失败: {str(e)}")

def schedule_task(authorization_code, run_time_config):
    """Schedule a task based on the run_time_config"""
    try:
        logger.info(f"Scheduling task for authorization code: {authorization_code} with config: {run_time_config}")
        
        # 移除现有的任务（如果存在）
        job_id = f"wxread_{authorization_code}"
        if scheduler.get_job(job_id):
            logger.info(f"Removing existing job: {job_id}")
            scheduler.remove_job(job_id)
        
        # 解析cron表达式
        cron_params = parse_cron_expression(run_time_config)
        logger.info(f"Cron parameters for job {job_id}: {cron_params}")
        
        # 添加新任务
        scheduler.add_job(
            task_wrapper,
            'cron',
            **cron_params,
            id=job_id,
            args=[authorization_code]  # 传递授权码作为参数
        )
        
        logger.info(f"Successfully scheduled task for authorization code: {authorization_code}")
        
    except Exception as e:
        logger.error(f"Error scheduling task: {str(e)}", exc_info=True)
        raise

def parse_cron_expression(expression):
    """Parse cron expression into APScheduler parameters"""
    try:
        # 记录原始表达式
        logger.info(f"Parsing cron expression: {expression}")
        
        # 分割表达式
        parts = expression.split()
        if len(parts) != 5:
            logger.error(f"Invalid cron expression format: {expression}")
            raise ValueError(f"Invalid cron expression format: {expression}")
        
        # 提取各个部分
        minute, hour, day, month, day_of_week = parts
        
        # 验证各个部分
        if not (minute.isdigit() or minute == '*'):
            logger.error(f"Invalid minute in cron expression: {minute}")
            raise ValueError(f"Invalid minute in cron expression: {minute}")
            
        if not (hour.isdigit() or hour == '*'):
            logger.error(f"Invalid hour in cron expression: {hour}")
            raise ValueError(f"Invalid hour in cron expression: {hour}")
            
        # 构建参数
        params = {
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week
        }
        
        logger.info(f"Parsed cron expression to parameters: {params}")
        return params
        
    except Exception as e:
        logger.error(f"Error parsing cron expression: {str(e)}", exc_info=True)
        raise

@app.route('/api/tasks', methods=['GET'])
def get_scheduled_tasks():
    """查询当前的所有定时任务，支持根据授权码筛选"""
    try:
        logger.info("Received request to get scheduled tasks")
        
        # 获取查询参数
        auth_code = request.args.get('auth_code')
        logger.info(f"Query parameter - auth_code: {auth_code}")
        
        # 检查是否提供了授权码
        if not auth_code:
            logger.warning("No authorization code provided")
            return jsonify({'success': False, 'error': '必须提供授权码'}), 400
            
        # 检查是否是管理员授权码
        is_admin = auth_code == APP_CONFIG.get('ADMIN_AUTH_CODE', 'admin')
        logger.info(f"Is admin: {is_admin}")
        
        # 获取所有定时任务
        jobs = scheduler.get_jobs()
        logger.info(f"Found {len(jobs)} scheduled jobs")
        
        # 准备结果列表
        tasks = []
        logger.info(f"Starting to iterate over jobs")
        
        # 获取数据库连接
        connection = get_db_connection()
        cursor = connection.cursor()
        
        for job in jobs:
            logger.info(f"Processing job: {job}")
            # 从job_id中提取授权码
            job_id = job.id
            job_auth_code = job_id[7:]  # 去掉'wxread_'前缀
            
            # 如果不是管理员，只显示匹配的任务
            if not is_admin and job_auth_code != auth_code:
                logger.info(f"Skipping job {job_id} - not matching auth code")
                continue
            
            # 从数据库获取任务的详细信息
            cursor.execute("""
                SELECT single_read_time_seconds, created_at, is_active, last_validated_at
                FROM record
                WHERE authorization_code = %s
            """, (job_auth_code,))
            record = cursor.fetchone()
            
            # 获取任务的下次运行时间
            next_run_time = job.next_run_time
            if next_run_time:
                # 确保时间与系统时间一致
                next_run_time = next_run_time.astimezone()
                next_run_time = next_run_time.strftime('%Y-%m-%d %H:%M:%S')

            # 构建任务信息
            task_info = {
                'job_id': job_id,
                'auth_code': job_auth_code,
                'next_run_time': next_run_time,
                'cron_expression': job.trigger.fields_str if hasattr(job.trigger, 'fields_str') else str(job.trigger),
                'reading_time_minutes': record['single_read_time_seconds'] // 60 if record else None,
                'created_at': record['created_at'].strftime('%Y-%m-%d %H:%M:%S') if record and record['created_at'] else None,
                'is_active': record['is_active'] if record else False,
                'last_validated_at': record['last_validated_at'].strftime('%Y-%m-%d %H:%M:%S') if record and record['last_validated_at'] else None
            }

            tasks.append(task_info)
        
        # 关闭数据库连接
        cursor.close()
        connection.close()
        
        logger.info(f"Returning {len(tasks)} tasks")
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total': len(tasks)
        })
        
    except Exception as e:
        logger.error(f"Error getting scheduled tasks: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 加载定时任务
    load_scheduled_tasks()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000)