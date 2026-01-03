# HY-MT 翻译服务优化指南

> 基于 HY-MT1.5-1.8B 模型的长文本翻译优化实践总结

## 目录

1. [问题背景](#问题背景)
2. [核心优化参数](#核心优化参数)
3. [分段策略](#分段策略)
4. [滚动上下文机制](#滚动上下文机制)
5. [重复惩罚调优](#重复惩罚调优)
6. [最佳实践](#最佳实践)
7. [测试验证](#测试验证)

---

## 问题背景

### 长文本翻译面临的挑战

1. **模型上下文窗口限制**：HY-MT1.5-1.8B 上下文窗口约 4096 token
2. **输出重复**：长输入时模型容易产生重复内容
3. **上下文断裂**：分段翻译后，代词指代、术语一致性丢失
4. **分段不均匀**：简单按字符截断会破坏句子完整性

### 优化目标

- 翻译完整，无遗漏
- 无重复输出
- 代词指代准确（He/She/They 正确关联人物）
- 术语一致性
- 响应时间合理

---

## 核心优化参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `MAX_CHUNK_LENGTH` | **150 字符** | 每段最大长度（关键参数） |
| `repetition_penalty` | 1.1 | 重复惩罚系数 |
| `temperature` | 0.7 | 生成温度 |
| `top_p` | 0.6 | 核采样概率 |
| `top_k` | 20 | Top-K 采样 |

### 参数选择依据

#### MAX_CHUNK_LENGTH = 150（重要发现）

**这是最关键的优化参数！** 经过大量测试发现，分段越小，翻译质量越好：

| 分段大小 | 段数 | 输出长度 | 翻译质量 |
|---------|------|---------|---------|
| 500 字符 | 4 | ~900 | ❌ 中英混杂严重 |
| 300 字符 | 7 | ~1600 | ⚠️ 部分中文残留 |
| **150 字符** | 16 | **4908** | ✅ 几乎全英文 |

**原因分析**：
- HY-MT 模型对长输入容易产生"偷懒"行为，只翻译部分内容
- 短段落让模型专注于完整翻译每个句子
- 虽然段数增加导致耗时增加，但配合流式输出，用户体验反而更好

**结论**：150 字符是最佳分段大小，确保翻译完整且质量高。

#### 上下文长度比例 (250:350)

```
总上下文预算：~600 字符
- 原文 250 字符：提供语境参考
- 译文 350 字符：更重要，帮助保持翻译风格和术语一致性
```

**原因**：译文比原文更重要，因为模型需要参考前文的翻译风格来保持一致性。

---

## 分段策略

### 算法设计

```python
def split_text(text: str, max_length: int = 500) -> List[str]:
    """智能分段：优先按句子分割，确保每段大小均匀"""
    
    # 1. 短文本直接返回
    if len(text) <= max_length:
        return [text]
    
    # 2. 按句子分割（保留标点）
    sentence_pattern = r'([。！？.!?]+[\s]*)'
    parts = re.split(sentence_pattern, text)
    
    # 3. 重组句子（句子+标点）
    sentences = []
    for i in range(0, len(parts), 2):
        sent = parts[i]
        if i + 1 < len(parts):
            sent += parts[i + 1]
        if sent.strip():
            sentences.append(sent)
    
    # 4. 贪心分段：尽量填满每段
    chunks = []
    current_chunk = ""
    
    for sent in sentences:
        if len(current_chunk) + len(sent) <= max_length:
            current_chunk += sent
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 单句超长则强制分割
            if len(sent) > max_length:
                for i in range(0, len(sent), max_length):
                    chunks.append(sent[i:i+max_length].strip())
                current_chunk = ""
            else:
                current_chunk = sent
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks
```

### 分段原则

1. **句子完整性**：优先在句子边界分割，不破坏句子结构
2. **均匀分布**：避免出现一段很长、一段很短的情况
3. **容错处理**：单句超长时强制按字符分割

### 支持的句子分隔符

- 中文：`。` `！` `？`
- 英文：`.` `!` `?`

---

## 滚动上下文机制

### 设计思路

```
第1段翻译 → 保存原文+译文
    ↓
第2段翻译时，将第1段作为上下文参考
    ↓
第3段翻译时，将第2段作为上下文参考（第1段丢弃）
    ...
```

### 实现代码

```python
def translate(text, target_lang, ...):
    chunks = split_text(text)
    results = []
    
    # 滚动上下文
    prev_src = ""  # 前文原文
    prev_tgt = ""  # 前文译文
    
    for i, chunk in enumerate(chunks):
        # 构建上下文
        if prev_src and prev_tgt:
            context = f"前文：{prev_src}\n译文：{prev_tgt}"
        else:
            context = None
        
        # 翻译当前段
        result = translate_single(chunk, target_lang, context=context, ...)
        results.append(result)
        
        # 更新滚动上下文（为下一段准备）
        if i < len(chunks) - 1:
            prev_src = smart_truncate(chunk, 250)
            prev_tgt = smart_truncate(result, 350)
    
    return "\n".join(results)
```

### 智能截取函数

```python
def smart_truncate(text: str, max_len: int) -> str:
    """在句子边界截断，从末尾保留"""
    if len(text) <= max_len:
        return text
    
    # 从末尾截取
    truncated = text[-max_len:]
    
    # 找第一个句子开头
    for sep in ['. ', '。', '！', '？', '! ', '? ']:
        pos = truncated.find(sep)
        if 0 < pos < len(truncated) - 30:
            return truncated[pos + len(sep):]
    
    return truncated
```

### 为什么只保留前一段？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 保留所有前文 | 上下文完整 | Token 溢出，处理变慢 |
| 保留前2段 | 上下文较丰富 | 可能超出预算 |
| **保留前1段** | 简单高效，足够保持连贯性 | 极长文本可能丢失早期上下文 |

**实践结论**：保留前1段（约600字符）在大多数场景下足够，且不会导致 token 溢出。

---

## 重复惩罚调优

### 问题现象

当输入文本较长时，模型可能产生重复输出：

```
输入：Many companies have expressed interest...
输出：许多公司都表示有兴趣...许多公司都表示有兴趣...许多公司都表示有兴趣...
```

### 解决方案

将 `repetition_penalty` 从 1.05 提升到 1.1：

```python
outputs = model.generate(
    input_ids,
    max_new_tokens=2048,
    repetition_penalty=1.1,  # 关键参数
    ...
)
```

### 参数范围建议

| 值 | 效果 |
|----|------|
| 1.0 | 无惩罚，容易重复 |
| 1.05 | 轻微惩罚，长文本仍可能重复 |
| **1.1** | 推荐值，有效防止重复 |
| 1.2+ | 惩罚过重，可能影响翻译质量 |

---

## 最佳实践

### 1. 环境变量配置

```bash
# 可通过环境变量调整参数
export MAX_CHUNK_LENGTH=500
export GPU_IDLE_TIMEOUT=300
```

### 2. API 调用示例

#### 基础翻译

```bash
curl -X POST "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "source_lang": "en",
    "target_lang": "zh"
  }'
```

#### 长文本翻译（自动分段）

```bash
curl -X POST "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "很长的文章内容...",
    "source_lang": "en",
    "target_lang": "zh",
    "auto_split": true
  }'
```

#### 带术语干预

```bash
curl -X POST "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple released iPhone 16",
    "source_lang": "en",
    "target_lang": "zh",
    "terms": {"Apple": "苹果公司", "iPhone": "苹果手机"}
  }'
```

#### 自定义参数

```bash
curl -X POST "https://hy-mt.aws.xin/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "...",
    "target_lang": "zh",
    "temperature": 0.5,
    "top_p": 0.8,
    "repetition_penalty": 1.15,
    "max_new_tokens": 1024
  }'
```

### 3. 响应格式

```json
{
  "status": "success",
  "result": "翻译结果",
  "elapsed_ms": 1234,
  "chunks": 3,
  "input_length": 1092,
  "output_length": 378,
  "error": null
}
```

---

## 测试验证

### 测试用例 1：长文本翻译

**输入**（1092 字符）：
```
Dr. Sarah Chen is a renowned AI researcher at Stanford University. 
She has published over 100 papers in top conferences...
```

**预期结果**：
- 分段数：2-3 段
- 无重复输出
- 代词指代正确（She → 她/莎拉）
- 人名一致（Sarah Chen → 莎拉·陈）

### 测试用例 2：多人物长文本

**输入**（含多个人物）：
```
Dr. Sarah Chen... Meanwhile, Professor James Liu is working on quantum computing...
```

**预期结果**：
- Sarah Chen → 莎拉·陈（一致）
- James Liu → 詹姆斯·刘（一致）
- 代词不混淆

### 测试用例 3：术语干预

**输入**：
```json
{
  "text": "Apple released iPhone 16",
  "terms": {"Apple": "苹果公司", "iPhone": "苹果手机"}
}
```

**预期输出**：`苹果公司发布了苹果手机16`

### 自动化测试脚本

```bash
#!/bin/bash
# test_translation.sh

API="https://hy-mt.aws.xin/api/translate"

echo "=== 测试1: 基础翻译 ==="
curl -s "$API" -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "target_lang": "zh"}' | jq .

echo "=== 测试2: 长文本 ==="
curl -s "$API" -H "Content-Type: application/json" \
  -d '{"text": "长文本内容...", "target_lang": "zh"}' | jq '{chunks, elapsed_ms}'

echo "=== 测试3: 术语干预 ==="
curl -s "$API" -H "Content-Type: application/json" \
  -d '{"text": "Apple iPhone", "target_lang": "zh", "terms": {"Apple": "苹果公司"}}' | jq .result
```

---

## 附录

### A. 支持的语言列表

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| 中文 | zh | 英语 | en |
| 日语 | ja | 韩语 | ko |
| 法语 | fr | 德语 | de |
| 西班牙语 | es | 葡萄牙语 | pt |
| 俄语 | ru | 阿拉伯语 | ar |
| 繁体中文 | zh-Hant | 粤语 | yue |

完整列表见 `/api/languages` 接口。

### B. 性能基准（MAX_CHUNK_LENGTH=150）

| 场景 | 输入长度 | 分段数 | 耗时 | 输出长度 |
|------|----------|--------|------|---------|
| 短文本 | <150 字符 | 1 | ~1-2s | - |
| 中等文本 | 500 字符 | 3-4 | ~8-12s | - |
| 长文本 | 1000 字符 | 7-8 | ~20-25s | - |
| 超长文本 | 1800 字符 | 16 | ~35-40s | ~4900 字符 |

**注意**：虽然耗时增加，但配合流式输出，用户可以实时看到翻译进度，体验更好。

### C. 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 输出重复 | repetition_penalty 过低 | 提高到 1.1-1.15 |
| 翻译不完整 | 分段过大 | 降低 MAX_CHUNK_LENGTH |
| 上下文断裂 | 上下文长度不足 | 增加 MAX_PREV_TGT |
| 响应超时 | 文本过长 | 启用 auto_split |

---

## 更新日志

- **2026-01-03**：初版，完成长文本优化
  - 分段策略优化（500字符/段）
  - 滚动上下文机制（250+350字符）
  - 重复惩罚调优（1.05→1.1）

---

*文档维护：HY-MT 项目组*
