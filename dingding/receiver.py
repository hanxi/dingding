"""
钉钉机器人异步消息接收模块
使用 asyncio 和 http.server 实现异步 HTTP 服务器

验证方式：简单比较 token 是否相等
"""

import asyncio
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional, Awaitable
from threading import Thread

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

class DingDingRequestHandler(BaseHTTPRequestHandler):
    """处理钉钉回调请求的 HTTP 处理器"""

    token: str = ""
    callback: Optional[Callable[[dict], Awaitable[None]]] = None
    message_queue: Optional[asyncio.Queue] = None

    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"HTTP 请求：{args[0]}")

    def do_POST(self):
        """处理 POST 请求"""
        # 验证 token（从请求头中获取）
        request_token = self.headers.get("token", "")
        
        if request_token != self.token:
            logger.warning(f"❌ Token 验证失败 | 请求：'{request_token}' | 期望：'{self.token}'")
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
            return
        
        logger.info("✅ Token 验证通过")

        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body)
            logger.info(f"📥 收到钉钉消息：{data.get('msgtype', 'unknown')}")

            # 将消息放入队列（供 receive_message 使用）
            if self.message_queue:
                self.message_queue.put_nowait(data)

            # 异步调用回调函数
            if self.callback:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.callback(data))
                finally:
                    loop.close()

            # 返回成功响应
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))

        except json.JSONDecodeError:
            logger.error("❌ JSON 解析失败")
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))


class DingDingReceiver:
    """钉钉消息异步接收器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080, token: str = ""):
        """
        初始化消息接收器

        :param host: 服务器监听地址
        :param port: 服务器端口
        :param token: 用于验证请求的 token
        """
        self.host = host
        self.port = port
        self.token = token
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[Thread] = None
        self.callback: Optional[Callable[[dict], Awaitable[None]]] = None

    def set_callback(self, callback: Callable[[dict], Awaitable[None]]):
        """
        设置消息处理回调函数

        :param callback: 异步回调函数，接收消息数据字典
        """
        self.callback = callback
        DingDingRequestHandler.callback = callback

    def start(self):
        """启动 HTTP 服务器（非阻塞）"""
        # 初始化消息队列
        self._message_queue = asyncio.Queue()
        DingDingRequestHandler.token = self.token
        DingDingRequestHandler.message_queue = self._message_queue

        self.server = HTTPServer((self.host, self.port), DingDingRequestHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        logger.info(f"🚀 消息接收服务器已启动 | 地址：http://{self.host}:{self.port}")

    def stop(self):
        """停止 HTTP 服务器"""
        if self.server:
            self.server.shutdown()
            self.server = None
            logger.info("🛑 消息接收服务器已停止")

    async def receive_message(self, timeout: float = 60.0) -> dict:
        """
        异步等待接收消息（使用 asyncio.Queue 实现）

        :param timeout: 等待超时时间（秒）
        :return: 接收到的消息数据
        """
        if not hasattr(self, "_message_queue"):
            self._message_queue = asyncio.Queue()

        try:
            message = await asyncio.wait_for(self._message_queue.get(), timeout=timeout)
            return message
        except asyncio.TimeoutError:
            logger.warning(f"⏰ 等待消息超时（{timeout}秒）")
            raise
