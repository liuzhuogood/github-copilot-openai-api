import json
import os

import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.requests import Request
from starlette.responses import StreamingResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from api.chat_stream import run_stream, run
from auth.device_auth import DeviceAuth

app = FastAPI(title="GitHub Copilot API")

DEFAULT_API_KEY=""

# 设置模板
templates = Jinja2Templates(directory="templates")

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """重定向到设备认证页面"""
    return RedirectResponse(url="/auth/device")

@app.get("/auth/device", response_class=HTMLResponse)
async def device_auth(request: Request):
    """设备认证页面"""
    auth = DeviceAuth()
    auth_info = await auth.new_get_token()
    
    if "error" in auth_info:
        return HTMLResponse(content=f"<h1>错误</h1><p>{auth_info['error']}</p>")
    
    return templates.TemplateResponse(
        "auth.html", 
        {
            "request": request, 
            "user_code": auth_info["user_code"],
            "verification_uri": auth_info["verification_uri"],
            "device_code": auth_info["device_code"]
        }
    )
      

@app.post("/auth/confirm/{device_code}")
async def confirm_auth(device_code: str):
    """确认认证"""
    auth = DeviceAuth()
    result = await auth.confirm_token(device_code)
    return JSONResponse(content=result)

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """处理聊天完成请求，支持 OpenAI API 兼容的流式输出"""
    try:
        logger.debug("Received request: {}", str(await request.body(), encoding="utf-8"))
        # 校验header
        headers = request.headers
        api_key = headers.get("Authorization")
        server_auth_key=os.getenv("API_KEY",DEFAULT_API_KEY)
        if server_auth_key:
            if not api_key:
                return {"error": {"message": "invalid token", "type": "invalid_request_error"}}, 401
            if api_key != server_auth_key:
                return {"error": {"message": "invalid token", "type": "invalid_request_error"}}, 401

        data = await request.json()
        messages = data.get("messages", [])
        stream = data.get("stream", False)
        if not messages:
            logger.debug("No messages received")
            return {"error": {"message": "no messages found", "type": "invalid_request_error"}}, 400

        if stream:
            # 处理流式请求
            # 设置 SSE 响应头
            headers = {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no"
            }

            async def event_generator():
                try:
                    async for chunk in run_stream(data):
                        logger.debug(chunk)
                        yield chunk
                except Exception as e:
                    logger.exception("Exception occurred: {}", e)
                    error_response = json.dumps({"error": {"message": str(e), "type": "stream_error"}})
                    yield f"data: {error_response}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers=headers
            )
        else:
            # 处理非流式请求
            try:
                response = await run(data)
                logger.debug(f"Non-streaming response: {response}")
                return JSONResponse(content=response)
            except Exception as e:
                logger.exception("Exception occurred: {}", e)
                return JSONResponse(
                    status_code=500,
                    content={"error": {"message": str(e), "type": "server_error"}}
                )
    except ValueError as e:
        logger.exception("Exception occurred: {}", e)
        return JSONResponse(
            status_code=401,
            content={"error": {"message": str(e), "type": "auth_error"}}
        )
    except Exception as e:
        logger.exception("Exception occurred: {}", e)
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "type": "server_error"}}
        )


@app.get("/v1/models")
async def models():
    """返回支持的模型列表"""
    return {
        "object": "list",
        "data": [
            {"id": "gpt-4", "object": "model"},
            {"id": "o3-mini", "object": "model"},
            {"id": "o1", "object": "model"},
            {"id": "gemini-2.0-flash-001", "object": "model"},
            {"id": "claude-3.5-sonnet", "object": "model"},
            {"id": "claude-3.7-sonnet", "object": "model"},
        ]
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", 8000)
    logger.debug(f"Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
