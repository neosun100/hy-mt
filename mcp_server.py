"""HY-MT MCP 服务器 - 完整版"""
import os
import sys
from fastmcp import FastMCP

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mcp = FastMCP("hy-mt")

from app_fastapi import gpu, translate, LANGUAGES, split_text, MAX_CHUNK_LENGTH


@mcp.tool()
def translate_text(
    text: str,
    target_lang: str,
    source_lang: str = None,
    context: str = None,
    temperature: float = 0.7,
    top_p: float = 0.6,
    top_k: int = 20,
    repetition_penalty: float = 1.05,
    max_new_tokens: int = 2048,
    auto_split: bool = True
) -> dict:
    """
    翻译文本到目标语言
    
    Args:
        text: 待翻译的文本
        target_lang: 目标语言代码 (zh/en/ja/ko/fr/de/es/ru/ar 等38种)
        source_lang: 源语言代码 (可选，自动检测)
        context: 上下文参考 (可选)
        temperature: 生成温度 0-2 (默认0.7，越高越随机)
        top_p: 核采样概率 0-1 (默认0.6)
        top_k: Top-K采样 1-100 (默认20)
        repetition_penalty: 重复惩罚 1-2 (默认1.05)
        max_new_tokens: 最大生成token数 (默认2048)
        auto_split: 自动分段长文本 (默认True)
    
    Returns:
        包含 result, elapsed_ms, chunks 等信息的字典
    """
    try:
        data = translate(
            text=text, target_lang=target_lang, source_lang=source_lang,
            context=context, temperature=temperature, top_p=top_p,
            top_k=top_k, repetition_penalty=repetition_penalty,
            max_new_tokens=max_new_tokens, auto_split=auto_split
        )
        return {"status": "success", **data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def translate_with_terms(
    text: str,
    target_lang: str,
    terms: dict,
    source_lang: str = None,
    temperature: float = 0.7,
    top_p: float = 0.6,
    top_k: int = 20
) -> dict:
    """
    使用术语干预进行翻译
    
    Args:
        text: 待翻译的文本
        target_lang: 目标语言代码
        terms: 术语映射字典，如 {"API": "接口", "cache": "缓存"}
        source_lang: 源语言代码 (可选)
        temperature: 生成温度 (默认0.7)
        top_p: 核采样概率 (默认0.6)
        top_k: Top-K采样 (默认20)
    
    Returns:
        翻译结果
    """
    try:
        data = translate(
            text=text, target_lang=target_lang, source_lang=source_lang,
            terms=terms, temperature=temperature, top_p=top_p, top_k=top_k
        )
        return {"status": "success", **data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def translate_batch(
    texts: list,
    target_lang: str,
    source_lang: str = None,
    terms: dict = None
) -> dict:
    """
    批量翻译多个文本
    
    Args:
        texts: 待翻译文本列表
        target_lang: 目标语言代码
        source_lang: 源语言代码 (可选)
        terms: 术语映射 (可选)
    
    Returns:
        包含所有翻译结果的列表
    """
    import time
    start = time.time()
    results = []
    for text in texts:
        try:
            data = translate(text=text, target_lang=target_lang, source_lang=source_lang, terms=terms)
            results.append({"status": "success", "result": data["result"], "elapsed_ms": data["elapsed_ms"]})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})
    
    return {
        "status": "success",
        "results": results,
        "total_elapsed_ms": int((time.time() - start) * 1000),
        "count": len(results)
    }


@mcp.tool()
def get_gpu_status() -> dict:
    """获取 GPU 状态，包括显存使用、模型加载状态等"""
    return gpu.status()


@mcp.tool()
def release_gpu() -> dict:
    """释放 GPU 显存，卸载模型"""
    gpu.offload()
    return {"status": "ok", "message": "GPU memory released"}


@mcp.tool()
def list_languages() -> dict:
    """获取支持的38种语言列表及其代码"""
    return LANGUAGES


@mcp.tool()
def get_config() -> dict:
    """获取服务配置信息"""
    from app_fastapi import MODEL_NAME, GPU_IDLE_TIMEOUT
    return {
        "model_name": MODEL_NAME,
        "gpu_idle_timeout": GPU_IDLE_TIMEOUT,
        "max_chunk_length": MAX_CHUNK_LENGTH,
        "supported_languages": len(LANGUAGES),
        "default_params": {
            "temperature": 0.7,
            "top_p": 0.6,
            "top_k": 20,
            "repetition_penalty": 1.05,
            "max_new_tokens": 2048
        }
    }


if __name__ == "__main__":
    mcp.run()
