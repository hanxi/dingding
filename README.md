# 钉钉机器人库

异步钉钉机器人库，支持消息推送和接收功能。

## 功能特性

- ✅ **异步消息推送**：使用 aiohttp 实现高性能异步发送
- ✅ **Markdown 格式**：支持发送 Markdown 格式消息
- ✅ **@功能**：支持@特定用户或@所有人
- ✅ **消息接收**：内置 HTTP 服务器接收钉钉回调消息
- ✅ **Token 认证**：支持请求 token 验证
- ✅ **完善日志**：详细的日志记录

## 安装

```bash
# 使用 uv 安装依赖并同步项目
uv sync

# 安装项目到虚拟环境（可编辑模式）
uv pip install -e .
```

## 运行示例

```bash
# 运行示例代码
uv run python examples/example.py

# 或直接使用虚拟环境的 Python
source .venv/bin/activate
python examples/example.py
```

## 快速开始

### 消息推送

```python
import asyncio
from dingding import DingDingRobot

async def main():
    # 初始化机器人
    robot = DingDingRobot(
        access_token="你的 access_token",
        secret="你的 secret"
    )
    
    # 发送 Markdown 消息
    result = await robot.send_markdown_message(
        title="测试消息",
        text="### 这是一条测试消息\n- 内容 1\n- 内容 2",
        at_all=False
    )
    
    print(f"发送结果：{result}")

asyncio.run(main())
```

### 消息接收

```python
import asyncio
from dingding import DingDingReceiver

async def handle_message(message: dict):
    """处理接收到的消息"""
    print(f"收到消息：{message}")

async def main():
    # 创建接收器
    receiver = DingDingReceiver(
        host='0.0.0.0',
        port=8080,
        token='your_token'
    )
    
    # 设置回调
    receiver.set_callback(handle_message)
    
    # 启动服务器
    receiver.start()
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        receiver.stop()

asyncio.run(main())
```

## API 文档

### DingDingRobot

#### 初始化
```python
DingDingRobot(access_token: str, secret: str)
```

#### 发送消息
```python
async def send_markdown_message(
    title: str,
    text: str,
    at_mobiles: list[str] = None,
    at_all: bool = False
) -> dict
```

参数：
- `title`: 消息标题
- `text`: Markdown 格式的消息内容
- `at_mobiles`: 需要@的手机号列表，如 `["13800138000", "13900139000"]`
- `at_all`: 是否@所有人，默认 `False`

返回：
- `dict`: 钉钉 API 响应字典

### DingDingReceiver

#### 初始化
```python
DingDingReceiver(host: str = '0.0.0.0', port: int = 8080, token: str = '')
```

参数：
- `host`: 服务器监听地址，默认 `'0.0.0.0'`
- `port`: 服务器端口，默认 `8080`
- `token`: 用于验证请求的 token

#### 设置回调
```python
def set_callback(callback: Callable[[dict], Awaitable[None]])
```

参数：
- `callback`: 异步回调函数，接收消息数据字典

#### 启动/停止
```python
def start()
def stop()
```

#### 异步接收消息
```python
async def receive_message(timeout: float = 60.0) -> dict
```

参数：
- `timeout`: 等待超时时间（秒），默认 60 秒

返回：
- `dict`: 接收到的消息数据

## 配置说明

### 获取机器人配置

1. 在钉钉群中添加自定义机器人
2. 获取 `access_token`（webhook URL 中）
3. 设置安全关键词或加签 secret
4. 复制配置到代码中

### 消息接收配置

1. 在钉钉机器人配置中设置回调地址
2. 设置 token 用于验证请求（通过 `X-DingTalk-Token` 头部传递）
3. 确保服务器可公网访问

## 开发

```bash
# 安装开发依赖
uv add --dev pytest pytest-asyncio

# 运行测试
uv run pytest
```

## 许可证

MIT License
