import os
import sys
import re
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console

from src.config import FORMATS, OUTPUTS_DIR
from src.script_analyzer import ScriptAnalyzer
from src.voice_engine import VoiceEngine
from src.transcriber import Transcriber
from src.visual_engine import VisualEngine
from src.caption_styler import CaptionStyler
from src.video_composer import VideoComposer

console = Console(safe_box=True)

class CreatorAgent:
    """Master AI agent for automated, high-impact video creation."""

    def __init__(
        self,
        voice: Optional[str] = None,
        whisper_model: str = "base",
        hf_token: Optional[str] = None,
    ):
        self.script_analyzer = ScriptAnalyzer(hf_token=hf_token)
        self.voice_engine = VoiceEngine(voice=voice)
        self.transcriber = Transcriber(model_size=whisper_model)
        self.visual_engine = VisualEngine(hf_token=hf_token)

    def create_from_audio(
        self,
        audio_path: str | Path,
        category: str = "reel",
        num_scenes: int = 4,
        output_name: Optional[str] = None,
    ) -> Path:
        """
        Scenario 1: Creates an engaging captioned video directly from an existing audio file.
        """
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Provided audio file does not exist: {audio_file}")

        console.print(f"[bold cyan]🎤 Step 1/4:[/bold cyan] Transcribing audio with word-level timestamps...")
        transcription = self.transcriber.transcribe(audio_file)
        console.print(f"[green]✓ Detected language: {transcription['language']}, Duration: {transcription['duration']}s[/green]")

        # 2. Extract scene visual prompts from transcript
        console.print(f"[bold cyan]🎨 Step 2/4:[/bold cyan] Generating visual scenes for the audio...")
        full_text = transcription["full_text"]
        words_found = re.findall(r"\b[A-Za-z]{4,}\b", full_text)
        chunk_size = max(1, len(words_found) // num_scenes)

        visual_paths = []
        for i in range(num_scenes):
            sub_words = words_found[i * chunk_size : (i + 1) * chunk_size]
            prompt_theme = " ".join(sub_words[:4]) if sub_words else "creative modern dynamic aesthetic"
            visual_prompt = f"cinematic commercial shot of {prompt_theme}, vibrant lighting, 4k ultra-detailed"
            
            console.print(f"  - Generating Scene {i+1}: [italic]{prompt_theme}[/italic]")
            img_path = self.visual_engine.prepare_visual(visual_prompt, category=category, scene_id=i + 1)
            visual_paths.append(img_path)

        # 3. Create Highlighted Captions
        console.print(f"[bold cyan]✨ Step 3/4:[/bold cyan] Building animated karaoke highlighted captions...")
        fmt = FORMATS.get(category, FORMATS["reel"])
        batches = self.transcriber.create_caption_batches(
            transcription["words"],
            words_per_batch=fmt["words_per_batch"],
        )
        caption_styler = CaptionStyler(category=category)
        caption_clips = caption_styler.build_caption_clips(batches)
        console.print(f"[green]✓ Generated {len(caption_clips)} dynamic highlight cards.[/green]")

        # 4. Render Video
        console.print(f"[bold cyan]🎬 Step 4/4:[/bold cyan] Stitching video clips, audio, and captions with MoviePy...")
        filename = output_name or f"audio_video_{category}_{audio_file.stem}.mp4"
        composer = VideoComposer(category=category)
        final_video_path = composer.compose_video(
            visual_paths=visual_paths,
            audio_path=audio_file,
            caption_clips=caption_clips,
            output_filename=filename,
        )

        console.print(f"[bold green]🚀 Video ready:[/bold green] [bold white]{final_video_path}[/bold white]")
        return final_video_path

    def create_from_document(
        self,
        doc_or_text: str | Path,
        category: str = "reel",
        target_duration: int = 60,
        output_name: Optional[str] = None,
    ) -> Path:
        """
        Scenario 2: Analyzes documents/notes, crafts a script, generates voiceover,
        fetches visuals, adds highlighted captions, and renders the complete video.
        """
        console.print(f"[bold cyan]📝 Step 1/5:[/bold cyan] Analyzing notes & structuring video script...")
        script_data = self.script_analyzer.generate_script(
            content_or_doc=doc_or_text,
            category=category,
            target_duration=target_duration,
        )
        scenes = script_data.get("scenes", [])
        title = script_data.get("title", "Creator Video")
        console.print(f"[green]✓ Script generated: '{title}' ({len(scenes)} scenes)[/green]")

        # Combine narration for voice-over
        full_narration = " ".join(scene["narration"] for scene in scenes)

        # 2. Generate Voiceover
        console.print(f"[bold cyan]🎙️ Step 2/5:[/bold cyan] Synthesizing studio voiceover with Edge-TTS...")
        audio_path, duration = self.voice_engine.generate_speech(full_narration)
        console.print(f"[green]✓ Voiceover generated ({round(duration, 1)}s)[/green]")

        # 3. Transcribe for exact word timestamps
        console.print(f"[bold cyan]⏱️ Step 3/5:[/bold cyan] Transcribing voiceover for word-level sync...")
        transcription = self.transcriber.transcribe(audio_path)

        # 4. Generate Visuals for each scene
        console.print(f"[bold cyan]🎨 Step 4/5:[/bold cyan] Generating visual scenes...")
        visual_paths = []
        for i, scene in enumerate(scenes):
            v_prompt = scene.get("visual_prompt", scene["narration"])
            console.print(f"  - Scene {i+1}: [italic]{v_prompt[:60]}...[/italic]")
            img_path = self.visual_engine.prepare_visual(v_prompt, category=category, scene_id=i + 1)
            visual_paths.append(img_path)

        # 5. Build Highlighted Captions & Render
        console.print(f"[bold cyan]✨ Step 5/5:[/bold cyan] Styling captions & assembling final video...")
        fmt = FORMATS.get(category, FORMATS["reel"])
        batches = self.transcriber.create_caption_batches(
            transcription["words"],
            words_per_batch=fmt["words_per_batch"],
        )
        caption_styler = CaptionStyler(category=category)
        caption_clips = caption_styler.build_caption_clips(batches)

        filename = output_name or f"campaign_{category}_{title.lower().replace(' ', '_')[:30]}.mp4"
        composer = VideoComposer(category=category)
        final_video_path = composer.compose_video(
            visual_paths=visual_paths,
            audio_path=audio_path,
            caption_clips=caption_clips,
            output_filename=filename,
        )

        console.print(f"[bold green]🚀 Complete campaign video created:[/bold green] [bold white]{final_video_path}[/bold white]")
        return final_video_path
