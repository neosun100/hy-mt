#!/usr/bin/env python3
"""
HY-MT 多模型性能测试脚本

用法:
    python benchmark.py [--api-url URL] [--runs N] [--output FILE]

示例:
    python benchmark.py
    python benchmark.py --api-url http://localhost:8021 --runs 5
    python benchmark.py --output results.json
"""

import requests
import json
import time
import argparse
from datetime import datetime

# 默认配置
DEFAULT_API_URL = "http://localhost:8021"
DEFAULT_RUNS = 3

# 测试文本
TEXTS = {
    "短文本": "Artificial intelligence is transforming how we live and work.",
    
    "中等文本": """Machine learning has revolutionized many industries in recent years. 
From healthcare to finance, AI systems are now capable of analyzing vast amounts of data 
and making predictions that were previously impossible. Natural language processing enables 
computers to understand and generate human language, while computer vision allows machines 
to interpret visual information from the world around us. These technologies are becoming 
increasingly integrated into our daily lives, from voice assistants to recommendation systems.""",
    
    "长文本": """The rapid advancement of artificial intelligence and machine learning technologies 
has fundamentally transformed the landscape of modern computing and its applications across 
virtually every sector of the global economy. In healthcare, AI-powered diagnostic tools are 
now capable of detecting diseases with accuracy that rivals or even surpasses human physicians, 
analyzing medical images, genetic data, and patient histories to provide personalized treatment 
recommendations. The financial industry has embraced algorithmic trading systems and fraud 
detection mechanisms that process millions of transactions in real-time, identifying patterns 
and anomalies that would be impossible for human analysts to detect.

In the realm of transportation, autonomous vehicles represent one of the most visible applications 
of AI technology, combining computer vision, sensor fusion, and deep learning to navigate complex 
environments safely. Manufacturing facilities increasingly rely on robotic systems guided by 
machine learning algorithms to optimize production processes, predict equipment failures, and 
maintain quality control standards. The entertainment industry has been transformed by 
recommendation engines that analyze user preferences and behavior to suggest content, while 
creative AI tools are now capable of generating music, art, and even written content.

Education is being revolutionized by adaptive learning platforms that customize instruction 
based on individual student needs and learning patterns. Customer service has been enhanced 
through intelligent chatbots and virtual assistants that can handle routine inquiries and 
provide 24/7 support. Scientific research has accelerated dramatically with AI systems that 
can analyze experimental data, simulate complex phenomena, and even propose new hypotheses 
for investigation.""",

    "超长文本": """The history of artificial intelligence spans several decades, beginning with 
the foundational work of pioneers like Alan Turing, who proposed the famous Turing Test as a 
measure of machine intelligence. The field officially emerged as an academic discipline at the 
Dartmouth Conference in 1956, where researchers gathered to explore the possibility of creating 
machines that could simulate human intelligence. Early AI research focused on symbolic reasoning 
and expert systems, which attempted to encode human knowledge into rule-based systems.

The development of neural networks represented a paradigm shift in AI research. Inspired by the 
structure of biological brains, these computational models consist of interconnected nodes that 
process information in layers. The backpropagation algorithm, developed in the 1980s, enabled 
efficient training of multi-layer networks, though computational limitations initially restricted 
their practical applications. The resurgence of neural networks in the 2010s, powered by advances 
in GPU computing and the availability of large datasets, led to the deep learning revolution.

Convolutional neural networks have achieved remarkable success in computer vision tasks, from 
image classification to object detection and semantic segmentation. These architectures exploit 
the spatial structure of visual data through convolutional layers that learn hierarchical 
representations of features. Transfer learning techniques allow models trained on large datasets 
to be fine-tuned for specific applications, dramatically reducing the data and computational 
requirements for new tasks.

Recurrent neural networks and their variants, including Long Short-Term Memory networks and 
Gated Recurrent Units, have proven effective for sequential data processing. These architectures 
maintain internal state that allows them to capture temporal dependencies in data, making them 
suitable for applications like speech recognition, language modeling, and time series prediction. 
The attention mechanism, introduced to address limitations in processing long sequences, has 
become a fundamental component of modern NLP systems.

The Transformer architecture, introduced in 2017, revolutionized natural language processing by 
enabling parallel processing of sequential data through self-attention mechanisms. This innovation 
led to the development of large language models like BERT, GPT, and their successors, which have 
achieved unprecedented performance on a wide range of language understanding and generation tasks. 
These models are pre-trained on massive text corpora and can be fine-tuned for specific applications.

Reinforcement learning represents another major branch of AI research, focusing on training agents 
to make decisions through interaction with environments. Notable achievements include systems that 
have mastered complex games like Go and StarCraft, as well as applications in robotics, resource 
management, and autonomous systems. The combination of deep learning with reinforcement learning 
has enabled agents to learn directly from raw sensory inputs without hand-crafted features.

The ethical implications of AI development have become increasingly important as these technologies 
become more powerful and pervasive. Concerns about bias in AI systems, privacy implications of 
data collection, the potential for job displacement, and the long-term risks of artificial general 
intelligence have prompted calls for responsible AI development practices and regulatory frameworks. 
Researchers and policymakers are working to establish guidelines that ensure AI systems are 
developed and deployed in ways that benefit humanity while minimizing potential harms.

Looking forward, the field continues to evolve rapidly with research into more efficient 
architectures, multimodal learning systems that can process multiple types of data simultaneously, 
and approaches to achieving more general forms of intelligence. The integration of AI with other 
emerging technologies like quantum computing, biotechnology, and advanced materials science 
promises to unlock new capabilities and applications that we can only begin to imagine today."""
}


def get_models(api_url):
    """获取可用模型列表"""
    resp = requests.get(f"{api_url}/api/models", timeout=30)
    data = resp.json()
    return list(data.get("models", {}).keys())


def switch_model(api_url, model):
    """切换模型"""
    resp = requests.post(
        f"{api_url}/api/models/switch",
        json={"model": model},
        timeout=300
    )
    return resp.json()


def translate(api_url, text):
    """执行翻译"""
    resp = requests.post(
        f"{api_url}/api/translate",
        json={"text": text, "target_lang": "zh"},
        timeout=600
    )
    return resp.json()


def run_benchmark(api_url, runs=3):
    """运行性能测试"""
    print(f"HY-MT 多模型性能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址: {api_url}")
    print(f"每项测试次数: {runs}")
    
    # 获取模型列表
    models = get_models(api_url)
    print(f"\n可用模型: {len(models)} 个")
    for m in models:
        print(f"  - {m}")
    
    print(f"\n文本长度统计:")
    for name, text in TEXTS.items():
        print(f"  {name}: {len(text)} 字符")
    
    results = {
        "meta": {
            "test_time": datetime.now().isoformat(),
            "api_url": api_url,
            "runs_per_test": runs,
            "models": models,
            "text_lengths": {k: len(v) for k, v in TEXTS.items()}
        },
        "results": {}
    }
    
    for model in models:
        print(f"\n{'='*60}")
        print(f"测试模型: {model}")
        print(f"{'='*60}")
        
        # 切换模型
        switch_result = switch_model(api_url, model)
        if switch_result.get("status") != "success":
            print(f"  ❌ 切换失败: {switch_result}")
            continue
        print(f"  ✓ 模型加载完成 ({switch_result.get('elapsed_ms', 0)}ms)")
        
        results["results"][model] = {}
        
        for text_type, text in TEXTS.items():
            print(f"\n  测试 {text_type} ({len(text)} 字符)...")
            times = []
            
            for run in range(runs):
                resp = translate(api_url, text)
                if resp.get("status") == "success":
                    elapsed = resp["elapsed_ms"]
                    times.append(elapsed)
                    print(f"    第{run+1}次: {elapsed}ms")
                else:
                    print(f"    第{run+1}次: 失败 - {resp.get('error')}")
            
            if times:
                best = min(times)
                avg = sum(times) / len(times)
                results["results"][model][text_type] = {
                    "best_ms": best,
                    "avg_ms": round(avg, 1),
                    "all_runs_ms": times,
                    "text_length": len(text)
                }
                print(f"    最佳: {best}ms, 平均: {avg:.1f}ms")
    
    return results


def print_summary(results):
    """打印结果汇总表"""
    print("\n\n" + "="*80)
    print("测试结果汇总 (最佳耗时 ms)")
    print("="*80)
    
    models = list(results["results"].keys())
    text_types = list(TEXTS.keys())
    
    # 表头
    header = f"{'模型':<35}"
    for tt in text_types:
        header += f" {tt:>10}"
    print(header)
    print("-"*80)
    
    # 数据行
    for model in models:
        row = f"{model:<35}"
        for text_type in text_types:
            if text_type in results["results"].get(model, {}):
                ms = results["results"][model][text_type]["best_ms"]
                row += f" {ms:>10}"
            else:
                row += f" {'N/A':>10}"
        print(row)
    
    print("\n" + "="*80)
    print("测试结果汇总 (秒)")
    print("="*80)
    print(header)
    print("-"*80)
    
    for model in models:
        row = f"{model:<35}"
        for text_type in text_types:
            if text_type in results["results"].get(model, {}):
                ms = results["results"][model][text_type]["best_ms"]
                row += f" {ms/1000:>10.1f}s"
            else:
                row += f" {'N/A':>10}"
        print(row)


def main():
    parser = argparse.ArgumentParser(description="HY-MT 多模型性能测试")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API 地址")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS, help="每项测试次数")
    parser.add_argument("--output", default="benchmark_results.json", help="输出文件")
    args = parser.parse_args()
    
    # 运行测试
    results = run_benchmark(args.api_url, args.runs)
    
    # 保存结果
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存到: {args.output}")
    
    # 打印汇总
    print_summary(results)


if __name__ == "__main__":
    main()
