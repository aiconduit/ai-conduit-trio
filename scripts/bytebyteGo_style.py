#!/usr/bin/env python3
"""
ByteByteGoスタイル動画生成
- 図解アニメーション + ステップバイステップ
- PIL でシンプルな図解を描画
"""
import os, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = Path("/tmp/trio_work")

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

COLORS = {
    "bg": (8, 12, 24),
    "box": (30, 40, 80),
    "box_highlight": (50, 100, 200),
    "arrow": (100, 180, 255),
    "text": (220, 230, 255),
    "accent": (80, 160, 255),
    "success": (60, 200, 120),
    "warning": (255, 180, 50),
}

def get_font(size=32):
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except: pass
    return ImageFont.load_default()

def draw_rounded_box(d, x1, y1, x2, y2, color, radius=20):
    d.rectangle([x1+radius, y1, x2-radius, y2], fill=color)
    d.rectangle([x1, y1+radius, x2, y2-radius], fill=color)
    d.ellipse([x1, y1, x1+2*radius, y1+2*radius], fill=color)
    d.ellipse([x2-2*radius, y1, x2, y1+2*radius], fill=color)
    d.ellipse([x1, y2-2*radius, x1+2*radius, y2], fill=color)
    d.ellipse([x2-2*radius, y2-2*radius, x2, y2], fill=color)

def draw_arrow(d, x1, y1, x2, y2, color=(100, 180, 255), width=4):
    d.line([x1, y1, x2, y2], fill=color, width=width)
    # 矢印の先端
    import math
    angle = math.atan2(y2-y1, x2-x1)
    size = 20
    d.polygon([
        (x2, y2),
        (x2 - size*math.cos(angle-0.5), y2 - size*math.sin(angle-0.5)),
        (x2 - size*math.cos(angle+0.5), y2 - size*math.sin(angle+0.5)),
    ], fill=color)

def make_diagram_image(diagram_desc: str, step_num: int, width=1080, height=960) -> str:
    """図解画像生成"""
    img = Image.new("RGB", (width, height), COLORS["bg"])
    d = ImageDraw.Draw(img)
    
    # グリッドライン（薄い）
    for x in range(0, width, 60):
        d.line([x, 0, x, height], fill=(15, 20, 35), width=1)
    for y in range(0, height, 60):
        d.line([0, y, width, y], fill=(15, 20, 35), width=1)
    
    font_title = get_font(36)
    font_body = get_font(28)
    font_small = get_font(22)
    
    # ステップ番号インジケーター
    step_x = 60
    for i in range(5):
        color = COLORS["accent"] if i == step_num else (40, 50, 80)
        d.ellipse([step_x + i*180 - 20, 30, step_x + i*180 + 20, 70], fill=color)
        d.text((step_x + i*180, 50), str(i+1), fill=COLORS["text"], font=font_small, anchor="mm")
    
    # メインコンテンツ（diagram_descをパース）
    lines = diagram_desc.split("→") if "→" in diagram_desc else [diagram_desc]
    
    if len(lines) >= 2:
        # フローチャートスタイル
        y_start = 150
        box_w, box_h = 280, 80
        spacing = 340
        
        for i, line in enumerate(lines[:3]):
            x = 100 + i * spacing
            y = y_start + (i % 2) * 120
            
            color = COLORS["box_highlight"] if i == len(lines)-1 else COLORS["box"]
            draw_rounded_box(d, x, y, x+box_w, y+box_h, color)
            
            text = line.strip()[:15]
            d.text((x + box_w//2, y + box_h//2), text, 
                   fill=COLORS["text"], font=font_body, anchor="mm")
            
            if i < len(lines) - 1:
                draw_arrow(d, x+box_w, y+box_h//2, x+spacing, y_start+(((i+1)%2)*120)+box_h//2)
    else:
        # シンプルな説明ボックス
        draw_rounded_box(d, 100, 200, 980, 700, COLORS["box"])
        
        # テキストを複数行に分割
        words = diagram_desc
        wrapped = []
        line = ""
        for char in words:
            line += char
            if len(line) >= 20:
                wrapped.append(line)
                line = ""
        if line:
            wrapped.append(line)
        
        y = 400 - len(wrapped)*30
        for wrap_line in wrapped[:6]:
            d.text((540, y), wrap_line, fill=COLORS["text"], font=font_title, anchor="mm")
            y += 70
    
    # BottomBar
    d.rectangle([0, 920, width, 960], fill=COLORS["accent"])
    d.text((540, 940), "ByteByteGo Style", fill=COLORS["bg"], font=font_small, anchor="mm")
    
    out_path = str(WORK_DIR / f"diagram_{step_num:02d}.png")
    img.save(out_path)
    return out_path

def make_bytebyteGo_scene(scene: dict, idx: int, dur: float, audio_path: str, ass_path: str) -> str:
    """ByteByteGoスタイルシーン生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    diagram = scene.get("diagram", "")
    
    # 図解画像生成
    diagram_img = make_diagram_image(diagram, idx)
    
    top_path = str(WORK_DIR / f"top_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-loop", "1", "-i", diagram_img,
          "-t", str(dur), "-r", "30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
          top_path])
    
    # 下半分
    img2 = Image.new("RGB", (1080, 960), COLORS["bg"])
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([0, 0, 1080, 4], fill=COLORS["accent"])
    char_img_path = str(WORK_DIR / f"char_img_{idx:02d}.png")
    img2.save(char_img_path)
    
    char_path = str(WORK_DIR / f"char_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-loop", "1", "-i", char_img_path,
          "-t", str(dur), "-r", "30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
          char_path])
    
    combined = str(WORK_DIR / f"combined_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", top_path, "-i", char_path,
          "-filter_complex", "[0:v][1:v]vstack=inputs=2[v]",
          "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-pix_fmt", "yuv420p", "-an", combined])
    
    scene_out = str(WORK_DIR / f"scene_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", combined, "-i", audio_path,
          "-vf", f"ass={ass_path}",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", scene_out])
    
    return scene_out

if __name__ == "__main__":
    print("✅ bytebyteGo_style.py loaded")
