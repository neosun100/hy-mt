#!/bin/bash
# HY-MT 翻译服务测试脚本

HOST="${1:-localhost:8021}"

echo "🔍 测试 HY-MT 翻译服务 @ $HOST"
echo "================================"

# 健康检查
echo -e "\n1️⃣ 健康检查..."
curl -s "http://$HOST/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   状态: {d[\"status\"]}, GPU已加载: {d[\"gpu\"][\"loaded\"]}')"

# 英译中
echo -e "\n2️⃣ 英译中..."
result=$(curl -s -X POST "http://$HOST/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "source_lang": "en", "target_lang": "zh"}')
echo "   输入: Hello, how are you?"
echo "   输出: $(echo $result | python3 -c "import sys,json; print(json.load(sys.stdin).get('result','ERROR'))")"

# 中译英
echo -e "\n3️⃣ 中译英..."
result=$(curl -s -X POST "http://$HOST/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能正在改变世界", "source_lang": "zh", "target_lang": "en"}')
echo "   输入: 人工智能正在改变世界"
echo "   输出: $(echo $result | python3 -c "import sys,json; print(json.load(sys.stdin).get('result','ERROR'))")"

# 英译日
echo -e "\n4️⃣ 英译日..."
result=$(curl -s -X POST "http://$HOST/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "The weather is beautiful today", "source_lang": "en", "target_lang": "ja"}')
echo "   输入: The weather is beautiful today"
echo "   输出: $(echo $result | python3 -c "import sys,json; print(json.load(sys.stdin).get('result','ERROR'))")"

# 术语干预
echo -e "\n5️⃣ 术语干预..."
result=$(curl -s -X POST "http://$HOST/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple released a new iPhone", "source_lang": "en", "target_lang": "zh", "terms": {"Apple": "苹果公司", "iPhone": "苹果手机"}}')
echo "   输入: Apple released a new iPhone"
echo "   术语: Apple→苹果公司, iPhone→苹果手机"
echo "   输出: $(echo $result | python3 -c "import sys,json; print(json.load(sys.stdin).get('result','ERROR'))")"

# GPU 状态
echo -e "\n6️⃣ GPU 状态..."
curl -s "http://$HOST/api/gpu/status" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'   显存: {d[\"gpu_free_mb\"]}MB / {d[\"gpu_total_mb\"]}MB')
print(f'   空闲: {d[\"idle_seconds\"]}秒')
"

echo -e "\n✅ 测试完成!"
