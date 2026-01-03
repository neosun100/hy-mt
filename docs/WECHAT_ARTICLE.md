# 一条命令部署腾讯混元翻译大模型，支持38种语言，All-in-One Docker方案

> 本地私有化部署翻译服务，告别API调用费用，数据安全有保障

## 前言

最近腾讯开源了 HunyuanMT (混元翻译) 大模型，支持38种语言互译，翻译质量相当不错。但官方只提供了模型权重，要真正用起来还需要自己搭建服务。

于是我花了点时间，把它打包成了一个 **All-in-One Docker 镜像**，一条命令就能跑起来，还附带了 Web UI、REST API 和 MCP Server。

**项目地址**: https://github.com/neosun100/hy-mt

## 为什么要私有化部署翻译服务？

1. **数据安全** - 敏感文档不用上传到第三方服务器
2. **无调用限制** - 不受 API 配额和速率限制
3. **零边际成本** - 一次部署，无限使用
4. **离线可用** - 内网环境也能用

## 一条命令启动

```bash
docker run -d --gpus all -p 8021:8021 --name hy-mt neosun/hy-mt:latest
```

然后访问 `http://localhost:8021` 就能看到 Web UI 了。

没错，就这么简单。镜像里已经包含了所有模型（约43GB），下载完就能直接用，不需要再从 HuggingFace 下载任何东西。

## 功能亮点

### 🌐 38种语言支持

中文、英语、日语、韩语、法语、德语、西班牙语、葡萄牙语、俄语、阿拉伯语、泰语、越南语... 基本覆盖了主流语言。

### 🎨 现代化 Web UI

- 深色/浅色主题一键切换
- 拖拽上传文件翻译
- 实时显示翻译进度
- 支持术语干预（专业领域翻译必备）

### ⚡ 流式翻译

长文本翻译时，结果会实时流式输出，不用干等着。基于 Server-Sent Events (SSE) 实现。

### 🔀 多模型切换

内置4个模型，可以根据需求在 UI 或 API 中切换：

| 模型 | 显存需求 | 特点 |
|------|----------|------|
| **HY-MT 7B** | 16GB | 🏆 推荐，质量最高，速度也快 |
| HY-MT 1.8B | 6GB | 速度最快，质量也不错 |
| HY-MT 7B FP8 | 10GB | 7B质量，省显存 |
| HY-MT 1.8B FP8 | 4GB | 最省显存 |

### 🤖 MCP Server 支持

可以集成到 Claude Desktop 等支持 MCP 协议的 AI 助手中，让 AI 直接调用翻译能力。

## 性能实测

在 NVIDIA L40S GPU 上测试，英译中：

| 文本长度 | HY-MT 7B | HY-MT 1.8B |
|----------|----------|------------|
| 短文本 (61字符) | 0.4秒 | 0.4秒 |
| 中等文本 (530字符) | 4.4秒 | 3.6秒 |
| 长文本 (1.8K字符) | 17.7秒 | 14.0秒 |
| 超长文本 (4.2K字符) | 43.0秒 | 32.3秒 |

7B 模型只比 1.8B 慢 20-30%，但翻译质量明显更好，所以默认使用 7B。

## API 调用示例

### 基础翻译

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "zh"
  }'
```

返回：
```json
{
  "status": "success",
  "result": "你好，你好吗？",
  "elapsed_ms": 358,
  "model": "tencent/HY-MT1.5-7B"
}
```

### 术语干预

翻译专业文档时，可以指定术语映射：

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple released iPhone 16",
    "target_lang": "zh",
    "terms": {"Apple": "苹果公司", "iPhone": "苹果手机"}
  }'
```

返回：`苹果公司发布了苹果手机16`

### 流式翻译

```bash
curl -N "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Long article...", "target_lang": "zh", "stream": true}'
```

## 完整 API 列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/translate` | POST | 翻译文本（支持流式） |
| `/api/translate/file` | POST | 上传文件翻译 |
| `/api/translate/batch` | POST | 批量翻译 |
| `/api/models` | GET | 获取模型列表 |
| `/api/models/switch` | POST | 切换模型 |
| `/api/languages` | GET | 支持的语言列表 |
| `/api/gpu/status` | GET | GPU 状态 |
| `/docs` | GET | Swagger 文档 |

## 环境要求

- NVIDIA GPU，显存 6GB 以上（推荐 16GB 以上用 7B 模型）
- Docker + nvidia-docker
- CUDA 11.8+

## 一些技术细节

### 为什么 FP8 量化模型反而更慢？

这是个反直觉的现象。FP8 量化的目的是**省显存**，不是加速。

FP8 模型存储为 8-bit，但 GPU 计算时需要动态解压成 16-bit，这个解压过程在每个 token 生成时都会发生，所以反而更慢。

**结论**：显存够用就用基础模型，FP8 是给显存不够的用户准备的。

### 长文本优化

经过测试，chunk size 设为 150 字符时翻译质量最好。太大会导致输出混乱，太小会影响上下文理解。

## 写在最后

这个项目的目标是让大家能**零门槛**地私有化部署翻译服务。

如果觉得有用，欢迎 Star ⭐

**GitHub**: https://github.com/neosun100/hy-mt  
**Docker Hub**: https://hub.docker.com/r/neosun/hy-mt

---

*扫码关注，获取更多 AI 工具和技术分享*
