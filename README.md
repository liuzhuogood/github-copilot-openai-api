# GitHub Copilot OpenAI API

[![Docker Pulls](https://img.shields.io/docker/pulls/liuzhuogood/github-copilot-openai-api.svg)](https://hub.docker.com/r/liuzhuogood/github-copilot-openai-api)
[![Docker Image Size](https://img.shields.io/docker/image-size/liuzhuogood/github-copilot-openai-api/latest)](https://hub.docker.com/r/liuzhuogood/github-copilot-openai-api)
[![GitHub License](https://img.shields.io/github/license/liuzhuogood/github-copilot-openai-api)](https://github.com/liuzhuogood/github-copilot-openai-api/blob/main/LICENSE)

A lightweight and efficient bridge that transforms GitHub Copilot into an OpenAI-compatible API endpoint. This service enables seamless integration with any OpenAI API client, featuring streaming responses, multiple model support, and enterprise-grade security options. Perfect for developers looking to leverage GitHub Copilot's capabilities through a familiar API interface.

🔥 Turn GitHub Copilot into OpenAI API | 将 GitHub Copilot 转换为 OpenAI API

[English](#english) | [中文](#中文)

## 🐳 Docker Hub Quick Start | Docker Hub 快速开始

```bash
# Pull and run the image | 拉取并运行镜像
docker run -d -p 8000:8000 liuzhuogood/github-copilot-openai-api:latest

# With API key authentication | 使用 API 密钥认证
docker run -d -p 8000:8000 -e API_KEY=your_secret_key liuzhuogood/github-copilot-openai-api:latest
```

First time setup | 首次使用：
1. Visit/访问：http://localhost:8000/auth/device
2. Follow GitHub device auth flow | 按照 GitHub 设备认证流程操作
3. Start using the API | 开始使用 API

For detailed documentation, please visit our [GitHub Repository](https://github.com/liuzhuogood/github-copilot-openai-api).
更多详细文档，请访问我们的 [GitHub 仓库](https://github.com/liuzhuogood/github-copilot-openai-api)。

<a name="english"></a>
## 🌟 English

### Introduction
This project provides an OpenAI API-compatible interface by reverse engineering the GitHub Copilot API. It allows you to use GitHub Copilot's capabilities through a standard OpenAI API interface, supporting streaming output and multiple models.

### 🚀 Features
- OpenAI API compatibility
- Streaming response support
- Multiple model support
- Device authentication flow
- Docker deployment support
- API key authentication (optional)

### 🛠 Tech Stack
- FastAPI: High-performance web framework
- Python 3.12+: Latest Python features
- Docker: Containerization
- Uvicorn: ASGI server
- aiohttp: Async HTTP client
- Jinja2: Template engine

### 📝 Quick Start

#### Using Docker (Recommended)
```bash
docker run -d -p 8000:8000 liuzhuogood/github-copilot-openai-api:latest
```

With API key authentication:
```bash
docker run -d -p 8000:8000 -e API_KEY=your_secret_key liuzhuogood/github-copilot-openai-api:latest
```

#### Building from Source
```bash
# Clone the repository
git clone https://github.com/liuzhuogood/github-copilot-openai-api.git
cd github-copilot-openai-api

# Build Docker image
docker build -t github-copilot-openai-api .

# Run container
docker run -d -p 8000:8000 github-copilot-openai-api
```

### 🔧 Configuration
Environment variables:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `API_KEY`: Optional API key for authentication

### 📚 API Usage
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Hello, who are you?"
      }
    ],
    "stream": true
  }'
```

### 🎯 Supported Models
- gpt-4
- o3-mini
- o1
- gemini-2.0-flash-001
- claude-3.5-sonnet
- claude-3.7-sonnet

### 🔐 First-time Setup
1. Visit http://localhost:8000/auth/device
2. Follow the GitHub device authentication flow
3. Once authorized, the service will automatically use the GitHub Copilot token

---

<a name="中文"></a>
## 🌟 中文

### 简介
本项目通过逆向工程 GitHub Copilot API，提供了一个与 OpenAI API 兼容的接口。它允许你通过标准的 OpenAI API 接口使用 GitHub Copilot 的功能，支持流式输出和多种模型。

### 🚀 特性
- OpenAI API 兼容
- 支持流式响应
- 支持多种模型
- 设备认证流程
- Docker 部署支持
- API 密钥认证（可选）

### 🛠 技术栈
- FastAPI：高性能 Web 框架
- Python 3.12+：使用最新的 Python 特性
- Docker：容器化部署
- Uvicorn：ASGI 服务器
- aiohttp：异步 HTTP 客户端
- Jinja2：模板引擎

### 📝 快速开始

#### 使用 Docker（推荐）
```bash
docker run -d -p 8000:8000 liuzhuogood/github-copilot-openai-api:latest
```

使用 API 密钥认证：
```bash
docker run -d -p 8000:8000 -e API_KEY=your_secret_key liuzhuogood/github-copilot-openai-api:latest
```

#### 从源码构建
```bash
# 克隆仓库
git clone https://github.com/liuzhuogood/github-copilot-openai-api.git
cd github-copilot-openai-api

# 构建 Docker 镜像
docker build -t github-copilot-openai-api .

# 运行容器
docker run -d -p 8000:8000 github-copilot-openai-api
```

### 🔧 配置
环境变量：
- `HOST`：服务器监听地址（默认：0.0.0.0）
- `PORT`：服务器监听端口（默认：8000）
- `API_KEY`：可选的 API 密钥认证

### 📚 API 使用
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "你好，请问你是谁？"
      }
    ],
    "stream": true
  }'
```

### 🎯 支持的模型
- gpt-4
- o3-mini
- o1
- gemini-2.0-flash-001
- claude-3.5-sonnet
- claude-3.7-sonnet

### 🔐 首次使用
1. 访问 http://localhost:8000/auth/device
2. 按照 GitHub 设备认证流程进行操作
3. 认证成功后，服务将自动使用 GitHub Copilot 令牌 