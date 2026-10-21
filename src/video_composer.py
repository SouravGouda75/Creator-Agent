import os
from pathlib import Path
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)
from src.config import FORMATS, OUTPUTS_DIR

class VideoComposer:
    """Assembles visuals, audio, transitions, and dynamic captions into a final video."""

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
        Combines visual scene clips, narration audio, and animated captions.
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

        # 2. Divide total duration across the visual scenes
        num_scenes = len(visual_paths)
        scene_duration = total_duration / num_scenes

        scene_clips = []
        for i, img_path in enumerate(visual_paths):
            # Calculate duration for each scene (ensure last scene takes any fractional remainder)
            dur = scene_duration if i < num_scenes - 1 else (total_duration - (scene_duration * i))
            dur = max(0.5, dur)

            img_clip = (
                ImageClip(str(img_path))
                .with_duration(dur)
                .resized(new_size=(self.fmt["width"], self.fmt["height"]))
            )
            scene_clips.append(img_clip)

        # Concatenate background visual scenes
        background_video = concatenate_videoclips(scene_clips, method="compose")
        background_video = background_video.with_duration(total_duration)

        # 3. Layer the caption clips on top of the background
        final_composite = CompositeVideoClip(
            [background_video, *caption_clips],
            size=(self.fmt["width"], self.fmt["height"]),
        )
        final_composite = final_composite.with_duration(total_duration)
        final_composite = final_composite.with_audio(audio_clip)

        # 4. Render final video using multithreaded FFmpeg
        final_composite.write_videofile(
            str(output_path),
            fps=self.fmt["fps"],
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=threads,
            logger="bar",
        )

        # Clean up resources
        audio_clip.close()
        final_composite.close()
        for sc in scene_clips:
            sc.close()
        for cc in caption_clips:
            cc.close()

        return output_path
