"""
钉钉机器人工具函数模块
提供签名生成、token 验证等公共功能
"""

import time
import hmac
import hashlib
import base64
import urllib.parse


def generate_signature(secret: str) -> tuple[str, str]:
    """
    生成钉钉 API 请求签名

    :param secret: 机器人安全设置的加签 secret
    :return: (timestamp, sign) 元组
    """
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode("utf-8"))
    return timestamp, sign


def verify_token(token: str, expected_token: str) -> bool:
    """
    验证请求 token 是否匹配

    :param token: 请求中的 token
    :param expected_token: 期望的 token
    :return: 是否匹配
    """
    return hmac.compare_digest(token, expected_token)
