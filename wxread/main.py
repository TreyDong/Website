# main.py 主逻辑：包括字段拼接、模拟请求
import hashlib
import json
import logging
import random
import time
import urllib.parse

import requests

from config import data, headers, cookies

# 配置日志格式
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)-8s - %(message)s')

# 加密盐及其它默认值
KEY = "3c5c8717f3daf09iop3423zafeqoi"
COOKIE_DATA = {"rq": "%2Fweb%2Fbook%2Fread"}
READ_URL = "https://weread.qq.com/web/book/read"
RENEW_URL = "https://weread.qq.com/web/login/renewal"

def execute_reading(credentials, read_count=1):
    """
    执行阅读任务
    
    Args:
        credentials: 包含headers和cookies的凭证信息
        read_count: 阅读次数，默认为1
        
    Returns:
        bool: 是否成功完成阅读任务
    """
    try:
        # 解析凭证信息
        headers = json.loads(credentials.get('headers', '{}'))
        cookies = credentials.get('cookies', '{}')
        logger.info("headers: %s", headers)
        logger.info("cookies: %s", cookies)
        if not headers or not cookies:
            logging.error("凭证信息不完整")
            return False
            
        # 准备请求数据
        request_data = data.copy()
        request_data['ct'] = int(time.time())
        request_data['ts'] = int(time.time() * 1000)
        request_data['rn'] = random.randint(0, 1000)
        request_data['sg'] = hashlib.sha256(f"{request_data['ts']}{request_data['rn']}{KEY}".encode()).hexdigest()
        request_data['s'] = cal_hash(encode_data(request_data))


        success_count = 0
        for i in range(read_count):
            logging.info(f"⏱️ 尝试第 {i+1}/{read_count} 次阅读...")
            logger.info("Request data: %s", request_data)
            # 发送阅读请求
            response = requests.post(
                READ_URL, 
                headers=headers, 

                data=json.dumps(request_data, separators=(',', ':'))
            )
            logger.info(f"Response: {response.text}")
            if response.status_code == 200:
                res_data = response.json()
                if 'succ' in res_data:
                    success_count += 1
                    logging.info(f"✅ 阅读成功，阅读进度：{success_count}/{read_count}")
                    time.sleep(30)  # 每次阅读间隔30秒
                else:
                    logging.warning("❌ 阅读失败，尝试刷新cookie...")
                    new_skey = get_wr_skey(headers, cookies)
                    if new_skey:
                        cookies['wr_skey'] = new_skey
                        logging.info(f"✅ 密钥刷新成功，新密钥：{new_skey}")
                        # 重试当前阅读
                        i -= 1
                        continue
                    else:
                        logging.error("❌ 无法获取新密钥，终止阅读")
                        return False
            else:
                logging.error(f"❌ 请求失败，状态码：{response.status_code}")
                return False
                
            # 移除签名，准备下一次请求
            request_data.pop('s', None)
            
        return success_count == read_count
        
    except Exception as e:
        logging.error(f"执行阅读任务失败: {str(e)}")
        return False

def encode_data(data):
    """数据编码"""
    return '&'.join(f"{k}={urllib.parse.quote(str(data[k]), safe='')}" for k in sorted(data.keys()))

def cal_hash(input_string):
    """计算哈希值"""
    _7032f5 = 0x15051505
    _cc1055 = _7032f5
    length = len(input_string)
    _19094e = length - 1

    while _19094e > 0:
        _7032f5 = 0x7fffffff & (_7032f5 ^ ord(input_string[_19094e]) << (length - _19094e) % 30)
        _cc1055 = 0x7fffffff & (_cc1055 ^ ord(input_string[_19094e - 1]) << _19094e % 30)
        _19094e -= 2

    return hex(_7032f5 + _cc1055)[2:].lower()

def get_wr_skey(headers, cookies):
    """刷新cookie密钥"""
    try:
        response = requests.post(
            RENEW_URL, 
            headers=headers,
            data=json.dumps(COOKIE_DATA, separators=(',', ':'))
        )
        
        for cookie in response.headers.get('Set-Cookie', '').split(';'):
            if "wr_skey" in cookie:
                return cookie.split('=')[-1][:8]
        return None
    except Exception as e:
        logging.error(f"刷新密钥失败: {str(e)}")
        return None

if __name__ == "__main__":
    # 测试代码
    test_credentials = {
        'headers': json.dumps(headers),
        'cookies': json.dumps(cookies)
    }
    success = execute_reading(test_credentials, read_count=1)
    if success:
        logging.info("测试阅读成功")
    else:
        logging.error("测试阅读失败")
