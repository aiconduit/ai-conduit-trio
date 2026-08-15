#!/usr/bin/env python3
"""
TTS音声生成 - Fireship/NeetCodeスタイル対応
スタイル別に異なるパートを音声化
"""
import os, asyncio, subprocess
from pathlib import Path
import edge_tts

VOICE = "ja-JP-KeitaNeural"
RATE = "+10%"  # Fireshipは高速
PITCH = "+0Hz"
WORK_DIR = Path("/tmp/trio_work")

async def _generate(text: str, path: str, rate: str = RATE):
    comm = edge_tts.Communicate(text, voice=VOICE, rate=rate, pitch=PITCH)
    await comm.save(path)

def probe_dur(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 3.0

def gen_audio(text: str, path: str, rate: str = RATE) -> float:
    asyncio.run(_generate(text, path, rate))
    return probe_dur(path)

def generate_fireship_audio(plan: dict) -> tuple:
    """Fireshipスタイルの音声生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    audio_files = []
    ass_texts = []

    # Hook
    hook_text = plan.get("hook", "知らないと損")
    hook_path = str(WORK_DIR / "audio_hook.mp3")
    gen_audio(hook_text, hook_path, "+15%")
    audio_files.append(hook_path)
    ass_texts.append(hook_text)
    print(f"  Hook: {hook_text}")

    # Tips
    for tip in plan.get("tips", []):
        num = tip["num"]
        text = tip["text"]
        code = tip.get("code", "")
        narration = f"ナンバー{num}。{text}"
        
        tip_path = str(WORK_DIR / f"audio_tip_{num:02d}.mp3")
        gen_audio(narration, tip_path, "+10%")
        audio_files.append(tip_path)
        ass_texts.append(narration)
        print(f"  Tip{num}: {narration}")

    # Outro
    outro_text = plan.get("outro", "フォローして最新情報を受け取れ")
    outro_path = str(WORK_DIR / "audio_outro.mp3")
    gen_audio(outro_text, outro_path, "+10%")
    audio_files.append(outro_path)
    ass_texts.append(outro_text)
    print(f"  Outro: {outro_text}")

    return audio_files, ass_texts

def generate_neetcode_audio(plan: dict) -> tuple:
    """NeetCodeスタイルの音声生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    audio_files = []
    ass_texts = []

    # Hook
    hook = plan.get("hook", "")
    title = plan.get("title", "")
    hook_narration = f"{title}。{hook}"
    hook_path = str(WORK_DIR / "audio_hook.mp3")
    gen_audio(hook_narration, hook_path, "+5%")
    audio_files.append(hook_path)
    ass_texts.append(hook_narration)
    print(f"  Hook: {hook_narration[:40]}")

    # Points
    for point in plan.get("points", []):
        num = point["num"]
        text = point["text"]
        data = point.get("data", "")
        narration = f"ポイント{num}。{text}。{data}" if data else f"ポイント{num}。{text}"
        
        p_path = str(WORK_DIR / f"audio_point_{num:02d}.mp3")
        gen_audio(narration, p_path, "+5%")
        audio_files.append(p_path)
        ass_texts.append(narration)
        print(f"  Point{num}: {narration[:40]}")

    # Opinion
    opinion = plan.get("opinion", "")
    op_path = str(WORK_DIR / "audio_opinion.mp3")
    gen_audio(f"私の意見は、{opinion}", op_path, "+5%")
    audio_files.append(op_path)
    ass_texts.append(f"私の意見は、{opinion}")
    print(f"  Opinion: {opinion[:30]}")

    # CTA
    cta = plan.get("cta", "コメントで意見を教えてください")
    cta_path = str(WORK_DIR / "audio_cta.mp3")
    gen_audio(cta, cta_path, "+5%")
    audio_files.append(cta_path)
    ass_texts.append(cta)
    print(f"  CTA: {cta[:30]}")

    return audio_files, ass_texts

if __name__ == "__main__":
    print("✅ tts_generator.py loaded")
