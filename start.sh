#!/bin/bash
set -e

cd "$(dirname "$0")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 HY-MT 翻译服务启动脚本${NC}"
echo "================================"

# 检查 nvidia-docker
if ! docker info 2>/dev/null | grep -q "Runtimes.*nvidia"; then
    echo -e "${RED}❌ 未检测到 nvidia-docker，请先安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ nvidia-docker 环境正常${NC}"

# 检查 GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ 未检测到 nvidia-smi${NC}"
    exit 1
fi

# 自动选择显存占用最少的 GPU
if [ -z "$NVIDIA_VISIBLE_DEVICES" ]; then
    GPU_ID=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | \
             sort -t',' -k2 -n | head -1 | cut -d',' -f1 | tr -d ' ')
    export NVIDIA_VISIBLE_DEVICES=$GPU_ID
    echo -e "${GREEN}✓ 自动选择 GPU: $GPU_ID${NC}"
else
    echo -e "${GREEN}✓ 使用指定 GPU: $NVIDIA_VISIBLE_DEVICES${NC}"
fi

# 显示 GPU 信息
nvidia-smi --query-gpu=index,name,memory.used,memory.free --format=csv -i $NVIDIA_VISIBLE_DEVICES

# 加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 设置默认值
export PORT=${PORT:-8021}
export MODEL_NAME=${MODEL_NAME:-tencent/HY-MT1.5-1.8B}
export GPU_IDLE_TIMEOUT=${GPU_IDLE_TIMEOUT:-300}

# 创建必要目录
mkdir -p models /tmp/hy-mt

echo ""
echo -e "${YELLOW}📦 启动服务...${NC}"
docker compose up -d --build

echo ""
echo -e "${GREEN}✅ 服务启动成功！${NC}"
echo "================================"
echo -e "🌐 UI 界面:     http://0.0.0.0:${PORT}"
echo -e "📚 API 文档:    http://0.0.0.0:${PORT}/docs"
echo -e "❤️  健康检查:   http://0.0.0.0:${PORT}/health"
echo -e "🔧 MCP 服务:    见 MCP_GUIDE.md"
echo "================================"
echo -e "📊 查看日志: docker logs -f hy-mt"
echo -e "🛑 停止服务: docker compose down"
