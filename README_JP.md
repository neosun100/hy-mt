<p align="center">
  <img src="imgs/hunyuanlogo.png" width="400"/>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">简体中文</a> | <a href="README_TW.md">繁體中文</a> | <b>日本語</b>
</p>

<p align="center">
  <a href="https://hub.docker.com/r/neosun/hy-mt"><img src="https://img.shields.io/docker/pulls/neosun/hy-mt?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <a href="https://github.com/neosun100/hy-mt/stargazers"><img src="https://img.shields.io/github/stars/neosun100/hy-mt?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/neosun100/hy-mt/blob/main/License.txt"><img src="https://img.shields.io/badge/license-Tencent_Hunyuan-blue?style=flat-square" alt="License"></a>
  <a href="https://huggingface.co/tencent/HY-MT1.5-1.8B"><img src="https://img.shields.io/badge/🤗-HuggingFace-yellow?style=flat-square" alt="HuggingFace"></a>
</p>

# HY-MT 翻訳サービス

> 🚀 Tencent HunyuanMT 1.5 翻訳モデルの All-in-One Docker デプロイメント。Web UI、REST API、MCP Server をサポート。

## ✨ 機能

- 🌐 **38言語対応** - 中国語、英語、日本語、韓国語、フランス語、ドイツ語、スペイン語など
- 🎨 **モダンな Web UI** - ダーク/ライトテーマ切替、ドラッグ＆ドロップアップロード、リアルタイム進捗表示
- ⚡ **ストリーミング翻訳** - Server-Sent Events (SSE) によるリアルタイム出力、長文翻訳に最適
- 🔧 **完全なパラメータ制御** - Temperature、Top-P、Top-K、繰り返しペナルティなど調整可能
- 📚 **用語介入** - カスタム用語マッピング、専門分野の翻訳に対応
- 🤖 **MCP Server** - Model Context Protocol 対応、Claude などの AI アシスタントと統合可能
- 🐳 **ワンクリックデプロイ** - All-in-One Docker イメージ、全モデルプリインストール
- 🔄 **スマート GPU 管理** - GPU 自動選択、アイドルタイムアウト、メモリ解放
- 🔀 **マルチモデル対応** - 4種類のモデルを自由に切替（1.8B/7B、ベース/FP8）

## 🎯 モデル選択ガイド

| モデル | VRAM | 速度 | 品質 | 推奨シーン |
|--------|------|------|------|------------|
| **HY-MT 7B** | 16GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🏆 **最推奨** - 最高品質、高速 |
| HY-MT 1.8B | 6GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | VRAM が限られている場合の最良選択 |
| HY-MT 1.8B FP8 | 4GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | VRAM が極めて限られている場合（<6GB） |
| HY-MT 7B FP8 | 10GB | ⭐⭐ | ⭐⭐⭐⭐⭐ | 7B 品質が欲しいが VRAM が足りない場合 |

> 💡 **アドバイス**：VRAM が 16GB 以上あれば、**HY-MT 7B** を使用してください。FP8 モデルは VRAM を節約しますが、実行時の解凍により遅くなります。

## 📸 スクリーンショット

<p align="center">
  <img src="docs/images/ui-screenshot-v2.0.1.png" width="800"/>
</p>

## 🚀 クイックスタート

### 方法1：Docker Run（推奨）

```bash
# 1コマンドで起動（デフォルトで 7B モデルを使用）
docker run -d --gpus all \
  -p 8021:8021 \
  -v ./models:/app/models \
  --name hy-mt \
  neosun/hy-mt:latest

# Web UI にアクセス
open http://localhost:8021
```

Docker イメージ（約43GB）には全4モデルがプリインストールされています。追加ダウンロード不要！

### 方法2：Docker Compose

`docker-compose.yml` を作成：

```yaml
services:
  hy-mt:
    image: neosun/hy-mt:latest
    container_name: hy-mt
    ports:
      - "8021:8021"
    environment:
      - MODEL_NAME=tencent/HY-MT1.5-7B  # 16GB+ VRAM 推奨
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

## 📋 システム要件

| 要件 | 最小構成 | 推奨構成 |
|------|----------|----------|
| GPU | NVIDIA GPU 6GB+ VRAM | 16GB+ VRAM（7B モデル用） |
| CUDA | 11.8+ | 12.4+ |
| Docker | 20.10+ | 24.0+ |
| nvidia-docker | 必須 | - |

### GPU サポートの確認

```bash
# NVIDIA ドライバを確認
nvidia-smi

# Docker GPU サポートを確認
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## 📊 パフォーマンスベンチマーク

テスト環境：**NVIDIA L40S GPU**、翻訳方向：英語 → 中国語

| モデル | 短文 (61文字) | 中文 (530文字) | 長文 (1.8K文字) | 超長文 (4.2K文字) |
|--------|---------------|----------------|-----------------|-------------------|
| **HY-MT 7B** | 0.4s | 4.4s | 17.7s | 43.0s |
| HY-MT 1.8B | 0.4s | 3.6s | 14.0s | 32.3s |
| HY-MT 1.8B FP8 | 1.1s | 10.8s | 38.1s | 92.9s |
| HY-MT 7B FP8 | 2.9s | 28.5s | 115.6s | 274.1s |

### ⚠️ なぜ FP8 量子化モデルは遅いのか？

これは**直感に反するが技術的に正しい**現象です：

| 比較 | 速度変化 | 理由 |
|------|----------|------|
| 1.8B FP8 vs 1.8B | **2.7倍遅い** | 実行時の解凍オーバーヘッド |
| 7B FP8 vs 7B | **6.4倍遅い** | パラメータが多い = 解凍処理が多い |

**FP8 量子化の目的は VRAM 節約であり、高速化ではありません！** モデルは 8-bit で保存されますが、GPU 計算時には 16-bit に動的解凍する必要があり、この処理は各トークン生成時に発生します。

**FP8 を使うべき場合：**
- ✅ VRAM が限られている場合（7B は <16GB、1.8B は <6GB）
- ❌ 速度最適化には不向き
- ❌ バッチ処理には不向き（速度損失が累積）

詳細は [ベンチマークレポート](docs/BENCHMARK_REPORT.md) を参照。

## 🔑 重要な最適化：チャンクサイズ

**重要な発見**：チャンクサイズが小さいほど、翻訳品質が向上

| チャンクサイズ | 品質 | 備考 |
|----------------|------|------|
| 500文字 | ❌ 低 | 言語混在、モデルが「手抜き」 |
| 300文字 | ⚠️ 中 | 一部未翻訳 |
| **150文字** | ✅ 高 | 完全で正確な翻訳 |

サービスはデフォルトで `MAX_CHUNK_LENGTH=150` を使用し、最適な品質を実現。

**理由**：HY-MT モデルは長い入力に対して「手抜き」傾向があり、一部のみ翻訳することがあります。短いチャンクにすることで、各セグメントを完全に翻訳させます。

詳細は [最適化ガイド](docs/OPTIMIZATION_GUIDE.md) を参照。

## ⚙️ 設定

### 環境変数

| 変数 | デフォルト | 説明 |
|------|------------|------|
| `PORT` | 8021 | サービスポート |
| `MODEL_NAME` | tencent/HY-MT1.5-7B | HuggingFace モデル名 |
| `MODEL_PATH` | ./models | ローカルモデルキャッシュパス |
| `GPU_IDLE_TIMEOUT` | 300 | GPU アイドルタイムアウト自動解放（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 自動 | GPU ID（空欄で自動選択） |
| `HF_ENDPOINT` | https://huggingface.co | HuggingFace ミラー URL |

### .env ファイルの使用

```bash
# サンプル設定をコピー
cp .env.example .env

# 設定を編集
vim .env
```

## 📖 API 使用方法

### 基本翻訳

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "ja"
  }'
```

レスポンス：
```json
{
  "status": "success",
  "result": "こんにちは、お元気ですか？",
  "elapsed_ms": 358,
  "model": "tencent/HY-MT1.5-7B",
  "chunks": 1
}
```

### ストリーミング翻訳（SSE）

```bash
curl -N "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "翻訳する長い記事...",
    "target_lang": "en",
    "stream": true
  }'
```

### 用語介入

```bash
curl -X POST "http://localhost:8021/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple released iPhone 16",
    "target_lang": "ja",
    "terms": {"Apple": "アップル社", "iPhone": "アイフォン"}
  }'
```

出力：`アップル社がアイフォン16を発売`

### ファイルアップロード翻訳

```bash
curl "http://localhost:8021/api/translate/file" \
  -F "file=@document.txt" \
  -F "target_lang=ja" \
  -F "stream=true"
```

### モデル切替

```bash
curl -X POST "http://localhost:8021/api/models/switch" \
  -H "Content-Type: application/json" \
  -d '{"model": "tencent/HY-MT1.5-1.8B"}'
```

## 📚 API エンドポイント

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/` | GET | Web UI |
| `/api/translate` | POST | テキスト翻訳（ストリーミング対応） |
| `/api/translate/file` | POST | ファイルアップロード翻訳 |
| `/api/translate/batch` | POST | バッチ翻訳 |
| `/api/translate/stream` | POST | ストリーミング翻訳（SSE） |
| `/api/languages` | GET | 対応言語一覧 |
| `/api/models` | GET | 利用可能なモデル一覧 |
| `/api/models/switch` | POST | 翻訳モデル切替 |
| `/api/gpu/status` | GET | GPU ステータスとメモリ情報 |
| `/api/gpu/offload` | POST | GPU メモリ解放 |
| `/api/config` | GET | サービス設定情報 |
| `/health` | GET | ヘルスチェック |
| `/docs` | GET | Swagger API ドキュメント |

## 🌍 対応言語

| 言語 | コード | 言語 | コード | 言語 | コード |
|------|--------|------|--------|------|--------|
| 中国語 | zh | 英語 | en | 日本語 | ja |
| 韓国語 | ko | フランス語 | fr | ドイツ語 | de |
| スペイン語 | es | ポルトガル語 | pt | ロシア語 | ru |
| アラビア語 | ar | タイ語 | th | ベトナム語 | vi |
| イタリア語 | it | オランダ語 | nl | ポーランド語 | pl |
| トルコ語 | tr | インドネシア語 | id | マレー語 | ms |
| ヒンディー語 | hi | 繁体字中国語 | zh-Hant | 広東語 | yue |

他17言語対応。完全なリストは `/api/languages` を参照。

## 🛠️ 技術スタック

- **モデル**: [Tencent HY-MT1.5](https://huggingface.co/tencent/HY-MT1.5-1.8B)（1.8B & 7B）
- **バックエンド**: FastAPI + Uvicorn
- **フロントエンド**: Vanilla JS + ダーク/ライトモード
- **コンテナ**: NVIDIA CUDA 12.4 ベースイメージ
- **ストリーミング**: Server-Sent Events (SSE)
- **MCP**: Model Context Protocol AI 統合

## 📁 プロジェクト構成

```
hy-mt/
├── app_fastapi.py      # FastAPI メインアプリケーション
├── mcp_server.py       # MCP Server（AI アシスタント統合）
├── benchmark.py        # パフォーマンスベンチマークスクリプト
├── templates/
│   └── index.html      # Web UI（ダーク/ライトテーマ）
├── docs/
│   ├── BENCHMARK_REPORT.md    # パフォーマンステストレポート
│   ├── OPTIMIZATION_GUIDE.md  # 長文最適化ガイド
│   └── QUICK_REFERENCE.md     # API クイックリファレンス
├── Dockerfile          # All-in-One Docker ビルド
├── docker-compose.yml  # Docker Compose 設定
├── start.sh           # クイックスタートスクリプト
├── test_api.sh        # API テストスクリプト
└── .env.example       # 環境変数テンプレート
```

## 🔧 高度な使用方法

### ローカル開発実行

```bash
# リポジトリをクローン
git clone https://github.com/neosun100/hy-mt.git
cd hy-mt

# 依存関係をインストール
pip install torch transformers accelerate fastapi uvicorn

# サービスを起動
python -m uvicorn app_fastapi:app --host 0.0.0.0 --port 8021
```

### MCP Server 統合

Claude Desktop などの AI アシスタントで使用する場合、MCP 設定を追加：

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

対応 MCP ツール：
- `translate` - テキスト翻訳
- `list_languages` - 対応言語一覧取得
- `list_models` - 利用可能なモデル一覧取得
- `switch_model` - 翻訳モデル切替

詳細は [MCP_GUIDE.md](MCP_GUIDE.md) を参照。

## 🐛 トラブルシューティング

| 問題 | 解決策 |
|------|--------|
| モデルダウンロードが遅い | `HF_ENDPOINT=https://hf-mirror.com` を設定（中国ミラー） |
| GPU メモリ不足 | 量子化モデルを使用：`tencent/HY-MT1.5-1.8B-FP8` |
| コンテナが起動しない | `nvidia-smi` と nvidia-docker のインストールを確認 |
| 翻訳が不完全 | 最適化済み、デフォルトチャンクサイズ 150 文字 |
| コンテナが unhealthy と表示 | 1-2分待機、モデル読み込み中 |

## 📝 更新履歴

### v2.0.1 (2026-01-03)
- 🏆 デフォルトモデルを **HY-MT 7B** に変更（最高品質・高速）
- 🩺 Docker HEALTHCHECK 追加、コンテナ状態監視可能
- 📦 コンテナ状態が `(healthy)` でサービス準備完了を表示

### v2.0.0 (2026-01-03) - 真の All-in-One
- 🎯 **全4モデルをイメージにプリインストール**、ダウンロード即使用
- 📦 イメージサイズ：約43GB
- 🏆 推奨：HY-MT 7B 最高品質・高速
- 📊 パフォーマンステストレポート追加
- 🔧 `benchmark.py` パフォーマンステストスクリプト追加

### v1.2.0 (2026-01-03)
- 🔀 マルチモデル対応（4モデル：1.8B、1.8B-FP8、7B、7B-FP8）
- 🔄 UI と API でモデル切替対応
- 📝 MCP Server に `list_models` と `switch_model` ツール追加
- 🐛 翻訳レスポンスのモデル名表示問題を修正

### v1.0.0 (2026-01-03)
- 🎉 初回リリース
- ✨ All-in-One Docker イメージ
- ⚡ SSE ストリーミング翻訳
- 🎨 ダーク/ライトテーマ Web UI
- 🔧 長文最適化（チャンクサイズ 150 文字）
- 🤖 MCP Server サポート

## 🤝 コントリビューション

コントリビューション歓迎！お気軽に Pull Request を提出してください。

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Request を作成

## 📄 ライセンス

このプロジェクトは [Tencent HunyuanMT](https://github.com/Tencent-Hunyuan/HY-MT) に基づいています。詳細は [License.txt](License.txt) を参照。

## 🙏 謝辞

- [Tencent Hunyuan](https://github.com/Tencent-Hunyuan/HY-MT) - オリジナル HY-MT モデル
- [HuggingFace](https://huggingface.co/tencent/HY-MT1.5-1.8B) - モデルホスティング

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/hy-mt&type=Date)](https://star-history.com/#neosun100/hy-mt)

## 📱 フォローする

<p align="center">
  <img src="https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png" width="300"/>
</p>
