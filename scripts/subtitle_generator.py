#!/usr/bin/env python3
"""
ASS字幕生成（シンプル版）
"""
import os
from pathlib import Path

WORK_DIR = Path("/tmp/trio_work")
FONT_NAME = "Noto Sans CJK JP"
FONT_SIZE = 90
MARGIN_V = 850

ASS_HEADER = f"""\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,{FONT_NAME},{FONT_SIZE},&H00FFFFFF,&H0000E5FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,6,3,2,80,80,{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ms_to_ass(ms: int) -> str:
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    cs = (ms % 1000) // 10
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_ass(narration: str, duration: float, output_path: str):
    """シンプルな字幕生成（全体を2-3グループに分割）"""
    chars = list(narration)
    total_ms = int(duration * 1000)
    
    # 句読点で分割
    groups = []
    current = ""
    for c in chars:
        current += c
        if c in "。、！？!?,." or len(current) >= 12:
            if current.strip():
                groups.append(current.strip())
            current = ""
    if current.strip():
        groups.append(current.strip())
    
    if not groups:
        groups = [narration]
    
    # 各グループの時間を均等配分
    dur_per_group = total_ms // len(groups)
    
    ass_content = ASS_HEADER
    t = 0
    for i, group in enumerate(groups):
        start = t
        end = t + dur_per_group if i < len(groups)-1 else total_ms
        ass_content += f"Dialogue: 0,{ms_to_ass(start)},{ms_to_ass(end)},Pop,,0,0,0,,{group}\n"
        t = end
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

if __name__ == "__main__":
    generate_ass("テスト字幕です。これはテストです。", 5.0, "/tmp/test_sub.ass")
    print("✅ subtitle_generator.py テスト完了")
