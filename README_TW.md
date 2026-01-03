<p align="center">
  <img src="imgs/hunyuanlogo.png" width="400"/>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a> | <b>繁體中文</b> | <a href="README_JP.md">日本語</a>
</p>

<p align="center">
  <a href="https://hub.docker.com/r/neosun/hy-mt"><img src="https://img.shields.io/docker/pulls/neosun/hy-mt?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <a href="https://github.com/neosun100/hy-mt/stargazers"><img src="https://img.shields.io/github/stars/neosun100/hy-mt?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/neosun100/hy-mt/blob/main/License.txt"><img src="https://img.shields.io/badge/license-Tencent_Hunyuan-blue?style=flat-square" alt="License"></a>
  <a href="https://huggingface.co/tencent/HY-MT1.5-1.8B"><img src="https://img.shields.io/badge/🤗-HuggingFace-yellow?style=flat-square" alt="HuggingFace"></a>
</p>

# HY-MT 翻譯服務

> 🚀 騰訊混元 HY-MT1.5-1.8B 翻譯模型的 All-in-One Docker 部署方案，整合 Web UI、REST API 和 MCP Server。

## ✨ 功能特性

- 🌐 **38 種語言支援** - 中文、英語、日語、韓語、法語、德語、西班牙語等
- 🎨 **現代化 Web UI** - 深色/淺色主題切換、拖曳上傳、即時進度顯示
- ⚡ **串流翻譯** - Server-Sent Events (SSE) 即時輸出，長文本翻譯體驗更佳
- 🔧 **完整參數控制** - Temperature、Top-P、Top-K、重複懲罰等參數可調
- 📚 **術語干預** - 自訂術語對應，適用於專業領域翻譯
- 🤖 **MCP Server** - 支援 Model Context Protocol，可整合 Claude 等 AI 助手
- 🐳 **一鍵部署** - All-in-One Docker 映像檔，模型自動下載
- 🔄 **智慧 GPU 管理** - 自動選擇 GPU、閒置逾時釋放顯存

## 📸 介面截圖

<p align="center">
  <img src="docs/images/ui-screenshot.png" width="800"/>
</p>

## 🚀 快速開始

### 方式一：Docker Run（推薦）

```bash
# 一條指令啟動
docker run -d --gpus all \
  -p 8021:8021 \
  -v ./models:/app/models \
  --name hy-mt \
  neosun/hy-mt:latest

# 存取 Web UI
open http://localhost:8021
```

首次執行會自動下載模型（約 3.5GB）。

### 方式二：Docker Compose

建立 `docker-compose.yml`：

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
      - HF_ENDPOINT=https://huggingface.co
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

### 方式三：本機開發執行

```bash
# 複製儲存庫
git clone https://github.com/neosun100/hy-mt.git
cd hy-mt

# 安裝相依套件
pip install torch transformers accelerate fastapi uvicorn

# 啟動服務
python -m uvicorn app_fastapi:app --host 0.0.0.0 --port 8021
```

## 📋 環境需求

| 需求 | 最低配置 | 建議配置 |
|------|----------|----------|
| GPU | NVIDIA GPU 6GB+ 顯存 | 8GB+ 顯存 |
| CUDA | 11.8+ | 12.4+ |
| Docker | 20.10+ | 24.0+ |
| nvidia-docker | 必需 | - |

### 驗證 GPU 支援

```bash
# 檢查 NVIDIA 驅動程式
nvidia-smi

# 檢查 Docker GPU 支援
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## ⚙️ 配置說明

### 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `PORT` | 8021 | 服務連接埠 |
| `MODEL_NAME` | tencent/HY-MT1.5-1.8B | HuggingFace 模型名稱 |
| `MODEL_PATH` | ./models | 本機模型快取路徑 |
| `GPU_IDLE_TIMEOUT` | 300 | GPU 閒置逾時自動釋放（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 自動 | GPU ID（留空自動選擇） |
| `HF_ENDPOINT` | https://huggingface.co | HuggingFace 鏡像位址 |

### 使用 .env 檔案

```bash
# 複製範例配置
cp .env.example .env

# 編輯配置
vim .env
```

## 📖 API 使用

### 基礎翻譯

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "zh-Hant"
  }'
```

回應：
```json
{
  "status": "success",
  "result": "你好，你好嗎？",
  "elapsed_ms": 1234,
  "chunks": 1
}
```

### 串流翻譯（SSE）

```bash
curl -N "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "需要翻譯的長文章...",
    "target_lang": "en",
    "stream": true
  }'
```

### 術語干預

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple released iPhone 16",
    "target_lang": "zh-Hant",
    "terms": {"Apple": "蘋果公司", "iPhone": "蘋果手機"}
  }'
```

### 檔案上傳翻譯

```bash
curl "http://localhost:8021/api/translate/file" \
  -F "file=@document.txt" \
  -F "target_lang=zh-Hant" \
  -F "stream=true"
```

## 📚 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | Web UI 介面 |
| `/api/translate` | POST | 文字翻譯（支援串流） |
| `/api/translate/file` | POST | 檔案上傳翻譯 |
| `/api/translate/batch` | POST | 批次翻譯 |
| `/api/languages` | GET | 支援的語言清單 |
| `/api/gpu/status` | GET | GPU 狀態和顯存資訊 |
| `/api/gpu/offload` | POST | 釋放 GPU 顯存 |
| `/health` | GET | 健康檢查 |
| `/docs` | GET | Swagger API 文件 |

## 🔑 關鍵優化：分段大小

**重要發現**：分段越小，翻譯品質越好

| 分段大小 | 品質 | 說明 |
|----------|------|------|
| 500 字元 | ❌ 差 | 中英混雜 |
| 300 字元 | ⚠️ 一般 | 部分未翻譯 |
| **150 字元** | ✅ 優秀 | 翻譯完整準確 |

服務預設使用 `MAX_CHUNK_LENGTH=150` 以獲得最佳品質。

詳見 [優化指南](docs/OPTIMIZATION_GUIDE.md)。

## 🌍 支援的語言

| 語言 | 代碼 | 語言 | 代碼 | 語言 | 代碼 |
|------|------|------|------|------|------|
| 中文 | zh | 英語 | en | 日語 | ja |
| 韓語 | ko | 法語 | fr | 德語 | de |
| 西班牙語 | es | 葡萄牙語 | pt | 俄語 | ru |
| 阿拉伯語 | ar | 泰語 | th | 越南語 | vi |
| 義大利語 | it | 荷蘭語 | nl | 波蘭語 | pl |
| 土耳其語 | tr | 印尼語 | id | 馬來語 | ms |
| 印地語 | hi | 繁體中文 | zh-Hant | 粵語 | yue |

以及更多 17 種語言，完整清單見 `/api/languages`。

## 🛠️ 技術棧

- **模型**: [Tencent HY-MT1.5-1.8B](https://huggingface.co/tencent/HY-MT1.5-1.8B)
- **後端**: FastAPI + Uvicorn
- **前端**: 原生 JS + 深色/淺色主題
- **容器**: NVIDIA CUDA 12.4 基礎映像檔
- **串流**: Server-Sent Events (SSE)
- **MCP**: Model Context Protocol AI 整合

## 📁 專案結構

```
hy-mt/
├── app_fastapi.py      # FastAPI 主應用程式
├── mcp_server.py       # MCP Server（AI 助手整合）
├── templates/
│   └── index.html      # Web UI（深色/淺色主題）
├── docs/
│   ├── OPTIMIZATION_GUIDE.md  # 長文本優化指南
│   └── QUICK_REFERENCE.md     # API 快速參考
├── Dockerfile          # All-in-One Docker 建置
├── docker-compose.yml  # Docker Compose 配置
├── start.sh           # 快速啟動腳本
├── test_api.sh        # API 測試腳本
└── .env.example       # 環境變數範本
```

## 🔧 進階用法

### MCP Server 整合

在 Claude Desktop 等 AI 助手中使用，新增 MCP 配置：

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

詳見 [MCP_GUIDE.md](MCP_GUIDE.md)。

## 🐛 故障排除

| 問題 | 解決方案 |
|------|----------|
| 模型下載慢 | 設定 `HF_ENDPOINT=https://hf-mirror.com`（中國鏡像） |
| GPU 顯存不足 | 使用量化模型：`tencent/HY-MT1.5-1.8B-FP8` |
| 容器無法啟動 | 檢查 `nvidia-smi` 和 nvidia-docker 安裝 |
| 翻譯不完整 | 已優化，預設分段大小 150 字元 |

## 📝 更新日誌

### v1.0.0 (2026-01-03)
- 🎉 首次發布
- ✨ All-in-One Docker 映像檔
- ⚡ SSE 串流翻譯
- 🎨 深色/淺色主題 Web UI
- 🔧 長文本優化（分段 150 字元）
- 🤖 MCP Server 支援

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本儲存庫
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 授權條款

本專案基於 [騰訊混元 HunyuanMT](https://github.com/Tencent-Hunyuan/HY-MT)。詳見 [License.txt](License.txt)。

## 🙏 致謝

- [騰訊混元](https://github.com/Tencent-Hunyuan/HY-MT) - 原始 HY-MT 模型
- [HuggingFace](https://huggingface.co/tencent/HY-MT1.5-1.8B) - 模型託管

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/hy-mt&type=Date)](https://star-history.com/#neosun100/hy-mt)

## 📱 關注公眾號

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" width="300"/>
</p>
