"""
钉钉机器人异步消息推送模块
使用 aiohttp 实现异步 HTTP 请求
"""

import aiohttp
import logging
from typing import Optional

from .utils import generate_signature

# 配置基础日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class DingDingRobot:
    """钉钉自定义机器人（异步 Markdown 消息专用）"""

    def __init__(self, access_token: str, secret: str):
        """
        初始化钉钉机器人

        :param access_token: 机器人 webhook 中的 access_token
        :param secret: 机器人安全设置的加签 secret
        """
        self.access_token = access_token
        self.secret = secret
        self.base_url = "https://oapi.dingtalk.com/robot/send"

    def _generate_signature(self) -> tuple[str, str]:
        """生成签名（timestamp + sign）"""
        return generate_signature(self.secret)

    async def send_markdown_message(
        self,
        title: str,
        text: str,
        at_mobiles: Optional[list[str]] = None,
        at_all: bool = False,
    ) -> dict:
        """
        异步发送 Markdown 格式消息到钉钉群

        :param title: 消息标题（钉钉列表显示）
        :param text: Markdown 格式的消息内容
        :param at_mobiles: 需要@的手机号列表，如 ["13800138000", "13900139000"]
        :param at_all: 是否@所有人，默认 False
        :return: 钉钉 API 响应字典
        """
        # 生成签名
        timestamp, sign = self._generate_signature()

        # 构造完整请求 URL
        url = (
            f"{self.base_url}?access_token={self.access_token}"
            f"&timestamp={timestamp}&sign={sign}"
        )

        # 构造消息体
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"atMobiles": at_mobiles or [], "isAtAll": at_all},
        }

        # 异步发送请求
        headers = {"Content-Type": "application/json; charset=utf-8"}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url=url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if result.get("errcode") != 0:
                        raise Exception(f"钉钉接口返回错误：{result}")

                    logger.info(f"✅ Markdown 消息发送成功 | 标题：{title}")
                    return result

            except aiohttp.ClientTimeout:
                logger.error("❌ 钉钉消息发送超时（10 秒）")
                raise
            except aiohttp.ClientConnectionError:
                logger.error("❌ 钉钉消息发送失败：网络连接错误")
                raise
            except Exception as e:
                logger.error(f"❌ 钉钉消息发送失败：{str(e)}")
                raise
