#!/usr/bin/env python3
"""字幕生成（シンプル版）"""
import subprocess
from pathlib import Path

WORK_DIR = Path("/tmp/trio_work")
FONT = "Noto Sans CJK JP"
SIZE = 85
MARGIN_V = 880

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,{FONT},{SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,3,2,60,60,{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ms2ass(ms):
    h=ms//3600000; m=(ms%3600000)//60000; s=(ms%60000)//1000; cs=(ms%1000)//10
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_ass(text: str, duration: float, path: str):
    total_ms = int(duration * 1000)
    # 句読点で分割
    groups = []
    cur = ""
    for c in text:
        cur += c
        if c in "。、！？!?," or len(cur) >= 12:
            if cur.strip():
                groups.append(cur.strip())
            cur = ""
    if cur.strip():
        groups.append(cur.strip())
    if not groups:
        groups = [text]
    
    dur_each = total_ms // len(groups)
    content = HEADER
    t = 0
    for i, g in enumerate(groups):
        end = t + dur_each if i < len(groups)-1 else total_ms
        content += f"Dialogue: 0,{ms2ass(t)},{ms2ass(end)},Pop,,0,0,0,,{g}\n"
        t = end
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_all_ass(texts: list, audio_files: list, prefix: str = "sub") -> list:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    ass_files = []
    for i, (text, audio) in enumerate(zip(texts, audio_files)):
        # 音声の長さ取得
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", audio], capture_output=True, text=True)
        try: dur = float(r.stdout.strip())
        except: dur = 4.0
        
        ass_path = str(WORK_DIR / f"{prefix}_{i:02d}.ass")
        generate_ass(text, dur, ass_path)
        ass_files.append(ass_path)
    return ass_files

if __name__ == "__main__":
    print("✅ subtitle_generator.py loaded")
