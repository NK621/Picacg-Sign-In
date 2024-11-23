import json
import hashlib
import hmac
import logging
import time
import uuid
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict

import httpx

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BiKa:
    BASE_URL = "https://picaapi.picacomic.com/"
    POST = "POST"

    API_PATH = {"sign_in": "auth/sign-in", "punch_in": "users/punch-in"}

    API_KEY = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
    API_SECRET = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"

    def __init__(self):
        self.static_headers = {
            "api-key": self.API_KEY,
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "2",
            "app-version": "2.2.1.3.3.4",
            "image-quality": "original",
            "app-platform": "android",
            "app-build-version": "45",
            "User-Agent": "okhttp/3.8.1",
        }

    def _generate_device_uuid(self) -> str:
        """生成随机设备 UUID"""
        return str(uuid.uuid4())

    def _encode_signature(self, raw: str):
        raw = raw.lower()
        h = hmac.new(self.API_SECRET.encode("utf-8"), digestmod=hashlib.sha256)
        h.update(raw.encode("utf-8"))
        return h.hexdigest()

    def _send_request(self, _url: str, method: str, body: Dict = None, token: str = None):
        try:
            current_time = str(int(time.time()))
            nonce = str(uuid.uuid4()).replace("-", "")
            _raw = _url + current_time + nonce + method + self.API_KEY
            signature = self._encode_signature(_raw)

            headers = {
                **self.static_headers,
                "time": current_time,
                "nonce": nonce,
                "signature": signature,
                "app-uuid": self._generate_device_uuid(),
            }

            if method.lower() in ["post", "put"]:
                headers["Content-Type"] = "application/json; charset=UTF-8"

            if token:
                headers["authorization"] = token

            url = self.BASE_URL + _url
            logger.info("发送请求: %s %s", method, url)
            response = httpx.request(method=method, url=url, headers=headers, json=body, timeout=10)
            response_data = response.json()

            logger.info("响应状态码: %d", response.status_code)
            if response_data.get("code") != 200:
                logger.error("请求失败: %s", response_data.get("message"))
                raise Exception(response_data.get("message"))

            return response_data
        except Exception as e:
            logger.error("请求出错: %s", str(e))
            raise

    def sign_in(self, email: str, password: str) -> str:
        body = {"email": email, "password": password}
        logger.info("开始登录用户 %s...", email)
        res = self._send_request(self.API_PATH["sign_in"], self.POST, body)
        logger.info("用户 %s 登录成功，获取到Token", email)
        return res["data"]["token"]

    def punch_in(self, token: str):
        logger.info("开始打卡...")
        res = self._send_request(self.API_PATH["punch_in"], self.POST, token=token)
        logger.info("打卡响应: %s", res)
        return res["data"]["res"]

def parse_accounts(account_list: str) -> List[Dict[str, str]]:
    """解析账号列表"""
    accounts = []
    for pair in account_list.split(","):
        username, password = pair.split(":")
        accounts.append({"username": username.strip(), "password": password.strip()})
    return accounts

def send_email(email_config: Dict, subject: str, content: str):
    """发送邮件"""
    try:
        msg = MIMEMultipart()
        msg["From"] = email_config["sender_email"]
        msg["To"] = email_config["receiver_email"]
        msg["Subject"] = subject

        msg.attach(MIMEText(content, "plain", "utf-8"))

        with smtplib.SMTP_SSL(email_config["smtp_server"], email_config["port"]) as server:
            server.login(email_config["sender_email"], email_config["password"])
            server.send_message(msg)

        logger.info("邮件通知已发送")
    except Exception as e:
        logger.error("邮件发送失败: %s", str(e))

def process_accounts(account_list: str, email_config: Dict):
    """处理账户签到"""
    accounts = parse_accounts(account_list)
    bika = BiKa()
    results = []

    for account in accounts:
        username = account["username"]
        password = account["password"]

        try:
            current_token = bika.sign_in(username, password)
            result = bika.punch_in(current_token)

            if result["status"] == "ok":
                msg = f"用户 {username} 打卡成功, 最后一次打卡: {result['punchInLastDay']}"
                logger.info(msg)
                results.append(msg)
            else:
                msg = f"用户 {username} 重复签到 - Already punch-in"
                logger.warning(msg)
                results.append(msg)
        except Exception as e:
            msg = f"用户 {username} 执行过程中出现错误: {str(e)}"
            logger.error(msg)
            results.append(msg)

        # 随机延迟
        time.sleep(random.uniform(5, 10))

    email_content = "\n".join(results)
    send_email(email_config, "哔咔打卡结果通知", email_content)

if __name__ == "__main__":
    account_list = os.getenv("ACCOUNT_LIST")  # 从环境变量读取账号列表
    email_config_json = os.getenv("EMAIL_CONFIG")  # 从环境变量读取邮箱配置JSON

    if not account_list or not email_config_json:
        logger.error("环境变量未配置: ACCOUNT_LIST 或 EMAIL_CONFIG")
        exit(1)

    email_config = json.loads(email_config_json)  # 解析JSON
    process_accounts(account_list, email_config)

