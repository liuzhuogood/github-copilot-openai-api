from functools import cache
from typing import Optional, AsyncGenerator, Dict, Any

import async_lru

from api.chat_api import ChatAPI
from auth.device_auth import DeviceAuth
from auth.envs_auth import EnvsAuth
from auth.hosts_auth import HostsAuth


async def get_token() -> Optional[str]:
    """获取认证令牌"""
    auth_methods = [
        EnvsAuth(),
        HostsAuth(),
        DeviceAuth(),
    ]

    for auth in auth_methods:
        if token := await auth.get_token():
            return token
    return None


async def run_stream(
        data: dict
) -> AsyncGenerator[str, None]:
    """运行流式聊天，返回符合 OpenAI SSE 规范的数据流"""
    token = await get_token()
    if not token:
        raise ValueError("未能获取有效的认证令牌")

    chat = ChatAPI(token)
    messages = data.get("messages", [])
    model = data.get("model", "gpt-4")
    temperature = data.get("temperature", 0.7)
    if not messages:
        raise ValueError("not found any message")
    # 规范化消息格式
    normalized_messages = []
    for msg in messages:
        if isinstance(msg.get("content"), list):
            content = next((item["text"] for item in msg["content"] if isinstance(item, dict) and "text" in item), "")
        else:
            content = msg.get("content", "")

        normalized_messages.append({
            "content": content,
            "role": msg.get("role", "user")
        })

    async for chunk in chat.stream_chat(normalized_messages, model=model, temperature=temperature):
        yield chunk


async def run(
        data: dict
) -> Dict[str, Any]:
    """运行非流式聊天，返回完整的响应"""
    token = await get_token()
    if not token:
        raise ValueError("未能获取有效的认证令牌")

    chat = ChatAPI(token)
    messages = data.get("messages", [])
    model = data.get("model", "gpt-4")
    temperature = data.get("temperature", 0.7)
    if not messages:
        raise ValueError("not found any message")
    
    # 规范化消息格式
    normalized_messages = []
    for msg in messages:
        if isinstance(msg.get("content"), list):
            content = next((item["text"] for item in msg["content"] if isinstance(item, dict) and "text" in item), "")
        else:
            content = msg.get("content", "")

        normalized_messages.append({
            "content": content,
            "role": msg.get("role", "user")
        })

    return await chat.chat(normalized_messages, model=model, temperature=temperature)
