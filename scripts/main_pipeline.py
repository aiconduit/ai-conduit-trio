#!/usr/bin/env python3
"""
パイプライン12 トリオ メインスクリプト
Fireship / ByteByteGo / ONI スタイルを自動選択して動画生成
"""
import os, sys, json, subprocess, random, shutil
from pathlib import Path

WORK_DIR = Path("/tmp/trio_work")
OUTPUT_DIR = Path("output")

def _run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⚠️ cmd error: {r.stderr[:200]}")
    return r

def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # スタイル選択
    style = os.environ.get("TRIO_STYLE", None)
    if not style:
        style = random.choice(["fireship", "bytebyteGo", "oni"])
    print(f"🎬 スタイル: {style}")
    
    # Step 1: 台本生成
    print("\n[1/5] 台本生成中...")
    sys.path.insert(0, "scripts")
    from script_generator import generate_script
    plan = generate_script(style)
    title = plan.get("title", "AI Conduit Trio")
    print(f"  タイトル: {title}")
    
    # Step 2: 音声生成
    print("\n[2/5] 音声生成中...")
    from tts_generator import generate_all_audio
    audio_info = generate_all_audio(plan)
    print(f"  {len(audio_info)}シーンの音声生成完了")
    
    # Step 3: 字幕生成＋シーン動画生成
    print("\n[3/5] 動画シーン生成中...")
    from subtitle_generator import generate_ass
    
    if style == "fireship":
        from fireship_style import make_fireship_scene as make_scene
    elif style == "bytebyteGo":
        from bytebyteGo_style import make_bytebyteGo_scene as make_scene
    else:
        from oni_style import make_oni_scene as make_scene
    
    scene_files = []
    scenes = plan.get("scenes", [])
    
    for audio in audio_info:
        idx = audio["id"]
        dur = audio["duration"]
        audio_path = audio["audio_path"]
        scene = scenes[idx] if idx < len(scenes) else {}
        
        # 字幕生成
        ass_path = str(WORK_DIR / f"sub_{idx:02d}.ass")
        generate_ass(audio["narration"], dur, ass_path)
        
        # シーン動画生成
        scene_path = make_scene(scene, idx, dur, audio_path, ass_path)
        if scene_path and os.path.exists(scene_path):
            scene_files.append(scene_path)
            print(f"  Scene {idx}: {dur:.1f}秒 ✅")
    
    if not scene_files:
        print("❌ シーン生成失敗")
        sys.exit(1)
    
    # Step 4: シーン結合
    print("\n[4/5] シーン結合中...")
    concat_file = str(WORK_DIR / "concat.txt")
    with open(concat_file, "w") as f:
        for sf in scene_files:
            f.write(f"file '{sf}'\n")
    
    safe_title = "".join(c for c in title if c.isalnum() or c in "ぁ-ん゛゜ァ-ヴー一-龯 　").strip()[:30]
    final_output = str(OUTPUT_DIR / f"trio_{style}_{safe_title}.mp4")
    
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-pix_fmt", "yuv420p", final_output])
    
    if not os.path.exists(final_output):
        print("❌ 最終動画生成失敗")
        sys.exit(1)
    
    # Step 5: 最後0.5秒トリム
    print("\n[5/5] 仕上げ処理...")
    trimmed = final_output.replace(".mp4", "_trim.mp4")
    dur_r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", final_output], capture_output=True, text=True)
    try:
        total_dur = float(dur_r.stdout.strip()) - 0.5
        _run(["ffmpeg", "-y", "-i", final_output, "-t", str(total_dur),
              "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", trimmed])
        if os.path.exists(trimmed) and os.path.getsize(trimmed) > 100000:
            shutil.move(trimmed, final_output)
            print("  ✂️ 0.5秒トリム完了")
    except:
        pass
    
    size = os.path.getsize(final_output) // 1024
    print(f"\n✅ 完成: {final_output} ({size}KB)")
    
    # プラン保存
    with open("output/trio_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
