#!/usr/bin/env python3
"""
ONIスタイル動画生成
- テキスト強調 + 数字 + Pexels Bロール
- シンプル・即使える・具体的数字
"""
import os, json, subprocess, requests, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
WORK_DIR = Path("/tmp/trio_work")
OUTPUT_DIR = Path("output")

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

def get_pexels_video(query: str) -> str:
    """Pexels動画取得"""
    r = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": 5, "orientation": "portrait", "min_width": 720},
        timeout=15)
    if r.status_code != 200:
        return None
    videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 4]
    if not videos:
        return None
    videos = sorted(videos, key=lambda x: x.get("width", 0), reverse=True)
    v = random.choice(videos[:3])
    files = sorted([f for f in v["video_files"] if 360 <= f.get("width", 0) <= 1080],
                   key=lambda x: x["width"])
    url = files[-1]["link"] if files else v["video_files"][0]["link"]
    out = WORK_DIR / f"pexels_{v['id']}.mp4"
    if not out.exists():
        resp = requests.get(url, stream=True, timeout=30)
        with open(out, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    return str(out)

def make_oni_scene(scene: dict, idx: int, dur: float, audio_path: str, ass_path: str) -> str:
    """ONIスタイルシーン生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    scene_type = scene.get("type", "value")
    narration = scene.get("narration", "")
    point = scene.get("point", "")
    
    # 背景色設定
    bg_colors = {
        "hook": (10, 10, 10),
        "value": (15, 15, 20),
        "cta": (20, 10, 30),
    }
    bg_color = bg_colors.get(scene_type, (10, 10, 10))
    
    # Pexels Bロール取得（偶数シーン）
    broll_path = None
    if idx % 2 == 0:
        queries = ["AI technology dark", "coding computer", "business success"]
        broll_path = get_pexels_video(random.choice(queries))
    
    # 上半分: Pexels or 黒背景+テキスト
    top_path = str(WORK_DIR / f"top_{idx:02d}.mp4")
    if broll_path and os.path.exists(broll_path):
        _run(["ffmpeg", "-y", "-i", broll_path,
              "-t", str(dur), "-vf", "scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960",
              "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
              top_path])
    else:
        # テキスト画面生成
        img = Image.new("RGB", (1080, 960), bg_color)
        d = ImageDraw.Draw(img)
        
        # アクセントライン
        accent_color = (255, 200, 0) if scene_type == "hook" else (100, 200, 255)
        d.rectangle([0, 0, 8, 960], fill=accent_color)
        
        # ポイント番号（大きく）
        if point:
            try:
                font_big = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 200)
            except:
                font_big = ImageFont.load_default()
            d.text((540, 480), point, fill=accent_color, font=font_big, anchor="mm")
        
        img_path = str(WORK_DIR / f"top_img_{idx:02d}.png")
        img.save(img_path)
        _run(["ffmpeg", "-y", "-loop", "1", "-i", img_path,
              "-t", str(dur), "-r", "30", "-vf", "scale=1080:960",
              "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
              top_path])
    
    # キャラクター下半分（黒背景）
    char_path = str(WORK_DIR / f"char_{idx:02d}.mp4")
    bg_img = Image.new("RGB", (1080, 960), (5, 5, 10))
    d = ImageDraw.Draw(bg_img)
    # シンプルなブランドカラーライン
    d.rectangle([0, 0, 1080, 4], fill=(100, 50, 200))
    bg_path = str(WORK_DIR / f"bg_img_{idx:02d}.png")
    bg_img.save(bg_path)
    _run(["ffmpeg", "-y", "-loop", "1", "-i", bg_path,
          "-t", str(dur), "-r", "30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
          char_path])
    
    # 上下結合
    combined = str(WORK_DIR / f"combined_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", top_path, "-i", char_path,
          "-filter_complex", "[0:v][1:v]vstack=inputs=2[v]",
          "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-pix_fmt", "yuv420p", "-an", combined])
    
    # 字幕焼き込み
    scene_out = str(WORK_DIR / f"scene_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", combined, "-i", audio_path,
          "-vf", f"ass={ass_path}",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-shortest",
          "-pix_fmt", "yuv420p", scene_out])
    
    return scene_out

if __name__ == "__main__":
    print("✅ oni_style.py loaded")
