# HY-MT 翻译服务

基于腾讯混元 HY-MT1.5-1.8B 模型的翻译服务，支持 33 种语言互译。

## 快速开始

```bash
# 1. 复制配置文件
cp .env.example .env

# 2. 一键启动
./start.sh
```

## 访问方式

| 方式 | 地址 | 说明 |
|------|------|------|
| UI 界面 | http://localhost:8021 | Web 翻译界面 |
| API 文档 | http://localhost:8021/apidocs | Swagger 文档 |
| 健康检查 | http://localhost:8021/health | 服务状态 |
| MCP | 见 MCP_GUIDE.md | 程序化接口 |

## API 示例

```bash
# 翻译文本
curl -X POST http://localhost:8021/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "target_lang": "zh"}'

# 获取 GPU 状态
curl http://localhost:8021/api/gpu/status

# 释放显存
curl -X POST http://localhost:8021/api/gpu/offload
```

## 配置说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| PORT | 8021 | 服务端口 |
| MODEL_NAME | tencent/HY-MT1.5-1.8B | 模型名称 |
| GPU_IDLE_TIMEOUT | 300 | GPU 空闲超时(秒) |
| HF_ENDPOINT | https://hf-mirror.com | HF 镜像 |

## 支持的语言

中文、英语、日语、韩语、法语、德语、西班牙语、葡萄牙语、俄语、阿拉伯语、泰语、越南语、意大利语、荷兰语、波兰语、土耳其语、印尼语、马来语、印地语、繁体中文、捷克语、乌克兰语、波斯语、希伯来语、孟加拉语、泰米尔语、泰卢固语、马拉地语、古吉拉特语、乌尔都语、高棉语、缅甸语、菲律宾语、藏语、哈萨克语、蒙古语、维吾尔语、粤语

## 停止服务

```bash
docker compose down
```


## 测试脚本

运行测试脚本验证服务：

```bash
./test_api.sh
# 或指定地址
./test_api.sh localhost:8021
```

测试输出示例：
```
🔍 测试 HY-MT 翻译服务 @ localhost:8021
================================

1️⃣ 健康检查...
   状态: ok, GPU已加载: True

2️⃣ 英译中...
   输入: Hello, how are you?
   输出: 您好，您最近怎么样？

3️⃣ 中译英...
   输入: 人工智能正在改变世界
   输出: Artificial intelligence is transforming the world.

4️⃣ 英译日...
   输入: The weather is beautiful today
   输出: 今日の天気はとても良いです。

5️⃣ 术语干预...
   输入: Apple released a new iPhone
   术语: Apple→苹果公司, iPhone→苹果手机
   输出: 苹果公司推出了新款苹果手机。

✅ 测试完成!
```

## 故障排除

### 模型下载慢
使用国内镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### GPU 内存不足
1. 使用量化模型：`tencent/HY-MT1.5-1.8B-FP8`
2. 释放其他 GPU 进程

### 容器无法启动
检查 NVIDIA 驱动：
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```
