from typing import List, Dict, Any, AsyncGenerator, Union
import time
import json
import aiohttp
import async_lru
from loguru import logger


class ChatAPI:
    """聊天 API 实现"""

    def __init__(self, token):
        self.token = token

    async def stream_chat(
            self,
            messages: List[Dict[str, str]],
            model: str = "gpt-4",
            temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """将 GitHub Copilot API 转换为 OpenAI API 兼容的流式聊天接口"""
        # 首先获取 Copilot token
        copilot_token = await self.get_copilot_token()
        if not copilot_token:
            raise ValueError("No Copilot token")

        headers = {
            "authorization": f"Bearer {copilot_token}",
            "accept-language": "en-US,en;q=0.9",
            "editor-plugin-version": "copilot-chat/0.25.2025021001",
            "openai-intent": "conversation-panel",
            "editor-version": "vscode/1.98.0-insider",
            "content-type": "application/json",
            "accept": "text/event-stream",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url="https://api.githubcopilot.com/chat/completions",
                    headers=headers,
                    json={
                        "messages": messages,
                        "model": model,
                        "temperature": temperature,
                        "stream": True,
                    }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"status code ：{response.status}，error message：{error_text}")

                async for line in response.content:
                    try:
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue

                        if not line.startswith('data: '):
                            continue

                        data = line[6:].strip()
                        if data == '[DONE]':
                            yield 'data: [DONE]\n\n'
                            break

                        chunk = json.loads(data)
                        if not chunk.get('choices'):
                            continue

                        content = chunk['choices'][0].get('delta', {}).get('content', '')
                        if not content:
                            continue

                        response_chunk = {
                            'id': f"chatcmpl-{int(time.time() * 1000)}",
                            'object': 'chat.completion.chunk',
                            'created': int(time.time()),
                            'model': model,
                            'choices': [
                                {
                                    'index': 0,
                                    'delta': {'content': content},
                                    'finish_reason': None
                                }
                            ]
                        }
                        yield f"data: {json.dumps(response_chunk)}\n\n"

                    except Exception as e:
                        continue

    @async_lru.alru_cache(ttl=2 * 60 * 60)
    async def get_copilot_token(self) -> str:
        """获取 Copilot token"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url="https://api.github.com/copilot_internal/v2/token",
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Accept": "application/json",
                        "User-Agent": "Mozilla/5.0",
                    }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(
                        f"Get token error, status code: {response.status}, error messaget Copilot: {error_text}")

                data = await response.json()
                token = data.get("token")
                logger.info(f"Get Copilot token: {token}")
                if not token:
                    raise ValueError("No token")
                return token

    async def chat(
            self,
            messages: List[Dict[str, str]],
            model: str = "gpt-4",
            temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """非流式聊天接口，返回完整的响应"""
        # 首先获取 Copilot token
        copilot_token = await self.get_copilot_token()
        if not copilot_token:
            raise ValueError("No Copilot token")

        headers = {
            "authorization": f"Bearer {copilot_token}",
            "accept-language": "en-US,en;q=0.9",
            "editor-plugin-version": "copilot-chat/0.25.2025021001",
            "openai-intent": "conversation-panel",
            "editor-version": "vscode/1.98.0-insider",
            "content-type": "application/json",
            "accept": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url="https://api.githubcopilot.com/chat/completions",
                    headers=headers,
                    json={
                        "messages": messages,
                        "model": model,
                        "temperature": temperature,
                        "stream": False,
                    }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"status code：{response.status}，error message：{error_text}")

                response_data = await response.json()
                
                # 构造符合 OpenAI API 规范的响应格式
                return {
                    "id": f"chatcmpl-{int(time.time() * 1000)}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                            },
                            "finish_reason": response_data.get("choices", [{}])[0].get("finish_reason", "stop")
                        }
                    ],
                    "usage": response_data.get("usage", {})
                }
