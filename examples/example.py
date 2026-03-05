"""
钉钉机器人库使用示例
展示异步消息推送和接收功能
"""

import asyncio
from dingding import DingDingRobot, DingDingReceiver


async def handle_message(message: dict):
    """处理接收到的钉钉消息"""
    print(f"📥 收到消息：{message}")
    # 这里可以添加自定义的消息处理逻辑


async def main():
    # ========== 消息推送示例 ==========
    print("=== 消息推送示例 ===")

    # 替换为你的实际配置
    ACCESS_TOKEN = "你的机器人 access_token"
    SECRET = "你的机器人 secret"

    # 方式 1：使用类
    robot = DingDingRobot(ACCESS_TOKEN, SECRET)
    try:
        result = await robot.send_markdown_message(
            title="测试消息",
            text="### 这是一条测试消息\n- 内容 1\n- 内容 2",
            at_all=False,
        )
        print(f"发送结果：{result}")
    except Exception as e:
        print(f"发送失败：{e}")

    # ========== 消息接收示例 ==========
    print("\n=== 消息接收示例 ===")

    # 创建接收器
    receiver = DingDingReceiver(host="0.0.0.0", port=8080, token="your_token")

    # 设置消息处理回调
    receiver.set_callback(handle_message)

    # 启动服务器
    receiver.start()

    print("服务器已启动，按 Ctrl+C 停止...")

    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        receiver.stop()
        print("服务器已停止")


if __name__ == "__main__":
    asyncio.run(main())
