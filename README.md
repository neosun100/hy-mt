<p align="center">
  <img src="imgs/hunyuanlogo.png" width="400"/>
</p>

<p align="center">
  <b>English</b> | <a href="README_CN.md">简体中文</a> | <a href="README_TW.md">繁體中文</a> | <a href="README_JP.md">日本語</a>
</p>

<p align="center">
  <a href="https://hub.docker.com/r/neosun/hy-mt"><img src="https://img.shields.io/docker/pulls/neosun/hy-mt?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <a href="https://github.com/neosun100/hy-mt/stargazers"><img src="https://img.shields.io/github/stars/neosun100/hy-mt?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/neosun100/hy-mt/blob/main/License.txt"><img src="https://img.shields.io/badge/license-Tencent_Hunyuan-blue?style=flat-square" alt="License"></a>
  <a href="https://huggingface.co/tencent/HY-MT1.5-1.8B"><img src="https://img.shields.io/badge/🤗-HuggingFace-yellow?style=flat-square" alt="HuggingFace"></a>
</p>

# HY-MT Translation Service

> 🚀 All-in-One Docker deployment for Tencent HunyuanMT 1.5 translation model with Web UI, REST API, and MCP Server support.

## ✨ Features

- 🌐 **38 Languages Support** - Chinese, English, Japanese, Korean, French, German, Spanish, and 31 more
- 🎨 **Modern Web UI** - Dark/Light theme toggle, drag & drop file upload, real-time progress display
- ⚡ **Streaming Translation** - Server-Sent Events (SSE) for real-time output, perfect for long texts
- 🔧 **Full Parameter Control** - Temperature, Top-P, Top-K, repetition penalty adjustable
- 📚 **Terminology Intervention** - Custom term mapping for domain-specific translations
- 🤖 **MCP Server** - Model Context Protocol support for AI assistants (Claude, etc.)
- 🐳 **One-Click Deployment** - All-in-One Docker image with all models pre-downloaded
- 🔄 **Smart GPU Management** - Auto GPU selection, idle timeout, memory release
- 🔀 **Multi-Model Support** - Switch between 4 models (1.8B/7B, base/FP8) via UI or API

## 🎯 Model Selection Guide

| Model | VRAM | Speed | Quality | Recommendation |
|-------|------|-------|---------|----------------|
| **HY-MT 7B** | 16GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🏆 **Best Choice** - Highest quality, fast speed |
| HY-MT 1.8B | 6GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Good for limited VRAM |
| HY-MT 1.8B FP8 | 4GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | For VRAM < 6GB |
| HY-MT 7B FP8 | 10GB | ⭐⭐ | ⭐⭐⭐⭐⭐ | 7B quality with less VRAM |

> 💡 **Tip**: If you have 16GB+ VRAM, use **HY-MT 7B** for best results. FP8 models save memory but are slower due to runtime decompression.

## 📸 Screenshot

<p align="center">
  <img src="docs/images/ui-screenshot-v2.0.1.png" width="800"/>
</p>

## 🚀 Quick Start

### Docker Run (Recommended)

```bash
# One command to start (uses 7B model by default)
docker run -d --gpus all \
  -p 8021:8021 \
  -v ./models:/app/models \
  --name hy-mt \
  neosun/hy-mt:latest

# Access Web UI
open http://localhost:8021
```

The Docker image (~43GB) includes all 4 models pre-downloaded. No external downloads needed!

### Docker Compose

Create `docker-compose.yml`:

```yaml
services:
  hy-mt:
    image: neosun/hy-mt:latest
    container_name: hy-mt
    ports:
      - "8021:8021"
    environment:
      - MODEL_NAME=tencent/HY-MT1.5-7B  # Recommended for 16GB+ VRAM
      - GPU_IDLE_TIMEOUT=300
      - HF_ENDPOINT=https://huggingface.co  # Use https://hf-mirror.com for China
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

## 📋 Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| GPU | NVIDIA GPU with 6GB+ VRAM | 16GB+ VRAM (for 7B model) |
| CUDA | 11.8+ | 12.4+ |
| Docker | 20.10+ | 24.0+ |
| nvidia-docker | Required | - |

### Verify GPU Support

```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## 📊 Performance Benchmark

Tested on NVIDIA L40S GPU, translating English to Chinese:

| Model | Short (61 chars) | Medium (530 chars) | Long (1.8K chars) | Extra Long (4.2K chars) |
|-------|------------------|--------------------|--------------------|-------------------------|
| **HY-MT 7B** | 0.4s | 4.4s | 17.7s | 43.0s |
| HY-MT 1.8B | 0.4s | 3.6s | 14.0s | 32.3s |
| HY-MT 1.8B FP8 | 1.1s | 10.8s | 38.1s | 92.9s |
| HY-MT 7B FP8 | 2.9s | 28.5s | 115.6s | 274.1s |

### ⚠️ Why are FP8 models slower?

This is **counter-intuitive but technically correct**:

| Comparison | Speed Change | Reason |
|------------|--------------|--------|
| 1.8B FP8 vs 1.8B | **2.7x slower** | Runtime decompression overhead |
| 7B FP8 vs 7B | **6.4x slower** | More parameters = more decompression |

**FP8 quantization is designed to save VRAM, not to speed up inference.** The model is stored in 8-bit format but needs to be decompressed to 16-bit for GPU computation at runtime. This decompression happens for every token generation.

**When to use FP8:**
- ✅ When VRAM is limited (< 16GB for 7B, < 6GB for 1.8B)
- ❌ Not for speed optimization
- ❌ Not for batch processing (speed loss accumulates)

See [Benchmark Report](docs/BENCHMARK_REPORT.md) for detailed analysis.

## 🔑 Key Optimization: Chunk Size

**Critical finding**: Smaller chunk size = Better translation quality

| Chunk Size | Quality | Notes |
|-----------|---------|-------|
| 500 chars | ❌ Poor | Mixed languages in output |
| 300 chars | ⚠️ Fair | Some untranslated residue |
| **150 chars** | ✅ Excellent | Complete, accurate translation |

The service uses `MAX_CHUNK_LENGTH=150` by default for optimal quality.

**Why?** HY-MT model tends to "slack off" on long inputs, only translating part of the content. Shorter chunks force the model to fully translate each segment.

See [Optimization Guide](docs/OPTIMIZATION_GUIDE.md) for details.

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8021 | Service port |
| `MODEL_NAME` | tencent/HY-MT1.5-7B | HuggingFace model name |
| `MODEL_PATH` | ./models | Local model cache path |
| `GPU_IDLE_TIMEOUT` | 300 | Auto-release GPU after idle (seconds) |
| `NVIDIA_VISIBLE_DEVICES` | auto | GPU ID (empty = auto select) |
| `HF_ENDPOINT` | https://huggingface.co | HuggingFace mirror URL |

### Using .env File

```bash
# Copy example config
cp .env.example .env

# Edit as needed
vim .env
```

## 📖 API Usage

### Basic Translation

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "zh"
  }'
```

Response:
```json
{
  "status": "success",
  "result": "你好，你好吗？",
  "elapsed_ms": 358,
  "model": "tencent/HY-MT1.5-7B",
  "chunks": 1
}
```

### Streaming Translation (SSE)

```bash
curl -N "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long article to translate...",
    "target_lang": "en",
    "stream": true
  }'
```

### With Terminology Intervention

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple released iPhone 16",
    "target_lang": "zh",
    "terms": {"Apple": "苹果公司", "iPhone": "苹果手机"}
  }'
```

Output: `苹果公司发布了苹果手机16`

### File Upload Translation

```bash
curl "http://localhost:8021/api/translate/file" \
  -F "file=@document.txt" \
  -F "target_lang=zh" \
  -F "stream=true"
```

### Switch Model

```bash
curl -X POST "http://localhost:8021/api/models/switch" \
  -H "Content-Type: application/json" \
  -d '{"model": "tencent/HY-MT1.5-1.8B"}'
```

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/translate` | POST | Translate text (supports streaming) |
| `/api/translate/file` | POST | Upload and translate file |
| `/api/translate/batch` | POST | Batch translation |
| `/api/translate/stream` | POST | Streaming translation (SSE) |
| `/api/languages` | GET | List supported languages |
| `/api/models` | GET | List available models |
| `/api/models/switch` | POST | Switch translation model |
| `/api/gpu/status` | GET | GPU status and memory info |
| `/api/gpu/offload` | POST | Release GPU memory |
| `/api/config` | GET | Service configuration |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger API documentation |

## 🌍 Supported Languages

| Language | Code | Language | Code | Language | Code |
|----------|------|----------|------|----------|------|
| Chinese | zh | English | en | Japanese | ja |
| Korean | ko | French | fr | German | de |
| Spanish | es | Portuguese | pt | Russian | ru |
| Arabic | ar | Thai | th | Vietnamese | vi |
| Italian | it | Dutch | nl | Polish | pl |
| Turkish | tr | Indonesian | id | Malay | ms |
| Hindi | hi | Traditional Chinese | zh-Hant | Cantonese | yue |

And 17 more languages. See `/api/languages` for full list.

## 🛠️ Tech Stack

- **Model**: [Tencent HY-MT1.5](https://huggingface.co/tencent/HY-MT1.5-1.8B) (1.8B & 7B)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Vanilla JS with Dark/Light Mode
- **Container**: NVIDIA CUDA 12.4 base image
- **Streaming**: Server-Sent Events (SSE)
- **MCP**: Model Context Protocol for AI integration

## 📁 Project Structure

```
hy-mt/
├── app_fastapi.py      # Main FastAPI application
├── mcp_server.py       # MCP Server for AI assistants
├── benchmark.py        # Performance benchmark script
├── templates/
│   └── index.html      # Web UI (Dark/Light theme)
├── docs/
│   ├── BENCHMARK_REPORT.md    # Performance test report
│   ├── OPTIMIZATION_GUIDE.md  # Long text optimization guide
│   └── QUICK_REFERENCE.md     # API quick reference
├── Dockerfile          # All-in-One Docker build
├── docker-compose.yml  # Docker Compose config
├── start.sh           # Quick start script
├── test_api.sh        # API test script
└── .env.example       # Environment config template
```

## 🔧 Advanced Usage

### Manual Start (Development)

```bash
# Clone repository
git clone https://github.com/neosun100/hy-mt.git
cd hy-mt

# Install dependencies
pip install torch transformers accelerate fastapi uvicorn

# Run
python -m uvicorn app_fastapi:app --host 0.0.0.0 --port 8021
```

### MCP Server Integration

For AI assistants like Claude Desktop, add to MCP config:

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

Available MCP tools:
- `translate` - Translate text
- `list_languages` - Get supported languages
- `list_models` - Get available models
- `switch_model` - Switch translation model

See [MCP_GUIDE.md](MCP_GUIDE.md) for details.

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Model download slow | Set `HF_ENDPOINT=https://hf-mirror.com` (China mirror) |
| GPU out of memory | Use quantized model: `tencent/HY-MT1.5-1.8B-FP8` |
| Container won't start | Check `nvidia-smi` and nvidia-docker installation |
| Translation incomplete | Already optimized with chunk size 150 |
| Container shows unhealthy | Wait 1-2 minutes for model loading |

## 📝 Changelog

### v2.0.1 (2026-01-03)
- 🏆 Default model changed to **HY-MT 7B** (best quality & speed)
- 🩺 Added Docker HEALTHCHECK for container health monitoring
- 📦 Container status now shows `(healthy)` when ready

### v2.0.0 (2026-01-03) - True All-in-One
- 🎯 **All 4 models pre-downloaded in Docker image** - No external downloads needed!
- 📦 Image size: ~43GB (includes all models)
- 🏆 Recommended: HY-MT 7B for best quality and speed
- 📊 Added performance benchmark report
- 🔧 Added `benchmark.py` for reproducible testing

### v1.2.0 (2026-01-03)
- 🔀 Multi-model support (4 models: 1.8B, 1.8B-FP8, 7B, 7B-FP8)
- 🔄 Model switching via UI and API
- 📝 MCP Server: added `list_models` and `switch_model` tools
- 🐛 Fixed model name display in translation response

### v1.0.0 (2026-01-03)
- 🎉 Initial release
- ✨ All-in-One Docker image
- ⚡ Streaming translation with SSE
- 🎨 Dark/Light theme Web UI
- 🔧 Long text optimization (chunk size 150)
- 🤖 MCP Server support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is based on [Tencent HunyuanMT](https://github.com/Tencent-Hunyuan/HY-MT). See [License.txt](License.txt) for details.

## 🙏 Acknowledgments

- [Tencent Hunyuan](https://github.com/Tencent-Hunyuan/HY-MT) - Original HY-MT model
- [HuggingFace](https://huggingface.co/tencent/HY-MT1.5-1.8B) - Model hosting

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/hy-mt&type=Date)](https://star-history.com/#neosun100/hy-mt)

## 📱 Follow Us

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" width="300"/>
</p>
