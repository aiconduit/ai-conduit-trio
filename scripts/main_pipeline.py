#!/usr/bin/env python3
"""
パイプライン12 トリオ メインスクリプト
Fireship / NeetCode スタイル対応版
"""
import os, sys, json, subprocess, random, shutil
from pathlib import Path

sys.path.insert(0, "scripts")
OUTPUT_DIR = Path("output")
WORK_DIR = Path("/tmp/trio_work")

def _run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⚠️ {r.stderr[:100]}")
    return r

def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # スタイル選択
    style = os.environ.get("TRIO_STYLE", "").strip()
    if not style or style == "random":
        style = random.choice(["fireship", "neetcode"])
    print(f"🎬 スタイル: {style}")

    # Step 1: 台本生成
    print("\n[1/4] 台本生成中...")
    from script_generator import generate_script
    plan = generate_script(style)
    title = plan.get("title", "AI Conduit")
    print(f"  タイトル: {title}")

    # Step 2: 音声生成
    print("\n[2/4] 音声生成中...")
    from tts_generator import generate_fireship_audio, generate_neetcode_audio
    if style == "fireship":
        audio_files, ass_texts = generate_fireship_audio(plan)
    else:
        audio_files, ass_texts = generate_neetcode_audio(plan)
    print(f"  {len(audio_files)}個の音声生成完了")

    # Step 3: 字幕生成
    print("\n[3/4] 字幕・動画生成中...")
    from subtitle_generator import generate_all_ass
    ass_files = generate_all_ass(ass_texts, audio_files, prefix=style)

    # Step 4: 動画生成
    if style == "fireship":
        from fireship_style import generate_fireship_video
        final_tmp = generate_fireship_video(plan, audio_files, ass_files)
    else:
        from neetcode_style import generate_neetcode_video
        final_tmp = generate_neetcode_video(plan, audio_files, ass_files)

    if not os.path.exists(final_tmp):
        print("❌ 動画生成失敗")
        sys.exit(1)

    # Step 5: 仕上げ（0.5秒トリム）
    print("\n[4/4] 仕上げ中...")
    safe_title = "".join(c for c in title if c.isalnum() or c in "ぁ-ん゛゜ァ-ヴー一-龯 　").strip()[:25]
    final_output = str(OUTPUT_DIR / f"trio_{style}_{safe_title}.mp4")

    # 最終エンコード
    _run(["ffmpeg", "-y", "-i", final_tmp,
          "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-pix_fmt", "yuv420p", final_output])

    # Jenny Hoyosトリム（最後0.5秒カット）
    if os.path.exists(final_output):
        dur_r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", final_output], capture_output=True, text=True)
        try:
            total_dur = float(dur_r.stdout.strip()) - 0.5
            if total_dur > 5:
                trimmed = final_output.replace(".mp4", "_t.mp4")
                _run(["ffmpeg", "-y", "-i", final_output, "-t", str(total_dur),
                      "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", trimmed])
                if os.path.exists(trimmed) and os.path.getsize(trimmed) > 100000:
                    shutil.move(trimmed, final_output)
                    print(f"  ✂️ 0.5秒トリム完了")
        except: pass

    if not os.path.exists(final_output):
        print("❌ 最終出力失敗")
        sys.exit(1)

    size = os.path.getsize(final_output) // 1024
    dur_r2 = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "csv=p=0", final_output], capture_output=True, text=True)
    dur = float(dur_r2.stdout.strip()) if dur_r2.stdout.strip() else 0

    print(f"\n✅ 完成!")
    print(f"   ファイル: {final_output}")
    print(f"   サイズ: {size}KB / 長さ: {dur:.1f}秒")
    print(f"   スタイル: {style}")
    print(f"   タイトル: {title}")

    # プラン保存
    with open("output/trio_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
