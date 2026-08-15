#!/usr/bin/env python3
"""
台本生成 - Fireship/NeetCodeスタイル対応
実際のデータに基づいたスタイル:
- Fireship: 45秒・コードリスト・「N life-changing X」
- NeetCode: 60秒・AIニュース意見・「Did X really Y?」
"""
import os, json, re, random, requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

STYLE_PROMPTS = {
    "fireship": """あなたはFireshipスタイルのYouTube Shorts台本ライターです。
参考: 「5 life-changing Linux tips」→172万再生、「This rubber duck can debug your code」→47万再生

【スタイルの特徴】
- 45秒以下、リスト形式（3〜5個）
- コードやコマンドをそのまま表示
- 皮肉・ユーモアあり
- タイトルパターン: 「N つの[形容詞] [技術名] テクニック」「この[技術]で[結果]できる」

【構成（完全に守ること）】
- Hook（0-3秒）: 数字から始まる一文「5つの〇〇を知らないと損です」
- Tips（3-40秒）: 各Tip 1〜2文 + 実際のコード/コマンド例
- Outro（40-45秒）: 「フォローして最新情報を受け取れ」

JSONのみ出力（日本語）:
{
  "title": "5つの[技術名]テクニック（30文字以内）",
  "style": "fireship",
  "tips": [
    {"num": 1, "text": "説明(15文字以内)", "code": "実際のコマンド/コード"},
    {"num": 2, "text": "説明(15文字以内)", "code": "実際のコマンド/コード"},
    {"num": 3, "text": "説明(15文字以内)", "code": "実際のコマンド/コード"},
    {"num": 4, "text": "説明(15文字以内)", "code": "実際のコマンド/コード"},
    {"num": 5, "text": "説明(15文字以内)", "code": "実際のコマンド/コード"}
  ],
  "hook": "フック一文(20文字以内)",
  "outro": "フォローして最新情報を受け取れ"
}""",

    "neetcode": """あなたはNeetCodeスタイルのYouTube Shorts台本ライターです。
参考: 「Did AI Really Skyrocket the U.S. Economy?」→3万再生、「Why you need more than one adversarial code reviewer」→1.5万再生

【スタイルの特徴】
- 44〜70秒、AIニュース・エンジニアの意見
- 問いかけ・批判的視点
- タイトルパターン: 「AIは本当に〇〇したのか？」「なぜ〇〇が必要なのか」
- データ・具体的数字を使う

【構成（完全に守ること）】
- Hook（0-5秒）: 問いかけ or 驚きの事実「AIが〇〇したと言われているが...」
- Analysis（5-55秒）: 3つの視点で分析（各15秒）
- Opinion（55-65秒）: 個人的意見「私はこう思う」
- CTA（65-70秒）: 「コメントで意見を教えて」

JSONのみ出力（日本語）:
{
  "title": "AIは本当に〇〇したのか？（30文字以内）",
  "style": "neetcode",
  "hook": "フック一文(20文字以内)",
  "points": [
    {"num": 1, "text": "視点1(25文字以内)", "data": "具体的数字/事実"},
    {"num": 2, "text": "視点2(25文字以内)", "data": "具体的数字/事実"},
    {"num": 3, "text": "視点3(25文字以内)", "data": "具体的数字/事実"}
  ],
  "opinion": "個人的意見(30文字以内)",
  "cta": "コメントで意見を教えてください"
}"""
}

TOPICS = {
    "fireship": [
        "Git コマンド",
        "Claude Code ショートカット",
        "Python one-liner",
        "bash スクリプト",
        "VSCode 裏技",
        "Docker コマンド",
        "ffmpeg テクニック",
        "curl コマンド",
        "jq JSONパース",
        "sed/awk テクニック",
    ],
    "neetcode": [
        "AIはエンジニアの仕事を奪うのか",
        "Gemini 2.5 Proは本当にClaude Codeより優れているのか",
        "AIコーディングツールで生産性は本当に上がったのか",
        "量子コンピュータはAIを終わらせるのか",
        "オープンソースLLMはGPT-4を超えたのか",
        "Claude Codeで副業は本当に稼げるのか",
        "AIは本当にコードレビューができるのか",
        "2.8兆パラメータのAIは何ができるのか",
    ]
}

def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY未設定")
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30
    )
    if r.status_code != 200:
        raise Exception(f"Gemini error: {r.status_code}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def generate_script(style: str = None) -> dict:
    if style is None or style == "":
        style = random.choice(["fireship", "neetcode"])
    
    topic = random.choice(TOPICS[style])
    prompt = STYLE_PROMPTS[style] + f"\n\nトピック: {topic}"
    
    text = call_gemini(prompt)
    text = re.sub(r"```json\s*|```\s*", "", text).strip()
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        raise Exception("JSONが見つかりません")
    
    plan = json.loads(m.group())
    plan["topic"] = topic
    plan["selected_style"] = style
    
    os.makedirs("output", exist_ok=True)
    with open("output/trio_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 台本生成: [{style}] {plan.get('title','?')}")
    print(f"   トピック: {topic}")
    return plan

if __name__ == "__main__":
    import sys
    style = sys.argv[1] if len(sys.argv) > 1 else None
    plan = generate_script(style)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
