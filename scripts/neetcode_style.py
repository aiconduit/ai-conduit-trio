#!/usr/bin/env python3
"""
NeetCodeスタイル動画生成
参考: 「Did AI Really Skyrocket the U.S. Economy?」→3万再生
- テキスト中心・問いかけ形式
- データ・数字を強調
- ミニマルデザイン
"""
import os, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = Path("/tmp/trio_work")
W, H = 1080, 1920

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

def get_font(size):
    paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

PALETTE = {
    "bg": (8, 10, 18),
    "card": (18, 22, 35),
    "accent": (59, 130, 246),   # NeetCode blue
    "text": (240, 245, 255),
    "sub": (140, 160, 200),
    "highlight": (250, 204, 21), # yellow highlight
    "positive": (34, 197, 94),
    "negative": (239, 68, 68),
}

def draw_card(d, x1, y1, x2, y2, color=None, radius=24):
    c = color or PALETTE["card"]
    d.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=c)

def make_hook_frame(hook: str, title: str) -> str:
    """Hook画面 - 大きな問いかけ"""
    img = Image.new("RGB", (W, H), PALETTE["bg"])
    d = ImageDraw.Draw(img)

    font_q = get_font(85)
    font_sub = get_font(55)
    font_tiny = get_font(40)

    # 左サイドバー
    d.rectangle([0, 0, 6, H], fill=PALETTE["accent"])

    # 「?」大きく
    d.text((W//2, 600), "?", fill=PALETTE["accent"], font=get_font(500), anchor="mm",
           stroke_width=2, stroke_fill=(30, 60, 120))

    # タイトル
    words = title
    lines = []
    line = ""
    for c2 in words:
        line += c2
        if len(line) >= 16:
            lines.append(line)
            line = ""
    if line:
        lines.append(line)

    y = 1100
    for ln in lines[:3]:
        d.text((W//2, y), ln, fill=PALETTE["text"], font=font_q, anchor="mm",
               stroke_width=2, stroke_fill=(0,0,0))
        y += 110

    # サブテキスト
    d.text((W//2, H - 200), hook, fill=PALETTE["sub"], font=font_sub, anchor="mm")

    # チャンネル名風
    d.text((W//2, H - 100), "AI Conduit", fill=PALETTE["accent"], font=font_tiny, anchor="mm")

    path = str(WORK_DIR / "nc_hook.png")
    img.save(path)
    return path

def make_point_frame(num: int, text: str, data: str, total: int) -> str:
    """分析ポイント画面"""
    img = Image.new("RGB", (W, H), PALETTE["bg"])
    d = ImageDraw.Draw(img)

    font_num = get_font(160)
    font_text = get_font(70)
    font_data = get_font(55)

    # 進捗インジケーター（上部）
    seg_w = W // total
    for i in range(total):
        color = PALETTE["accent"] if i < num else PALETTE["card"]
        d.rectangle([i * seg_w + 4, 0, (i+1) * seg_w - 4, 12], fill=color)

    # 左サイドバー
    d.rectangle([0, 0, 6, H], fill=PALETTE["accent"])

    # ポイント番号
    d.text((120, H//2 - 300), f"{num}", fill=PALETTE["accent"],
           font=font_num, anchor="lm", stroke_width=2, stroke_fill=(20, 50, 120))

    # メインテキスト
    chars = list(text)
    lines = []
    line = ""
    for c2 in chars:
        line += c2
        if len(line) >= 14:
            lines.append(line)
            line = ""
    if line:
        lines.append(line)

    y = H//2 - 50
    for ln in lines[:3]:
        d.text((W//2, y), ln, fill=PALETTE["text"], font=font_text, anchor="mm",
               stroke_width=2, stroke_fill=(0,0,0))
        y += 90

    # データカード
    if data:
        draw_card(d, 60, H//2 + 250, W-60, H//2 + 420)
        d.text((W//2, H//2 + 335), data[:28], fill=PALETTE["highlight"],
               font=font_data, anchor="mm")

    path = str(WORK_DIR / f"nc_point_{num}.png")
    img.save(path)
    return path

def make_opinion_frame(opinion: str) -> str:
    """個人意見画面"""
    img = Image.new("RGB", (W, H), PALETTE["bg"])
    d = ImageDraw.Draw(img)

    font_label = get_font(55)
    font_text = get_font(75)

    d.rectangle([0, 0, 6, H], fill=PALETTE["positive"])
    d.text((W//2, 700), "私の意見", fill=PALETTE["sub"], font=font_label, anchor="mm")

    # 引用符
    d.text((120, 900), "「", fill=PALETTE["accent"], font=get_font(180), anchor="lm")
    d.text((W-120, 1300), "」", fill=PALETTE["accent"], font=get_font(180), anchor="rm")

    chars = list(opinion)
    lines = []
    line = ""
    for c2 in chars:
        line += c2
        if len(line) >= 12:
            lines.append(line)
            line = ""
    if line:
        lines.append(line)

    y = H//2
    for ln in lines[:4]:
        d.text((W//2, y), ln, fill=PALETTE["text"], font=font_text, anchor="mm",
               stroke_width=2, stroke_fill=(0,0,0))
        y += 100

    path = str(WORK_DIR / "nc_opinion.png")
    img.save(path)
    return path

def make_cta_frame(cta: str) -> str:
    """CTA画面"""
    img = Image.new("RGB", (W, H), PALETTE["bg"])
    d = ImageDraw.Draw(img)

    font_big = get_font(80)
    font_mid = get_font(60)

    d.rectangle([0, 0, 6, H], fill=PALETTE["accent"])
    d.text((W//2, H//2 - 100), "💬", font=get_font(300), anchor="mm")
    d.text((W//2, H//2 + 200), cta, fill=PALETTE["text"],
           font=font_mid, anchor="mm", stroke_width=2, stroke_fill=(0,0,0))
    d.text((W//2, H-120), "AI Conduit", fill=PALETTE["accent"], font=font_mid, anchor="mm")

    path = str(WORK_DIR / "nc_cta.png")
    img.save(path)
    return path

def generate_neetcode_video(plan: dict, audio_files: list, ass_files: list) -> str:
    """NeetCodeスタイル動画生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    title = plan.get("title", "AIの真実")
    hook = plan.get("hook", "本当のところどうなのか")
    points = plan.get("points", [])
    opinion = plan.get("opinion", "これは重要な問題だ")
    cta = plan.get("cta", "コメントで意見を教えてください")
    total = len(points)

    frames = [
        ("hook", make_hook_frame(hook, title)),
        *[(f"point_{p['num']}", make_point_frame(p["num"], p["text"], p.get("data",""), total))
          for p in points],
        ("opinion", make_opinion_frame(opinion)),
        ("cta", make_cta_frame(cta)),
    ]

    scene_videos = []
    for i, (label, img_path) in enumerate(frames):
        if i >= len(audio_files):
            break
        audio = audio_files[i]
        ass = ass_files[i] if i < len(ass_files) else None

        out = str(WORK_DIR / f"nc_scene_{i:02d}.mp4")
        vf = f"ass={ass},scale={W}:{H}" if ass else f"scale={W}:{H}"
        _run(["ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", audio,
              "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "20",
              "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", out])
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            scene_videos.append(out)

    if not scene_videos:
        raise Exception("シーン生成失敗")

    concat = str(WORK_DIR / "nc_concat.txt")
    with open(concat, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{sv}'\n")

    output = str(WORK_DIR / "neetcode_final.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-pix_fmt", "yuv420p", output])
    return output

if __name__ == "__main__":
    print("✅ neetcode_style.py loaded")
