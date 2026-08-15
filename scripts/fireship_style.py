#!/usr/bin/env python3
"""
Fireshipスタイル動画生成
参考: 「5 life-changing Linux tips」→172万再生
- ダーク背景
- コードをそのまま大きく表示
- 各Tipをカード形式で順番に表示
- 高速カット感
"""
import os, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = Path("/tmp/trio_work")
W, H = 1080, 1920

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

def get_font(size, bold=True):
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except: pass
    return ImageFont.load_default()

def make_hook_frame(hook_text: str, total_tips: int) -> str:
    """Hook画面 - 数字を大きく表示"""
    img = Image.new("RGB", (W, H), (10, 10, 15))
    d = ImageDraw.Draw(img)
    
    # グラデーション風背景ライン
    for i in range(0, H, 4):
        alpha = int(20 * (1 - i/H))
        d.line([(0, i), (W, i)], fill=(0, 100, 255, alpha), width=1)
    
    # 上部アクセントライン（Fireshipオレンジ）
    d.rectangle([0, 0, W, 8], fill=(255, 69, 0))
    
    # 数字を超大きく（Fireshipスタイル）
    font_huge = get_font(400)
    font_mid = get_font(80)
    font_small = get_font(55)
    
    # 数字
    num_text = str(total_tips)
    d.text((W//2, H//2 - 150), num_text, fill=(255, 69, 0), font=font_huge, anchor="mm",
           stroke_width=4, stroke_fill=(200, 40, 0))
    
    # テキスト
    d.text((W//2, H//2 + 200), hook_text, fill=(255, 255, 255), font=font_small, anchor="mm",
           stroke_width=2, stroke_fill=(0, 0, 0))
    
    # 下部ブランドライン
    d.rectangle([0, H-8, W, H], fill=(255, 69, 0))
    
    path = str(WORK_DIR / "hook_frame.png")
    img.save(path)
    return path

def make_tip_frame(num: int, text: str, code: str, total: int) -> str:
    """各Tipのカード画面"""
    img = Image.new("RGB", (W, H), (10, 10, 15))
    d = ImageDraw.Draw(img)
    
    # 背景グリッド（薄い）
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=(20, 25, 35), width=1)
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=(20, 25, 35), width=1)
    
    font_num = get_font(180)
    font_text = get_font(65)
    font_code = get_font(48)
    
    # 進捗バー
    progress = num / total
    d.rectangle([0, 0, int(W * progress), 10], fill=(255, 69, 0))
    
    # Tip番号（左上）
    d.text((80, 120), f"#{num}", fill=(255, 69, 0), font=font_num, anchor="lm",
           stroke_width=3, stroke_fill=(180, 40, 0))
    
    # 説明テキスト
    d.text((W//2, H//2 - 80), text, fill=(255, 255, 255), font=font_text, anchor="mm",
           stroke_width=2, stroke_fill=(0, 0, 0))
    
    # コードブロック（ターミナル風）
    if code:
        # コードボックス背景
        pad = 40
        code_y = H//2 + 80
        code_lines = code.split('\n')
        box_h = len(code_lines) * 65 + pad * 2
        d.rounded_rectangle([pad, code_y - pad, W - pad, code_y + box_h], 
                            radius=20, fill=(25, 30, 45))
        d.rounded_rectangle([pad, code_y - pad, W - pad, code_y + box_h], 
                            radius=20, outline=(60, 80, 120), width=2)
        
        # ターミナルドット
        d.ellipse([pad+20, code_y-pad+20, pad+40, code_y-pad+40], fill=(255, 95, 87))
        d.ellipse([pad+55, code_y-pad+20, pad+75, code_y-pad+40], fill=(255, 189, 46))
        d.ellipse([pad+90, code_y-pad+20, pad+110, code_y-pad+40], fill=(39, 201, 63))
        
        # コードテキスト
        for i, line in enumerate(code_lines[:6]):
            # キーワードカラー（簡易）
            color = (100, 200, 255)
            if line.startswith('#') or line.startswith('//'):
                color = (100, 160, 100)
            elif any(kw in line for kw in ['def ', 'class ', 'import ', 'const ', 'let ']):
                color = (200, 120, 255)
            d.text((pad + 20, code_y + i * 65), line[:30], 
                   fill=color, font=font_code)
    
    # 下部ライン
    d.rectangle([0, H-8, W, H], fill=(255, 69, 0))
    
    path = str(WORK_DIR / f"tip_{num:02d}_frame.png")
    img.save(path)
    return path

def make_outro_frame(text: str) -> str:
    """CTA画面"""
    img = Image.new("RGB", (W, H), (10, 10, 15))
    d = ImageDraw.Draw(img)
    
    font_big = get_font(90)
    font_small = get_font(60)
    
    d.rectangle([0, 0, W, 8], fill=(255, 69, 0))
    
    # 炎アイコン風テキスト
    d.text((W//2, H//2 - 100), "🔥", font=get_font(200), anchor="mm")
    d.text((W//2, H//2 + 150), text, fill=(255, 255, 255), font=font_small, anchor="mm",
           stroke_width=2, stroke_fill=(0, 0, 0))
    
    d.rectangle([0, H-8, W, H], fill=(255, 69, 0))
    
    path = str(WORK_DIR / "outro_frame.png")
    img.save(path)
    return path

def generate_fireship_video(plan: dict, audio_files: list, ass_files: list) -> str:
    """Fireshipスタイル動画生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    tips = plan.get("tips", [])
    hook = plan.get("hook", "知らないと損")
    outro = plan.get("outro", "フォローして最新情報を受け取れ")
    total_tips = len(tips)
    
    # 各セクションの動画を生成
    scene_videos = []
    
    # Hook画面（audio_files[0]があれば使用）
    if audio_files:
        hook_img = make_hook_frame(hook, total_tips)
        hook_audio = audio_files[0]
        hook_ass = ass_files[0] if ass_files else None
        
        # 音声の長さを確認
        dur_r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", hook_audio], capture_output=True, text=True)
        hook_dur = float(dur_r.stdout.strip()) if dur_r.stdout.strip() else 3.0
        
        hook_video = str(WORK_DIR / "hook_scene.mp4")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", hook_img,
               "-i", hook_audio, "-vf"]
        if hook_ass:
            cmd.append(f"ass={hook_ass},scale={W}:{H}")
        else:
            cmd.append(f"scale={W}:{H}")
        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", hook_video]
        _run(cmd)
        if os.path.exists(hook_video) and os.path.getsize(hook_video) > 10000:
            scene_videos.append(hook_video)
    
    # Tips画面
    for i, tip in enumerate(tips):
        if i + 1 >= len(audio_files):
            break
        
        tip_img = make_tip_frame(tip["num"], tip["text"], tip.get("code", ""), total_tips)
        tip_audio = audio_files[i + 1]
        tip_ass = ass_files[i + 1] if i + 1 < len(ass_files) else None
        
        dur_r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", tip_audio], capture_output=True, text=True)
        tip_dur = float(dur_r.stdout.strip()) if dur_r.stdout.strip() else 5.0
        
        tip_video = str(WORK_DIR / f"tip_{i:02d}_scene.mp4")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", tip_img,
               "-i", tip_audio, "-vf"]
        if tip_ass:
            cmd.append(f"ass={tip_ass},scale={W}:{H}")
        else:
            cmd.append(f"scale={W}:{H}")
        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", tip_video]
        _run(cmd)
        if os.path.exists(tip_video) and os.path.getsize(tip_video) > 10000:
            scene_videos.append(tip_video)
    
    # Outro
    if len(audio_files) > len(tips) + 1:
        outro_img = make_outro_frame(outro)
        outro_audio = audio_files[len(tips) + 1]
        outro_ass = ass_files[len(tips) + 1] if len(tips) + 1 < len(ass_files) else None
        
        outro_video = str(WORK_DIR / "outro_scene.mp4")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", outro_img,
               "-i", outro_audio, "-vf"]
        if outro_ass:
            cmd.append(f"ass={outro_ass},scale={W}:{H}")
        else:
            cmd.append(f"scale={W}:{H}")
        cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", outro_video]
        _run(cmd)
        if os.path.exists(outro_video) and os.path.getsize(outro_video) > 10000:
            scene_videos.append(outro_video)
    
    if not scene_videos:
        raise Exception("シーン動画が生成されませんでした")
    
    # 全シーン結合
    concat_file = str(WORK_DIR / "fireship_concat.txt")
    with open(concat_file, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{sv}'\n")
    
    output = str(WORK_DIR / "fireship_final.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-pix_fmt", "yuv420p", output])
    
    return output

if __name__ == "__main__":
    print("✅ fireship_style.py loaded")
