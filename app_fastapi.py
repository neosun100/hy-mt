"""
HY-MT 翻译服务 - FastAPI 版本 (流式增强版)
"""
import os
import time
import threading
import torch
import gc
import re
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, AsyncGenerator

# ==================== 配置 ====================
MODEL_NAME = os.getenv("MODEL_NAME", "tencent/HY-MT1.5-1.8B")
GPU_IDLE_TIMEOUT = int(os.getenv("GPU_IDLE_TIMEOUT", "300"))
MAX_CHUNK_LENGTH = int(os.getenv("MAX_CHUNK_LENGTH", "150"))

LANGUAGES = {
    "zh": "中文", "en": "英语", "ja": "日语", "ko": "韩语", "fr": "法语",
    "de": "德语", "es": "西班牙语", "pt": "葡萄牙语", "ru": "俄语", "ar": "阿拉伯语",
    "th": "泰语", "vi": "越南语", "it": "意大利语", "nl": "荷兰语", "pl": "波兰语",
    "tr": "土耳其语", "id": "印尼语", "ms": "马来语", "hi": "印地语",
    "zh-Hant": "繁体中文", "cs": "捷克语", "uk": "乌克兰语", "fa": "波斯语",
    "he": "希伯来语", "bn": "孟加拉语", "ta": "泰米尔语", "te": "泰卢固语",
    "mr": "马拉地语", "gu": "古吉拉特语", "ur": "乌尔都语", "km": "高棉语",
    "my": "缅甸语", "tl": "菲律宾语", "bo": "藏语", "kk": "哈萨克语",
    "mn": "蒙古语", "ug": "维吾尔语", "yue": "粤语"
}

# ==================== GPU 管理 ====================
class GPUManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.lock = threading.Lock()
        self.last_used = 0
        self.unload_timer = None
    
    def load(self):
        with self.lock:
            if self.model is None:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                self.model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME, device_map="auto", torch_dtype=torch.bfloat16
                )
            self.last_used = time.time()
            self._schedule_unload()
            return self.model, self.tokenizer
    
    def _schedule_unload(self):
        if self.unload_timer:
            self.unload_timer.cancel()
        self.unload_timer = threading.Timer(GPU_IDLE_TIMEOUT, self._unload)
        self.unload_timer.daemon = True
        self.unload_timer.start()
    
    def _unload(self):
        with self.lock:
            if self.model and time.time() - self.last_used >= GPU_IDLE_TIMEOUT:
                del self.model, self.tokenizer
                self.model = self.tokenizer = None
                gc.collect()
                torch.cuda.empty_cache()
    
    def status(self):
        return {
            "loaded": self.model is not None,
            "idle_seconds": int(time.time() - self.last_used) if self.last_used else 0,
            "gpu_free_mb": int(torch.cuda.mem_get_info()[0] / 1024 / 1024) if torch.cuda.is_available() else 0,
            "gpu_total_mb": int(torch.cuda.mem_get_info()[1] / 1024 / 1024) if torch.cuda.is_available() else 0,
            "model_name": MODEL_NAME
        }

gpu = GPUManager()

# ==================== 生命周期 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if gpu.unload_timer:
        gpu.unload_timer.cancel()

app = FastAPI(title="HY-MT Translation API", lifespan=lifespan)

# ==================== 分段函数 ====================
def split_text(text: str, max_length: int = MAX_CHUNK_LENGTH) -> List[str]:
    """智能分段：优先按句子分割"""
    if len(text) <= max_length:
        return [text]
    
    sentence_pattern = r'([。！？.!?]+[\s]*)'
    parts = re.split(sentence_pattern, text)
    
    sentences = []
    for i in range(0, len(parts), 2):
        sent = parts[i]
        if i + 1 < len(parts):
            sent += parts[i + 1]
        if sent.strip():
            sentences.append(sent)
    
    if not sentences:
        return [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    chunks = []
    current_chunk = ""
    
    for sent in sentences:
        if len(current_chunk) + len(sent) <= max_length:
            current_chunk += sent
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(sent) > max_length:
                for i in range(0, len(sent), max_length):
                    chunks.append(sent[i:i+max_length].strip())
                current_chunk = ""
            else:
                current_chunk = sent
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

# ==================== 翻译函数 ====================
def translate_single(text: str, target_lang: str, source_lang: str = None,
                     terms: dict = None, context: str = None,
                     temperature: float = 0.7, top_p: float = 0.6, 
                     top_k: int = 20, repetition_penalty: float = 1.1,
                     max_new_tokens: int = 2048) -> str:
    """翻译单个文本块"""
    model, tokenizer = gpu.load()
    target_name = LANGUAGES.get(target_lang, target_lang)
    
    # 检测输入是否包含中文
    def has_chinese(s):
        return any('\u4e00' <= c <= '\u9fff' for c in s)
    
    # 判断是否使用中文 prompt
    input_is_chinese = source_lang in ["zh", "zh-Hant"] or (source_lang is None and has_chinese(text))
    use_chinese_prompt = input_is_chinese or target_lang in ["zh", "zh-Hant"]
    
    if use_chinese_prompt:
        if context:
            prompt = context + "\n参考上面的信息，把下面的文本翻译成" + target_name + "，注意不需要翻译上文，也不要额外解释：\n" + text
        else:
            prompt = "请将以下中文文本完整翻译为" + target_name + "，必须全部翻译成" + target_name + "，不要保留任何中文，不要解释：\n\n" + text
        if terms:
            term_str = "\n".join([k + " 翻译成 " + v for k, v in terms.items()])
            prompt = "参考下面的翻译：\n" + term_str + "\n\n" + prompt
    else:
        if context:
            prompt = context + "\nRefer to the above, translate the following into " + target_name + ", without additional explanation:\n" + text
        else:
            prompt = "Translate the following segment into " + target_name + ", without additional explanation.\n\n" + text
        if terms:
            term_str = "\n".join([k + " -> " + v for k, v in terms.items()])
            prompt = "Use these translations:\n" + term_str + "\n\n" + prompt
    
    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    
    if hasattr(inputs, 'input_ids'):
        input_ids = inputs.input_ids.to(model.device)
    else:
        input_ids = inputs.to(model.device)
    
    input_len = input_ids.shape[1]
    outputs = model.generate(
        input_ids, max_new_tokens=max_new_tokens, do_sample=True,
        top_k=top_k, top_p=top_p, temperature=temperature,
        repetition_penalty=repetition_penalty, pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True).strip()

def _smart_truncate(text: str, max_len: int) -> str:
    """智能截取"""
    if len(text) <= max_len:
        return text
    truncated = text[-max_len:]
    for sep in ['. ', '。', '！', '？', '! ', '? ']:
        pos = truncated.find(sep)
        if 0 < pos < len(truncated) - 30:
            return truncated[pos + len(sep):]
    return truncated


def translate(text: str, target_lang: str, source_lang: str = None,
              terms: dict = None, context: str = None,
              temperature: float = 0.7, top_p: float = 0.6, 
              top_k: int = 20, repetition_penalty: float = 1.1,
              max_new_tokens: int = 2048, auto_split: bool = True) -> dict:
    """翻译文本 - 带重试机制"""
    start_time = time.time()
    chunks = split_text(text) if auto_split else [text]
    results = []
    
    def has_chinese(s):
        return any('\u4e00' <= c <= '\u9fff' for c in s)
    
    for i, chunk in enumerate(chunks):
        current_context = context if i == 0 else None
        
        # 使用用户设置的温度
        actual_temp = temperature
        result = translate_single(
            text=chunk, target_lang=target_lang, source_lang=source_lang,
            terms=terms, context=current_context, temperature=actual_temp,
            top_p=top_p, top_k=top_k, repetition_penalty=repetition_penalty,
            max_new_tokens=max_new_tokens
        )
        
        # 如果目标语言不是中文，但结果包含大量中文，重试一次
        if target_lang not in ["zh", "zh-Hant"] and has_chinese(result):
            chinese_ratio = sum(1 for c in result if '\u4e00' <= c <= '\u9fff') / max(len(result), 1)
            if chinese_ratio > 0.3:  # 超过30%是中文，重试
                result = translate_single(
                    text=chunk, target_lang=target_lang, source_lang=source_lang,
                    terms=terms, context=None, temperature=0.5,  # 降低温度
                    top_p=top_p, top_k=top_k, repetition_penalty=1.15,
                    max_new_tokens=max_new_tokens
                )
        
        results.append(result)
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    final_result = "\n".join(results) if len(results) > 1 else results[0]
    
    return {
        "result": final_result,
        "elapsed_ms": elapsed_ms,
        "chunks": len(chunks),
        "input_length": len(text),
        "output_length": len(final_result)
    }


async def translate_stream(text: str, target_lang: str, source_lang: str = None,
                           terms: dict = None, context: str = None,
                           temperature: float = 0.7, top_p: float = 0.6,
                           top_k: int = 20, repetition_penalty: float = 1.1,
                           max_new_tokens: int = 2048) -> AsyncGenerator[str, None]:
    """流式翻译 - 逐段返回结果"""
    start_time = time.time()
    chunks = split_text(text)
    total_chunks = len(chunks)
    
    yield f"data: {json.dumps({'event': 'start', 'total_chunks': total_chunks, 'input_length': len(text)})}\n\n"
    
    results = []
    
    for i, chunk in enumerate(chunks):
        chunk_start = time.time()
        
        yield f"data: {json.dumps({'event': 'progress', 'chunk': i + 1, 'total': total_chunks, 'status': 'translating'})}\n\n"
        
        current_context = context if i == 0 else None
        
        # 使用用户设置的温度
        actual_temp = temperature
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda c=chunk, ctx=current_context: translate_single(
                text=c, target_lang=target_lang, source_lang=source_lang,
                terms=terms, context=ctx, temperature=temperature,
                top_p=top_p, top_k=top_k, repetition_penalty=repetition_penalty,
                max_new_tokens=max_new_tokens
            )
        )
        results.append(result)
        
        chunk_elapsed = int((time.time() - chunk_start) * 1000)
        
        yield f"data: {json.dumps({'event': 'chunk', 'chunk': i + 1, 'total': total_chunks, 'result': result, 'elapsed_ms': chunk_elapsed})}\n\n"
    
    total_elapsed = int((time.time() - start_time) * 1000)
    final_result = "\n".join(results)
    
    yield f"data: {json.dumps({'event': 'done', 'total_chunks': total_chunks, 'elapsed_ms': total_elapsed, 'output_length': len(final_result)})}\n\n"


# ==================== Pydantic 模型 ====================
class TranslateRequest(BaseModel):
    text: str = Field(..., description="待翻译文本")
    target_lang: str = Field(..., description="目标语言代码")
    source_lang: Optional[str] = Field(None, description="源语言代码")
    terms: Optional[dict] = Field(None, description="术语干预")
    context: Optional[str] = Field(None, description="上下文参考")
    temperature: float = Field(0.7, ge=0, le=2)
    top_p: float = Field(0.6, ge=0, le=1)
    top_k: int = Field(20, ge=1, le=100)
    repetition_penalty: float = Field(1.1, ge=1.0, le=2.0)
    max_new_tokens: int = Field(2048, ge=1, le=4096)
    auto_split: bool = Field(True, description="自动分段")
    stream: bool = Field(False, description="流式返回")

class TranslateResponse(BaseModel):
    status: str
    result: Optional[str] = None
    elapsed_ms: Optional[int] = None
    chunks: Optional[int] = None
    input_length: Optional[int] = None
    output_length: Optional[int] = None
    error: Optional[str] = None

# ==================== API 端点 ====================
@app.post("/api/translate")
async def api_translate(req: TranslateRequest):
    """翻译接口 - 支持流式和非流式"""
    try:
        if req.stream:
            return StreamingResponse(
                translate_stream(
                    text=req.text, target_lang=req.target_lang, source_lang=req.source_lang,
                    terms=req.terms, context=req.context, temperature=req.temperature,
                    top_p=req.top_p, top_k=req.top_k, repetition_penalty=req.repetition_penalty,
                    max_new_tokens=req.max_new_tokens
                ),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
            )
        else:
            result = translate(
                text=req.text, target_lang=req.target_lang, source_lang=req.source_lang,
                terms=req.terms, context=req.context, temperature=req.temperature,
                top_p=req.top_p, top_k=req.top_k, repetition_penalty=req.repetition_penalty,
                max_new_tokens=req.max_new_tokens, auto_split=req.auto_split
            )
            return TranslateResponse(status="success", **result)
    except Exception as e:
        return TranslateResponse(status="error", error=str(e))


@app.post("/api/translate/stream")
async def api_translate_stream(req: TranslateRequest):
    """流式翻译接口（专用端点）"""
    return StreamingResponse(
        translate_stream(
            text=req.text, target_lang=req.target_lang, source_lang=req.source_lang,
            terms=req.terms, context=req.context, temperature=req.temperature,
            top_p=req.top_p, top_k=req.top_k, repetition_penalty=req.repetition_penalty,
            max_new_tokens=req.max_new_tokens
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@app.post("/api/translate/file")
async def api_translate_file(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    source_lang: Optional[str] = Form(None),
    stream: bool = Form(True)
):
    """文件翻译接口 - 支持上传文本文件"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        if stream:
            return StreamingResponse(
                translate_stream(text=text, target_lang=target_lang, source_lang=source_lang),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
            )
        else:
            result = translate(text=text, target_lang=target_lang, source_lang=source_lang)
            return TranslateResponse(status="success", **result)
    except UnicodeDecodeError:
        return TranslateResponse(status="error", error="文件编码错误，请使用 UTF-8 编码")
    except Exception as e:
        return TranslateResponse(status="error", error=str(e))


class BatchRequest(BaseModel):
    texts: List[str]
    target_lang: str
    source_lang: Optional[str] = None
    terms: Optional[dict] = None

@app.post("/api/translate/batch")
async def api_translate_batch(req: BatchRequest):
    """批量翻译"""
    start_time = time.time()
    results = []
    for text in req.texts:
        t0 = time.time()
        try:
            r = translate(text=text, target_lang=req.target_lang, 
                         source_lang=req.source_lang, terms=req.terms)
            results.append({"status": "success", "result": r["result"], 
                          "elapsed_ms": int((time.time() - t0) * 1000)})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})
    
    return {
        "status": "success",
        "results": results,
        "total_elapsed_ms": int((time.time() - start_time) * 1000),
        "count": len(results)
    }


@app.get("/api/languages")
async def api_languages():
    return LANGUAGES


@app.get("/api/gpu/status")
async def api_gpu_status():
    return gpu.status()


@app.post("/api/gpu/offload")
async def api_gpu_offload():
    gpu._unload()
    return {"status": "ok"}
async def api_gpu_status():
    return gpu.status()

@app.get("/health")
async def health():
    return {"status": "ok", "gpu": gpu.status()}


@app.get("/api/config")
async def api_config():
    return {
        "model_name": MODEL_NAME,
        "max_chunk_length": MAX_CHUNK_LENGTH,
        "gpu_idle_timeout": GPU_IDLE_TIMEOUT,
        "supported_languages": len(LANGUAGES),
        "default_params": {
            "temperature": 0.7,
            "top_p": 0.6,
            "top_k": 20,
            "repetition_penalty": 1.1,
            "max_new_tokens": 2048
        }
    }


# ==================== 静态文件和首页 ====================
@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("/app/templates/index.html")

app.mount("/static", StaticFiles(directory="/app/static"), name="static")
