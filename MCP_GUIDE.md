# HY-MT MCP 使用指南

## 简介

HY-MT 提供 MCP (Model Context Protocol) 接口，允许通过程序化方式调用翻译服务。

## 配置

在 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "hy-mt": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "MODEL_NAME": "tencent/HY-MT1.5-1.8B",
        "GPU_IDLE_TIMEOUT": "300"
      }
    }
  }
}
```

或使用 Docker：

```json
{
  "mcpServers": {
    "hy-mt": {
      "command": "docker",
      "args": ["exec", "-i", "hy-mt", "python", "mcp_server.py"]
    }
  }
}
```

## 可用工具

### 1. translate_text - 翻译文本

```python
result = await mcp.call_tool("translate_text", {
    "text": "Hello, world!",
    "target_lang": "zh",
    "source_lang": "en",  # 可选
    "context": "技术文档",  # 可选
    "temperature": 0.7,
    "top_p": 0.6,
    "top_k": 20
})
# 返回: {"status": "success", "result": "你好，世界！"}
```

### 2. translate_with_terms - 术语干预翻译

```python
result = await mcp.call_tool("translate_with_terms", {
    "text": "The API uses cache to improve performance.",
    "target_lang": "zh",
    "terms": {
        "API": "接口",
        "cache": "缓存"
    }
})
# 返回: {"status": "success", "result": "该接口使用缓存来提高性能。"}
```

### 3. get_gpu_status - 获取 GPU 状态

```python
result = await mcp.call_tool("get_gpu_status", {})
# 返回: {"loaded": true, "gpu_free_mb": 30000, "gpu_total_mb": 46068, "idle_seconds": 120}
```

### 4. release_gpu - 释放 GPU 显存

```python
result = await mcp.call_tool("release_gpu", {})
# 返回: {"status": "success", "message": "GPU memory released"}
```

### 5. list_languages - 获取支持的语言

```python
result = await mcp.call_tool("list_languages", {})
# 返回: {"zh": "中文", "en": "English", "ja": "日本語", ...}
```

## 支持的语言代码

| 代码 | 语言 | 代码 | 语言 |
|------|------|------|------|
| zh | 中文 | en | English |
| ja | 日本語 | ko | 한국어 |
| fr | Français | de | Deutsch |
| es | Español | pt | Português |
| ru | Русский | ar | العربية |
| th | ไทย | vi | Tiếng Việt |
| zh-Hant | 繁體中文 | yue | 粵語 |

完整列表请调用 `list_languages` 工具。

## 与 API 的区别

| 特性 | API | MCP |
|------|-----|-----|
| 访问方式 | HTTP REST | 程序化调用 |
| 适用场景 | Web 应用集成 | AI Agent / 自动化 |
| 认证 | 可配置 | 本地进程 |
| 响应格式 | JSON | 结构化对象 |

## 注意事项

1. MCP 服务器与 Web 服务共享同一个 GPU 管理器
2. 首次调用会自动加载模型（约需 30 秒）
3. 空闲超时后会自动释放显存
4. 建议在批量翻译后调用 `release_gpu` 释放资源
