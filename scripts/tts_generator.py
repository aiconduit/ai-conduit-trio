#!/usr/bin/env python3
"""
TTS音声生成 + タイムスタンプ取得
edge-ttsを使用（KeitaNeural）
"""
import os, asyncio, json, re
from pathlib import Path
import edge_tts

VOICE = "ja-JP-KeitaNeural"
RATE = "+8%"
PITCH = "+0Hz"
WORK_DIR = Path("/tmp/trio_work")

async def _generate(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(output_path)

def generate_speech(text: str, output_path: str) -> float:
    """音声生成して長さを返す"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    asyncio.run(_generate(text, output_path))
    
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", output_path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 4.0

def generate_all_audio(plan: dict) -> list:
    """全シーンの音声生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    scenes = plan.get("scenes", [])
    audio_info = []
    
    for scene in scenes:
        idx = scene["id"]
        narration = scene.get("narration", "")
        if not narration:
            continue
        
        audio_path = str(WORK_DIR / f"audio_{idx:02d}.mp3")
        dur = generate_speech(narration, audio_path)
        audio_info.append({
            "id": idx,
            "narration": narration,
            "audio_path": audio_path,
            "duration": dur
        })
        print(f"  Scene {idx}: {dur:.1f}秒 '{narration[:30]}'")
    
    return audio_info

if __name__ == "__main__":
    test = {"scenes": [{"id": 0, "narration": "テストナレーションです"}]}
    result = generate_all_audio(test)
    print(json.dumps(result, ensure_ascii=False, indent=2))
