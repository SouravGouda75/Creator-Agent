import asyncio
import os
from pathlib import Path
from typing import Optional
import edge_tts
from moviepy import AudioFileClip
from src.config import DEFAULT_VOICES, TEMP_DIR

class VoiceEngine:
    """Handles studio-grade Text-To-Speech generation using Edge TTS."""

    def __init__(self, voice: Optional[str] = None):
        self.voice = voice or DEFAULT_VOICES["english_male"]

    async def _generate_audio_async(self, text: str, output_path: Path, rate: str = "+0%", pitch: str = "+0Hz"):
        communicate = edge_tts.Communicate(text=text, voice=self.voice, rate=rate, pitch=pitch)
        await communicate.save(str(output_path))

    def generate_speech(
        self,
        text: str,
        output_filename: str = "voiceover.mp3",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> tuple[Path, float]:
        """
        Generates speech audio file from text.
        Returns:
            (Path to generated audio, duration in seconds)
        """
        if not text.strip():
            raise ValueError("Text for voice generation cannot be empty.")

        output_path = TEMP_DIR / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Run Edge-TTS
        asyncio.run(self._generate_audio_async(text, output_path, rate=rate, pitch=pitch))

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Failed to generate audio file at {output_path}")

        # Get audio duration using moviepy
        with AudioFileClip(str(output_path)) as audio:
            duration = audio.duration

        return output_path, duration

    @staticmethod
    def list_available_presets() -> dict[str, str]:
        return DEFAULT_VOICES
