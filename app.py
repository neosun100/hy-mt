"""HY-MT 翻译服务 - UI + API + GPU 管理"""
import os
import time
import threading
import torch
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from flasgger import Swagger
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template={
    "info": {"title": "HY-MT 翻译 API", "version": "1.5"},
    "basePath": "/api"
})

# 配置
MODEL_NAME = os.getenv("MODEL_NAME", "tencent/HY-MT1.5-1.8B")
GPU_IDLE_TIMEOUT = int(os.getenv("GPU_IDLE_TIMEOUT", "300"))

# 支持的语言
LANGUAGES = {
    "zh": "中文", "en": "English", "ja": "日本語", "ko": "한국어",
    "fr": "Français", "de": "Deutsch", "es": "Español", "pt": "Português",
    "ru": "Русский", "ar": "العربية", "th": "ไทย", "vi": "Tiếng Việt",
    "it": "Italiano", "nl": "Nederlands", "pl": "Polski", "tr": "Türkçe",
    "id": "Bahasa Indonesia", "ms": "Bahasa Melayu", "hi": "हिन्दी",
    "zh-Hant": "繁體中文", "cs": "Čeština", "uk": "Українська",
    "fa": "فارسی", "he": "עברית", "bn": "বাংলা", "ta": "தமிழ்",
    "te": "తెలుగు", "mr": "मराठी", "gu": "ગુજરાતી", "ur": "اردو",
    "km": "ភាសាខ្មែរ", "my": "မြန်မာ", "tl": "Filipino",
    "bo": "བོད་སྐད", "kk": "Қазақша", "mn": "Монгол", "ug": "ئۇيغۇرچە", "yue": "粵語"
}


class GPUManager:
    """GPU 资源管理器"""
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.lock = threading.Lock()
        self.last_used = 0
        self._start_idle_checker()

    def _start_idle_checker(self):
        def checker():
            while True:
                time.sleep(60)
                if self.model and time.time() - self.last_used > GPU_IDLE_TIMEOUT:
                    self.offload()
        t = threading.Thread(target=checker, daemon=True)
        t.start()

    def load(self):
        with self.lock:
            if self.model is None:
                print(f"Loading model: {MODEL_NAME}")
                self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                self.model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME, device_map="auto", torch_dtype=torch.bfloat16
                )
            self.last_used = time.time()
            return self.model, self.tokenizer

    def offload(self):
        with self.lock:
            if self.model:
                del self.model
                self.model = None
                if self.tokenizer:
                    del self.tokenizer
                    self.tokenizer = None
                torch.cuda.empty_cache()
                print("GPU memory released")

    def status(self):
        if torch.cuda.is_available():
            mem = torch.cuda.mem_get_info()
            return {
                "loaded": self.model is not None,
                "gpu_free_mb": mem[0] // 1024 // 1024,
                "gpu_total_mb": mem[1] // 1024 // 1024,
                "idle_seconds": int(time.time() - self.last_used) if self.model else None
            }
        return {"loaded": False, "error": "No GPU"}


gpu = GPUManager()


def translate(text: str, target_lang: str, source_lang: str = None,
              terms: dict = None, context: str = None,
              temperature: float = 0.7, top_p: float = 0.6, top_k: int = 20) -> str:
    """执行翻译"""
    import traceback
    try:
        model, tokenizer = gpu.load()
        
        # 构建 prompt
        target_name = LANGUAGES.get(target_lang, target_lang)
        
        if source_lang in ["zh", "zh-Hant"] or target_lang in ["zh", "zh-Hant"]:
            prompt = f"将以下文本翻译为{target_name}，注意只需要输出翻译后的结果，不要额外解释：\n\n{text}"
            if terms:
                term_str = "\n".join([f"{k} 翻译成 {v}" for k, v in terms.items()])
                prompt = f"参考下面的翻译：\n{term_str}\n\n{prompt}"
            if context:
                prompt = f"{context}\n参考上面的信息，把下面的文本翻译成{target_name}，注意不需要翻译上文，也不要额外解释：\n{text}"
        else:
            prompt = f"Translate the following segment into {target_name}, without additional explanation.\n\n{text}"
        
        messages = [{"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
        
        # inputs 可能是 tensor 或 BatchEncoding
        if hasattr(inputs, 'input_ids'):
            input_ids = inputs.input_ids.to(model.device)
        else:
            input_ids = inputs.to(model.device)
        
        input_len = input_ids.shape[1]
        
        outputs = model.generate(
            input_ids,
            max_new_tokens=2048,
            do_sample=True,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
        )
        
        result = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
        return result.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        traceback.print_exc()
        raise


# ==================== API 路由 ====================

@app.route("/health")
def health():
    """健康检查"""
    return jsonify({"status": "ok", "gpu": gpu.status()})


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """
    翻译文本
    ---
    tags: [翻译]
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [text, target_lang]
          properties:
            text: {type: string, description: 待翻译文本}
            target_lang: {type: string, description: 目标语言代码}
            source_lang: {type: string, description: 源语言代码(可选)}
            terms: {type: object, description: 术语干预(可选)}
            context: {type: string, description: 上下文(可选)}
            temperature: {type: number, default: 0.7}
            top_p: {type: number, default: 0.6}
            top_k: {type: integer, default: 20}
    responses:
      200:
        description: 翻译结果
        schema:
          properties:
            result: {type: string}
            status: {type: string}
    """
    import traceback
    data = request.json
    try:
        result = translate(
            text=data["text"],
            target_lang=data["target_lang"],
            source_lang=data.get("source_lang"),
            terms=data.get("terms"),
            context=data.get("context"),
            temperature=data.get("temperature", 0.7),
            top_p=data.get("top_p", 0.6),
            top_k=data.get("top_k", 20)
        )
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        error_msg = str(e) or traceback.format_exc()
        print(f"API error: {error_msg}")
        return jsonify({"status": "error", "error": error_msg}), 500


@app.route("/api/gpu/status")
def api_gpu_status():
    """
    获取 GPU 状态
    ---
    tags: [GPU]
    responses:
      200:
        description: GPU 状态信息
    """
    return jsonify(gpu.status())


@app.route("/api/gpu/offload", methods=["POST"])
def api_gpu_offload():
    """
    释放 GPU 显存
    ---
    tags: [GPU]
    responses:
      200:
        description: 操作结果
    """
    gpu.offload()
    return jsonify({"status": "success", "message": "GPU memory released"})


@app.route("/api/languages")
def api_languages():
    """
    获取支持的语言列表
    ---
    tags: [翻译]
    responses:
      200:
        description: 语言列表
    """
    return jsonify(LANGUAGES)


# ==================== UI 路由 ====================

@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)


@app.route("/docs")
def docs():
    return app.send_static_file("swagger-ui.html") if os.path.exists("static/swagger-ui.html") else ("Swagger UI at /apidocs", 302, {"Location": "/apidocs"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8021, threaded=True)
