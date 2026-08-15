#!/usr/bin/env python3
"""
台本生成 - Gemini APIを使って3スタイル対応
"""
import os, json, re, random, requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

STYLE_PROMPTS = {
    "fireship": """あなたはFireshipスタイルのYouTube Shortsクリエイターです。
高速・皮肉・ユーモア・コード解説が特徴。
日本語エンジニア向けに30秒のショート動画台本を作ってください。

フォーマット:
- Hook(0-3秒): 驚きの事実 or 「これ知ってた？」
- Core(3-25秒): コードの問題/解決を高速解説（コード例必須）
- CTA(25-30秒): 「もっと知りたければフォロー」

JSONのみ出力:
{"title": "タイトル(30文字以内)", "style": "fireship",
 "scenes": [
   {"id": 0, "type": "hook", "narration": "ナレーション(15文字以内)", "code": "コード例or空文字"},
   {"id": 1, "type": "code", "narration": "ナレーション", "code": "実際のコード"},
   {"id": 2, "type": "code", "narration": "ナレーション", "code": "実際のコード"},
   {"id": 3, "type": "result", "narration": "ナレーション", "code": ""},
   {"id": 4, "type": "cta", "narration": "フォローして最新情報を受け取ってください", "code": ""}
 ]}""",

    "bytebyteGo": """あなたはByteByteGoスタイルのYouTube Shortsクリエイターです。
システム設計・図解・アニメーションで解説するスタイル。
日本語エンジニア向けに30秒のショート動画台本を作ってください。

フォーマット:
- Hook(0-3秒): 「なぜXXXは〇〇なのか？」という問い
- Explain(3-25秒): 図解で説明（ステップバイステップ）
- Summary(25-30秒): まとめ+CTA

JSONのみ出力:
{"title": "タイトル(30文字以内)", "style": "bytebyteGo",
 "scenes": [
   {"id": 0, "type": "hook", "narration": "ナレーション(15文字以内)", "diagram": "図解の説明"},
   {"id": 1, "type": "explain", "narration": "ナレーション", "diagram": "ステップ1の図解"},
   {"id": 2, "type": "explain", "narration": "ナレーション", "diagram": "ステップ2の図解"},
   {"id": 3, "type": "explain", "narration": "ナレーション", "diagram": "ステップ3の図解"},
   {"id": 4, "type": "cta", "narration": "保存して後で確認してください", "diagram": ""}
 ]}""",

    "oni": """あなたはONI自動化の鬼スタイルのYouTube Shortsクリエイターです。
AI副業・具体的な数字・すぐ使える情報が特徴。
日本語エンジニア向けに30秒のショート動画台本を作ってください。

フォーマット:
- Hook(0-3秒): 「〇〇円稼げる」「〇〇分で完了」など具体的数字
- Value(3-25秒): 実際にできること・やり方を箇条書き3点
- CTA(25-30秒): 「コメントにAIと書いて」

JSONのみ出力:
{"title": "タイトル(30文字以内)", "style": "oni",
 "scenes": [
   {"id": 0, "type": "hook", "narration": "具体的数字で驚かせる一文(20文字以内)", "point": ""},
   {"id": 1, "type": "value", "narration": "ポイント1(20文字以内)", "point": "①"},
   {"id": 2, "type": "value", "narration": "ポイント2(20文字以内)", "point": "②"},
   {"id": 3, "type": "value", "narration": "ポイント3(20文字以内)", "point": "③"},
   {"id": 4, "type": "cta", "narration": "コメントにAIと書いてください", "point": ""}
 ]}"""
}

TOPICS = {
    "fireship": [
        "Claude CodeのHooksで自動化",
        "Python型ヒントの落とし穴",
        "非同期処理のよくある間違い",
        "GitのRebaseとMergeの違い",
        "DockerのMulti-stageビルド",
        "TypeScriptのUtility Types",
    ],
    "bytebyteGo": [
        "APIレート制限の仕組み",
        "データベースのインデックスとは",
        "キャッシュの種類と使い分け",
        "WebSocketとHTTPの違い",
        "マイクロサービスとモノリスの違い",
        "CDNの仕組みと効果",
    ],
    "oni": [
        "Claude Codeで副業月10万円",
        "AIツールで作業時間を90%削減",
        "無料AIで動画を自動生成",
        "ChatGPTで稼ぐ5つの方法",
        "Gemini APIで業務自動化",
        "AIで英語学習を効率化",
    ]
}

def generate_script(style: str = None) -> dict:
    """台本生成"""
    if style is None:
        style = random.choice(["fireship", "bytebyteGo", "oni"])
    
    topic = random.choice(TOPICS[style])
    prompt = STYLE_PROMPTS[style] + f"\n\nトピック: {topic}"
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY が設定されていません")
    
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30
    )
    
    if r.status_code != 200:
        raise Exception(f"Gemini API error: {r.status_code}")
    
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"```json\s*|```\s*", "", text).strip()
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        raise Exception("JSON not found in response")
    
    plan = json.loads(m.group())
    plan["topic"] = topic
    plan["selected_style"] = style
    
    # 保存
    os.makedirs("output", exist_ok=True)
    with open("output/trio_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 台本生成完了: [{style}] {plan['title']}")
    return plan

if __name__ == "__main__":
    import sys
    style = sys.argv[1] if len(sys.argv) > 1 else None
    plan = generate_script(style)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
