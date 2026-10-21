# 🎬 AI Creator Agent

An automated, CPU-optimized AI Video Production Agent for YouTube Creators, Reels, and Marketers.

## 🚀 Features
- **Scenario 1 (Audio -> Video):** Turn any voice recording or podcast clip into a viral video with word-by-word highlighted karaoke captions and matched visuals.
- **Scenario 2 (Docs -> Video):** Convert notes, campaign docs, or scripts into a full video with natural AI voiceover, AI-generated scene visuals, and synced subtitles.
- **Multiple Formats:**
  - **Reels / Shorts (9:16):** 1080x1920, fast-paced, centered glowing captions.
  - **YouTube Videos (16:9):** 1920x1080, cinematic lower-third captions.
- **Optimized for CPU:** Uses multi-threaded Whisper, Edge-TTS, and MoviePy.

## 📦 How to Run

1. Run the interactive creator CLI:
```powershell
.venv\Scripts\python.exe main.py
```

2. Run directly with CLI arguments:
```powershell
# Quick demo reel:
.venv\Scripts\python.exe main.py --scenario demo

# From audio file:
.venv\Scripts\python.exe main.py --scenario audio --input path\to\audio.mp3 --category reel

# From notes or document:
.venv\Scripts\python.exe main.py --scenario doc --input path\to\notes.txt --category reel --duration 60
```
