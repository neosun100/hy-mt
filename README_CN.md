<p align="center">
  <img src="imgs/hunyuanlogo.png" width="400"/>
</p>

<p align="center">
  <a href="README.md">English</a> | <b>简体中文</b> | <a href="README_TW.md">繁體中文</a> | <a href="README_JP.md">日本語</a>
</p>

<p align="center">
  <a href="https://hub.docker.com/r/neosun/hy-mt"><img src="https://img.shields.io/docker/pulls/neosun/hy-mt?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <a href="https://github.com/neosun100/hy-mt/stargazers"><img src="https://img.shields.io/github/stars/neosun100/hy-mt?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/neosun100/hy-mt/blob/main/License.txt"><img src="https://img.shields.io/badge/license-Tencent_Hunyuan-blue?style=flat-square" alt="License"></a>
  <a href="https://huggingface.co/tencent/HY-MT1.5-1.8B"><img src="https://img.shields.io/badge/🤗-HuggingFace-yellow?style=flat-square" alt="HuggingFace"></a>
</p>

# HY-MT 翻译服务

> 🚀 腾讯混元 HY-MT1.5-1.8B 翻译模型的 All-in-One Docker 部署方案，集成 Web UI、REST API 和 MCP Server。

## ✨ 功能特性

- 🌐 **38 种语言支持** - 中文、英语、日语、韩语、法语、德语、西班牙语等
- 🎨 **现代化 Web UI** - 深色/浅色主题切换、拖拽上传、实时进度显示
- ⚡ **流式翻译** - Server-Sent Events (SSE) 实时输出，长文本翻译体验更佳
- 🔧 **完整参数控制** - Temperature、Top-P、Top-K、重复惩罚等参数可调
- 📚 **术语干预** - 自定义术语映射，适用于专业领域翻译
- 🤖 **MCP Server** - 支持 Model Context Protocol，可集成 Claude 等 AI 助手
- 🐳 **一键部署** - All-in-One Docker 镜像，模型自动下载
- 🔄 **智能 GPU 管理** - 自动选择 GPU、空闲超时释放显存

## 📸 界面截图

<p align="center">
  <img src="docs/images/ui-screenshot.png" width="800"/>
</p>

## 🚀 快速开始

### 方式一：Docker Run（推荐）

```bash
# 一条命令启动
docker run -d --gpus all \
  -p 8021:8021 \
  -v ./models:/app/models \
  --name hy-mt \
  neosun/hy-mt:latest

# 访问 Web UI
open http://localhost:8021
```

首次运行会自动下载模型（约 3.5GB）。

### 方式二：Docker Compose

创建 `docker-compose.yml`：

```yaml
services:
  hy-mt:
    image: neosun/hy-mt:latest
    container_name: hy-mt
    ports:
      - "8021:8021"
    environment:
      - MODEL_NAME=tencent/HY-MT1.5-1.8B
      - GPU_IDLE_TIMEOUT=300
      - HF_ENDPOINT=https://hf-mirror.com  # 国内镜像加速
    volumes:
      - ./models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

```bash
docker compose up -d
```

### 方式三：本地开发运行

```bash
# 克隆仓库
git clone https://github.com/neosun100/hy-mt.git
cd hy-mt

# 安装依赖
pip install torch transformers accelerate fastapi uvicorn

# 启动服务
python -m uvicorn app_fastapi:app --host 0.0.0.0 --port 8021
```

## 📋 环境要求

| 要求 | 最低配置 | 推荐配置 |
|------|----------|----------|
| GPU | NVIDIA GPU 6GB+ 显存 | 8GB+ 显存 |
| CUDA | 11.8+ | 12.4+ |
| Docker | 20.10+ | 24.0+ |
| nvidia-docker | 必需 | - |

### 验证 GPU 支持

```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 8021 | 服务端口 |
| `MODEL_NAME` | tencent/HY-MT1.5-1.8B | HuggingFace 模型名称 |
| `MODEL_PATH` | ./models | 本地模型缓存路径 |
| `GPU_IDLE_TIMEOUT` | 300 | GPU 空闲超时自动释放（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 自动 | GPU ID（留空自动选择） |
| `HF_ENDPOINT` | https://huggingface.co | HuggingFace 镜像地址 |

### 使用 .env 文件

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
vim .env
```

## 📖 API 使用

### 基础翻译

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "zh"
  }'
```

响应：
```json
{
  "status": "success",
  "result": "你好，你好吗？",
  "elapsed_ms": 1234,
  "chunks": 1
}
```

### 流式翻译（SSE）

```bash
curl -N "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "需要翻译的长文章...",
    "target_lang": "en",
    "stream": true
  }'
```

### 术语干预

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple released iPhone 16",
    "target_lang": "zh",
    "terms": {"Apple": "苹果公司", "iPhone": "苹果手机"}
  }'
```

### 文件上传翻译

```bash
curl "http://localhost:8021/api/translate/file" \
  -F "file=@document.txt" \
  -F "target_lang=zh" \
  -F "stream=true"
```

## 📚 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web UI 界面 |
| `/api/translate` | POST | 文本翻译（支持流式） |
| `/api/translate/file` | POST | 文件上传翻译 |
| `/api/translate/batch` | POST | 批量翻译 |
| `/api/languages` | GET | 支持的语言列表 |
| `/api/gpu/status` | GET | GPU 状态和显存信息 |
| `/api/gpu/offload` | POST | 释放 GPU 显存 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger API 文档 |

## 🔑 关键优化：分段大小

**重要发现**：分段越小，翻译质量越好

| 分段大小 | 质量 | 说明 |
|----------|------|------|
| 500 字符 | ❌ 差 | 中英混杂 |
| 300 字符 | ⚠️ 一般 | 部分未翻译 |
| **150 字符** | ✅ 优秀 | 翻译完整准确 |

服务默认使用 `MAX_CHUNK_LENGTH=150` 以获得最佳质量。

详见 [优化指南](docs/OPTIMIZATION_GUIDE.md)。

## 🌍 支持的语言

| 语言 | 代码 | 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|------|------|
| 中文 | zh | 英语 | en | 日语 | ja |
| 韩语 | ko | 法语 | fr | 德语 | de |
| 西班牙语 | es | 葡萄牙语 | pt | 俄语 | ru |
| 阿拉伯语 | ar | 泰语 | th | 越南语 | vi |
| 意大利语 | it | 荷兰语 | nl | 波兰语 | pl |
| 土耳其语 | tr | 印尼语 | id | 马来语 | ms |
| 印地语 | hi | 繁体中文 | zh-Hant | 粤语 | yue |

以及更多 17 种语言，完整列表见 `/api/languages`。

## 🛠️ 技术栈

- **模型**: [Tencent HY-MT1.5-1.8B](https://huggingface.co/tencent/HY-MT1.5-1.8B)
- **后端**: FastAPI + Uvicorn
- **前端**: 原生 JS + 深色/浅色主题
- **容器**: NVIDIA CUDA 12.4 基础镜像
- **流式**: Server-Sent Events (SSE)
- **MCP**: Model Context Protocol AI 集成

## 📁 项目结构

```
hy-mt/
├── app_fastapi.py      # FastAPI 主应用
├── mcp_server.py       # MCP Server（AI 助手集成）
├── templates/
│   └── index.html      # Web UI（深色/浅色主题）
├── docs/
│   ├── OPTIMIZATION_GUIDE.md  # 长文本优化指南
│   └── QUICK_REFERENCE.md     # API 快速参考
├── Dockerfile          # All-in-One Docker 构建
├── docker-compose.yml  # Docker Compose 配置
├── start.sh           # 快速启动脚本
├── test_api.sh        # API 测试脚本
└── .env.example       # 环境变量模板
```

## 🔧 高级用法

### MCP Server 集成

在 Claude Desktop 等 AI 助手中使用，添加 MCP 配置：

```json
{
  "mcpServers": {
    "hy-mt": {
      "command": "python",
      "args": ["/path/to/hy-mt/mcp_server.py"],
      "env": {
        "HY_MT_API": "http://localhost:8021"
      }
    }
  }
}
```

详见 [MCP_GUIDE.md](MCP_GUIDE.md)。

## 🐛 故障排除

| 问题 | 解决方案 |
|------|----------|
| 模型下载慢 | 设置 `HF_ENDPOINT=https://hf-mirror.com`（国内镜像） |
| GPU 显存不足 | 使用量化模型：`tencent/HY-MT1.5-1.8B-FP8` |
| 容器无法启动 | 检查 `nvidia-smi` 和 nvidia-docker 安装 |
| 翻译不完整 | 已优化，默认分段大小 150 字符 |

## 📝 更新日志

### v1.0.0 (2026-01-03)
- 🎉 首次发布
- ✨ All-in-One Docker 镜像
- ⚡ SSE 流式翻译
- 🎨 深色/浅色主题 Web UI
- 🔧 长文本优化（分段 150 字符）
- 🤖 MCP Server 支持

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目基于 [腾讯混元 HunyuanMT](https://github.com/Tencent-Hunyuan/HY-MT)。详见 [License.txt](License.txt)。

## 🙏 致谢

- [腾讯混元](https://github.com/Tencent-Hunyuan/HY-MT) - 原始 HY-MT 模型
- [HuggingFace](https://huggingface.co/tencent/HY-MT1.5-1.8B) - 模型托管

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/hy-mt&type=Date)](https://star-history.com/#neosun100/hy-mt)

## 📱 关注公众号

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" width="300"/>
</p>
