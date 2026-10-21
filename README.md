# 🎬 Creator Agent

> **Turn raw audio recordings or notes into viral, studio-grade videos in minutes with AI.**  
> Optimized for modern creators, YouTube Shorts, Instagram Reels, and long-form YouTube videos. Built to run lightning fast even on CPU-only machines.

---

## ⚡ Highlights

* **🎙️ Scenario 1 (Audio to Viral Video):** Have an audio voice note, podcast snippet, or speech? Drop it in. Creator Agent transcribes it, extracts visual cues, fetches 8K photorealistic scene visuals, and overlays Alex Hormozi style karaoke captions.
* **📄 Scenario 2 (Docs & Notes to Campaign Video):** Paste rough notes, documentation, or campaign briefs. The agent structures an engaging script (Hook, Story, CTA), synthesizes natural human voiceover via Edge-TTS, and renders a complete video.
* **✨ Dynamic Karaoke Subtitles:** Bold, centered, 3D drop-shadow captions with glowing neon active-word highlighting using Anton typography (no ugly black tape boxes).
* **🎥 Ken Burns Dynamic Motion:** Eliminates boring static imagery with smooth camera slow-zooms (1.0x to 1.08x) and cinematic crossfades.
* **🎵 Background Score & Ducking:** Integrated lofi beat with subtle volume ducking and smooth audio fade in/out for a polished creator touch.
* **💻 CPU-Optimized:** Powered by multi-threaded `faster-whisper` and cloud-streamed TTS for zero local GPU dependency.

---

## 📐 Video Formats

| Format | Aspect Ratio | Resolution | Caption Position | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Reels / Shorts** | `9:16` Vertical | `1080 x 1920` | Safe-Zone Center (70%) | TikTok, IG Reels, YouTube Shorts (30–90s) |
| **Standard Video** | `16:9` Horizontal | `1920 x 1080` | Lower Third (80%) | YouTube Long-form, Tutorials (3–15 min) |

---

## 🛠️ Tech Stack

* **Environment & Package Manager:** [`uv`](https://github.com/astral-sh/uv) (Ultra-fast Python package resolver)
* **Speech-to-Text & Word Timestamps:** [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (CTranslate2 INT8 quantized on CPU)
* **Voice Synthesis (TTS):** [`edge-tts`](https://github.com/rany2/edge-tts) (Microsoft Neural Voices - English, Hindi, and more)
* **Video Compositing & Rendering:** [`moviepy`](https://github.com/Zulko/moviepy) v2.x + [`imageio-ffmpeg`](https://github.com/imageio/imageio-ffmpeg)
* **Visual Synthesis & B-Roll:** Multi-tier AI image engine with HD stock photography fallback
* **Typography & Caption Styling:** `Pillow` FreeType renderer with 3D drop-shadow geometry

---

## 🚀 Quickstart

### 1. Prerequisites
* Python 3.11+
* [uv](https://docs.astral.sh/uv/) installed:
  ```powershell
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. Clone & Setup
```bash
git clone https://github.com/SouravGouda75/Creator-Agent.git
cd Creator-Agent

# Create virtual environment and sync dependencies
uv venv --python 3.11
uv sync
```

### 3. Run the Interactive CLI
```powershell
.venv\Scripts\python.exe main.py
```

---

## 💻 CLI Usage

You can also trigger video generation directly with command-line arguments:

### Run Quick Demo Reel
```powershell
.venv\Scripts\python.exe main.py --scenario demo
```

### Create Video From Audio File
```powershell
.venv\Scripts\python.exe main.py --scenario audio --input "path\to\recording.mp3" --category reel
```

### Create Video From Notes / Document
```powershell
.venv\Scripts\python.exe main.py --scenario doc --input "path\to\notes.txt" --category reel --duration 60
```

---

## ⚙️ Configuration & Environment

Copy `.env.example` to `.env` (optional):
```env
# Optional: Hugging Face token for private/custom models
HF_TOKEN=

# Hugging Face Image Model
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell

# Whisper Model Size (tiny, base, small, medium)
WHISPER_MODEL_SIZE=base
```

---

## 📁 Project Structure

```
Creator-Agent/
├── assets/
│   ├── audio/              # Background beats (lofi, cinematic)
│   └── fonts/              # Typography (Anton-Regular)
├── src/
│   ├── config.py           # Aspect ratios, fonts, default voices
│   ├── script_analyzer.py  # Context-aware scene & prompt generator
│   ├── voice_engine.py     # Edge-TTS studio speech synthesis
│   ├── transcriber.py      # Faster-Whisper word-level timestamping
│   ├── visual_engine.py    # Multi-tier visual generator & watermark stripper
│   ├── caption_styler.py   # 3D drop-shadow karaoke caption renderer
│   ├── video_composer.py   # Ken Burns motion, audio ducking, MoviePy rendering
│   └── agent.py            # Master orchestration engine
├── main.py                 # Interactive terminal UI
├── pyproject.toml          # Project configuration & dependencies
└── README.md
```

---

## 📄 License
MIT License. Built for creators by creators.
