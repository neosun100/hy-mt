# HY-MT 快速参考

## 核心参数

```
MAX_CHUNK_LENGTH = 150      # 分段大小（关键！越小翻译越完整）
repetition_penalty = 1.1    # 重复惩罚
temperature = 0.7           # 生成温度
```

## 重要发现：分段大小决定翻译质量

| 分段大小 | 翻译质量 |
|---------|---------|
| 500 字符 | ❌ 中英混杂 |
| 300 字符 | ⚠️ 部分残留 |
| **150 字符** | ✅ 完整翻译 |

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/translate` | POST | 单文本翻译（支持流式） |
| `/api/translate/stream` | POST | 流式翻译（专用端点） |
| `/api/translate/file` | POST | 文件上传翻译 |
| `/api/translate/batch` | POST | 批量翻译 |
| `/api/languages` | GET | 支持的语言 |
| `/health` | GET | 健康检查 |

## 快速调用

```bash
# 基础翻译
curl -X POST "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "target_lang": "zh"}'

# 流式翻译（SSE）
curl -N "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "长文本...", "target_lang": "zh", "stream": true}'

# 文件上传翻译
curl "https://hy-mt.aws.xin/api/translate/file" \
  -F "file=@document.txt" \
  -F "target_lang=zh" \
  -F "stream=true"

# 术语干预
curl -X POST "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple iPhone", "target_lang": "zh", "terms": {"Apple": "苹果公司"}}'
```

## 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| text | string | 必填 | 待翻译文本 |
| target_lang | string | 必填 | 目标语言代码 |
| source_lang | string | 自动 | 源语言代码 |
| terms | object | null | 术语干预 |
| context | string | null | 上下文参考 |
| auto_split | bool | true | 自动分段 |
| stream | bool | false | 流式返回（SSE） |
| temperature | float | 0.7 | 生成温度 |
| repetition_penalty | float | 1.1 | 重复惩罚 |

## 流式返回事件

```javascript
// SSE 事件格式
data: {"event": "start", "total_chunks": 3, "input_length": 1000}
data: {"event": "progress", "chunk": 1, "total": 3, "status": "translating"}
data: {"event": "chunk", "chunk": 1, "total": 3, "result": "翻译结果", "elapsed_ms": 500}
data: {"event": "done", "total_chunks": 3, "elapsed_ms": 1500, "output_length": 300}
```

## 常用语言代码

```
zh=中文  en=英语  ja=日语  ko=韩语
fr=法语  de=德语  es=西班牙语  ru=俄语
zh-Hant=繁体中文  yue=粤语
```

## 故障排查

| 问题 | 解决 |
|------|------|
| 输出重复 | 提高 repetition_penalty 到 1.15 |
| 翻译不完整 | 降低 MAX_CHUNK_LENGTH |
| 响应慢 | 检查 GPU 状态 `/health` |
