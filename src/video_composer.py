import os
from pathlib import Path
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
    afx,
    vfx,
)
from src.config import ASSETS_DIR, FORMATS, OUTPUTS_DIR, TEMP_DIR

class VideoComposer:
    """Assembles visuals with Ken Burns motion, cinematic crossfades, background music, and viral captions."""

    def __init__(self, category: str = "reel"):
        self.category = category
        self.fmt = FORMATS.get(category, FORMATS["reel"])

    def compose_video(
        self,
        visual_paths: list[Path],
        audio_path: Path,
        caption_clips: list[ImageClip],
        output_filename: str = "final_output.mp4",
        threads: int = 16,
    ) -> Path:
        """
        Combines visual scene clips with Ken Burns camera motion,
        narration audio, subtle background score, and animated captions.
        Renders the final MP4 video file.
        """
        if not visual_paths:
            raise ValueError("At least one visual path is required to compose video.")
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        output_path = OUTPUTS_DIR / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Load Audio and determine total duration
        audio_clip = AudioFileClip(str(audio_path))
        total_duration = audio_clip.duration

        # 2. Mix subtle background music if available for creator glue
        bg_music_path = ASSETS_DIR / "audio" / "lofi_beat.wav"
        if bg_music_path.exists():
            try:
                bg_clip = (
                    AudioFileClip(str(bg_music_path))
                    .with_duration(total_duration)
                    .with_effects([
                        afx.MultiplyVolume(0.10),
                        afx.AudioFadeIn(0.5),
                        afx.AudioFadeOut(0.8),
                    ])
                )
                final_audio = CompositeAudioClip([audio_clip, bg_clip]).with_duration(total_duration)
            except Exception:
                final_audio = audio_clip
        else:
            final_audio = audio_clip

        # 3. Dynamic Ken Burns camera motion & cinematic crossfades across scenes
        num_scenes = len(visual_paths)
        overlap = 0.4 if num_scenes > 1 else 0.0
        scene_duration = (total_duration + (num_scenes - 1) * overlap) / num_scenes

        scene_clips = []
        for i, img_path in enumerate(visual_paths):
            dur = max(0.8, scene_duration)

            # Build Ken Burns slow zoom (1.0x -> 1.08x) so visual is never static
            clip_effects = [vfx.Resize(lambda t, d=dur: 1.0 + 0.08 * (t / d))]

            # Add smooth crossfade transition on scene changes
            if i > 0 and overlap > 0:
                clip_effects.append(vfx.CrossFadeIn(overlap))

            img_clip = (
                ImageClip(str(img_path))
                .with_duration(dur)
                .resized(new_size=(self.fmt["width"], self.fmt["height"]))
                .with_effects(clip_effects)
            )
            scene_clips.append(img_clip)

        # Concatenate scenes with crossfade overlap
        if len(scene_clips) > 1 and overlap > 0:
            background_video = concatenate_videoclips(
                scene_clips,
                padding=-overlap,
                method="compose",
            )
        else:
            background_video = concatenate_videoclips(scene_clips, method="compose")

        background_video = background_video.with_duration(total_duration)

        # 4. Layer the caption clips on top of the background
        final_composite = CompositeVideoClip(
            [background_video, *caption_clips],
            size=(self.fmt["width"], self.fmt["height"]),
        )
        final_composite = final_composite.with_duration(total_duration)
        final_composite = final_composite.with_audio(final_audio)

        # 5. Render final video using multithreaded FFmpeg
        temp_audio_name = str(TEMP_DIR / f"temp_snd_{os.getpid()}.m4a")
        final_composite.write_videofile(
            str(output_path),
            fps=self.fmt["fps"],
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=threads,
            logger="bar",
            temp_audiofile=temp_audio_name,
            remove_temp=False,
        )

        # Clean up resources safely
        audio_clip.close()
        final_composite.close()
        for sc in scene_clips:
            sc.close()
        for cc in caption_clips:
            cc.close()

        # Safe post-cleanup of temporary audio
        try:
            p = Path(temp_audio_name)
            if p.exists():
                p.unlink(missing_ok=True)
        except Exception:
            pass

        return output_path
