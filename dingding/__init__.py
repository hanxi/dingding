"""
钉钉机器人库
支持异步消息推送和接收
"""
from .sender import DingDingRobot
from .receiver import DingDingReceiver

__version__ = "0.1.0"
__all__ = [
    "DingDingRobot",
    "DingDingReceiver",
]
