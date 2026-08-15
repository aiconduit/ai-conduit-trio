# AI Conduit Trio Pipeline

3つのクリエイタースタイルを真似したYouTube Shorts自動生成パイプライン。

## スタイル

| スタイル | 参考クリエイター | 特徴 |
|---------|--------------|------|
| **Fireship** | Fireship (4.2M登録) | 高速コード解説・ユーモア・コードハイライト |
| **ByteByteGo** | ByteByteGo (1M登録) | 図解アニメーション・システム設計 |
| **ONI** | ONI自動化の鬼 | 実用的AI副業・具体的数字・日本語 |

## 構成
- パイプライン2（ai-conduit-pipeline）とは完全独立
- GitHub Actionsで毎日21:00 JST自動生成
- Gemini APIで台本生成
- edge-TTSで音声生成（KeitaNeural）

## フォルダ構成

pipeline12_trio/
├── .github/workflows/pipeline12_trio.yml
├── scripts/
│ ├── script_generator.py # Geminiで台本生成
│ ├── fireship_style.py # コードハイライト動画
│ ├── bytebyteGo_style.py # 図解アニメーション動画
│ ├── oni_style.py # テキスト強調動画
│ ├── tts_generator.py # 音声生成
│ ├── subtitle_generator.py # 字幕生成
│ └── uploader.py # YouTube投稿
├── assets/
│ ├── bgm/ # BGM
│ └── fonts/ # フォント
└── output/ # 生成動画

