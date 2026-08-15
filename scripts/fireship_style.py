#!/usr/bin/env python3
"""
Fireshipスタイル動画生成
- コードハイライト画像 + 高速カット + ダーク背景
- pygmentsでコードを美しく表示
"""
import os, json, subprocess, requests, random, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = Path("/tmp/trio_work")

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

def make_code_image(code: str, width=1080, height=960) -> str:
    """Pygmentsでコードハイライト画像生成"""
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.formatters import ImageFormatter
        from pygments.styles import get_style_by_name
        
        try:
            lexer = guess_lexer(code)
        except:
            lexer = get_lexer_by_name("python")
        
        formatter = ImageFormatter(
            style="monokai",
            font_size=28,
            line_numbers=False,
            image_pad=20,
        )
        result = highlight(code, lexer, formatter)
        
        # 一時ファイルに保存
        tmp_path = str(WORK_DIR / "code_tmp.png")
        with open(tmp_path, "wb") as f:
            f.write(result)
        
        # 1080x960にリサイズ・パディング
        code_img = Image.open(tmp_path)
        bg = Image.new("RGB", (width, height), (30, 30, 30))
        # 中央配置
        ratio = min((width-40)/code_img.width, (height-40)/code_img.height)
        new_w = int(code_img.width * ratio)
        new_h = int(code_img.height * ratio)
        code_img = code_img.resize((new_w, new_h), Image.LANCZOS)
        x = (width - new_w) // 2
        y = (height - new_h) // 2
        bg.paste(code_img, (x, y))
        
        out_path = str(WORK_DIR / "code_highlight.png")
        bg.save(out_path)
        return out_path
        
    except ImportError:
        # pygments未インストールの場合フォールバック
        return make_code_image_fallback(code, width, height)

def make_code_image_fallback(code: str, width=1080, height=960) -> str:
    """pygments未インストール時のフォールバック（Pillow使用）"""
    img = Image.new("RGB", (width, height), (30, 30, 30))
    d = ImageDraw.Draw(img)
    
    # ヘッダー
    d.rectangle([0, 0, width, 50], fill=(45, 45, 45))
    d.ellipse([15, 15, 35, 35], fill=(255, 95, 87))
    d.ellipse([45, 15, 65, 35], fill=(255, 189, 46))
    d.ellipse([75, 15, 95, 35], fill=(39, 201, 63))
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 26)
    except:
        font = ImageFont.load_default()
    
    # コード表示（シンタックスカラー簡易版）
    y = 70
    for line in code.split('\n')[:25]:
        color = (255, 255, 255)
        if line.strip().startswith('#'):
            color = (106, 153, 85)
        elif any(kw in line for kw in ['def ', 'class ', 'import ', 'from ', 'return']):
            color = (197, 134, 192)
        elif line.strip().startswith('"') or line.strip().startswith("'"):
            color = (206, 145, 120)
        d.text((20, y), line[:55], fill=color, font=font)
        y += 36
        if y > height - 20:
            break
    
    out_path = str(WORK_DIR / "code_highlight.png")
    img.save(out_path)
    return out_path

def make_fireship_scene(scene: dict, idx: int, dur: float, audio_path: str, ass_path: str) -> str:
    """Fireshipスタイルシーン生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    scene_type = scene.get("type", "code")
    code = scene.get("code", "")
    
    # 上半分: コードハイライトor黒背景
    top_path = str(WORK_DIR / f"top_{idx:02d}.mp4")
    
    if code and len(code) > 5:
        # コードハイライト画像
        code_img_path = make_code_image(code)
        _run(["ffmpeg", "-y", "-loop", "1", "-i", code_img_path,
              "-t", str(dur), "-r", "30",
              "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
              top_path])
    else:
        # ダーク背景 + Fireshipsタイルテキスト
        img = Image.new("RGB", (1080, 960), (15, 15, 20))
        d = ImageDraw.Draw(img)
        # オレンジアクセント
        d.rectangle([0, 0, 1080, 6], fill=(255, 100, 0))
        d.rectangle([0, 954, 1080, 960], fill=(255, 100, 0))
        
        # タイプ別アイコン
        type_icons = {"hook": "⚡", "result": "✅", "cta": "🔥"}
        icon = type_icons.get(scene_type, "")
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 80)
        except:
            font = ImageFont.load_default()
        
        if icon:
            d.text((540, 480), icon, font=font, anchor="mm")
        
        img_path = str(WORK_DIR / f"hook_img_{idx:02d}.png")
        img.save(img_path)
        _run(["ffmpeg", "-y", "-loop", "1", "-i", img_path,
              "-t", str(dur), "-r", "30",
              "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
              top_path])
    
    # 下半分: ダーク背景
    char_path = str(WORK_DIR / f"char_{idx:02d}.mp4")
    img2 = Image.new("RGB", (1080, 960), (10, 10, 15))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([0, 0, 1080, 4], fill=(255, 100, 0))
    char_img_path = str(WORK_DIR / f"char_img_{idx:02d}.png")
    img2.save(char_img_path)
    _run(["ffmpeg", "-y", "-loop", "1", "-i", char_img_path,
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
          "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", scene_out])
    
    return scene_out

if __name__ == "__main__":
    print("✅ fireship_style.py loaded")
