import re
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
from src.config import FONTS_DIR, FORMATS, TEMP_DIR

class CaptionStyler:
    """Renders viral karaoke-style highlighted captions with bold 3D drop shadow and neon effects."""

    def __init__(
        self,
        category: str = "reel",
        highlight_color: str = "#FFE600",   # Neon Yellow (Hormozi signature)
        base_color: str = "#FFFFFF",        # Pure Crisp White
        stroke_color: str = "#000000",      # Deep Black Outline
        stroke_width: int = 8,
    ):
        self.category = category
        self.fmt = FORMATS.get(category, FORMATS["reel"])
        self.highlight_color = highlight_color
        self.base_color = base_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.font = self._load_font(self.fmt["font_size"])

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        font_candidates = [
            FONTS_DIR / "Anton-Regular.ttf",
            Path(r"C:\Windows\Fonts\ariblk.ttf"),    # Arial Black
            Path(r"C:\Windows\Fonts\impact.ttf"),    # Impact
            Path(r"C:\Windows\Fonts\arialbd.ttf"),   # Arial Bold
            Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        ]
        for font_path in font_candidates:
            p = Path(font_path)
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def render_caption_card(
        self,
        words_in_batch: list[dict[str, Any]],
        active_index: int,
    ) -> Image.Image:
        """
        Renders a transparent RGBA image of the current caption card,
        highlighting the active word in neon with a crisp 3D drop shadow.
        No ugly black tape box.
        """
        width = self.fmt["width"]
        height = int(self.fmt["font_size"] * 2.8)

        # High-res canvas with transparent background
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Clean words and measure dimensions
        word_spacings = []
        space_width = draw.textlength(" ", font=self.font)
        total_text_width = 0

        for w_data in words_in_batch:
            raw = str(w_data.get("word", "")).strip()
            # Clean leading/trailing hyphens, dashes, and stray punctuation
            cleaned = re.sub(r"^[-_–—.,!?:;\"'()\[\]{}]+|[-_–—.,!?:;\"'()\[\]{}]+$", "", raw).upper()
            w_text = cleaned if cleaned else raw.upper()
            w_len = draw.textlength(w_text, font=self.font)
            word_spacings.append((w_text, w_len))
            total_text_width += w_len

        total_text_width += space_width * max(0, len(words_in_batch) - 1)

        # Center the caption line horizontally
        start_x = (width - total_text_width) / 2
        y_pos = (height - self.fmt["font_size"]) / 2

        # Draw each word with 3D drop shadow and thick outline
        curr_x = start_x
        shadow_offset_x = 5
        shadow_offset_y = 6

        for idx, (w_text, w_len) in enumerate(word_spacings):
            color = self.highlight_color if idx == active_index else self.base_color

            # 1. Solid drop shadow for 3D sticker pop (replaces ugly background box)
            draw.text(
                (curr_x + shadow_offset_x, y_pos + shadow_offset_y),
                w_text,
                font=self.font,
                fill=(0, 0, 0, 220),
                stroke_width=self.stroke_width + 1,
                stroke_fill=(0, 0, 0, 220),
            )

            # 2. Main text with bold outline and vivid fill
            draw.text(
                (curr_x, y_pos),
                w_text,
                font=self.font,
                fill=color,
                stroke_width=self.stroke_width,
                stroke_fill=self.stroke_color,
            )

            curr_x += w_len + space_width

        return img

    def build_caption_clips(self, batches: list[dict[str, Any]]) -> list[ImageClip]:
        """
        Builds a list of timed MoviePy ImageClips with transparency,
        each corresponding to an active word highlight.
        """
        clips = []
        video_height = self.fmt["height"]
        caption_y = int(video_height * self.fmt["caption_y_pos"])

        for batch_idx, batch in enumerate(batches):
            words = batch["words"]
            for word_idx, active_word in enumerate(words):
                w_start = active_word["start"]
                # Active until next word starts or batch ends
                if word_idx + 1 < len(words):
                    w_end = words[word_idx + 1]["start"]
                else:
                    w_end = active_word["end"]

                duration = max(0.12, w_end - w_start)

                card_img = self.render_caption_card(words, active_index=word_idx)
                img_array = np.array(card_img)

                # Create transparent MoviePy ImageClip
                clip = (
                    ImageClip(img_array, is_mask=False)
                    .with_start(w_start)
                    .with_duration(duration)
                    .with_position(("center", caption_y))
                )
                clips.append(clip)

        return clips
