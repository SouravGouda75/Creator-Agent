import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
ASSETS_DIR = ROOT_DIR / "assets"
TEMP_DIR = ROOT_DIR / "temp"
FONTS_DIR = ASSETS_DIR / "fonts"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Video Formats
FORMATS = {
    "reel": {
        "name": "Reel / Short (9:16)",
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "caption_y_pos": 0.70,  # Optimal TikTok/Reels safe zone (lower-third, above UI)
        "font_size": 72,
        "words_per_batch": 3,   # Snappy 2-3 words per caption card
    },
    "video": {
        "name": "Standard YouTube Video (16:9)",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "caption_y_pos": 0.80,  # Lower third
        "font_size": 56,
        "words_per_batch": 4,
    }
}

# Voices available for Edge-TTS
DEFAULT_VOICES = {
    "english_male": "en-US-ChristopherNeural",
    "english_female": "en-US-AriaNeural",
    "hindi_male": "hi-IN-MadhurNeural",
    "hindi_female": "hi-IN-SwaraNeural",
    "indian_english_male": "en-IN-PrabhatNeural",
    "indian_english_female": "en-IN-NeerjaNeural",
}

# Hugging Face Settings
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")

# Whisper Model Configuration
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_CPU_THREADS = 8
