from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
from src.config import FORMATS, TEMP_DIR

class CaptionStyler:
    """Renders viral karaoke-style highlighted captions with glowing word effects."""

    def __init__(
        self,
        category: str = "reel",
        highlight_color: str = "#FFE600",   # Neon Yellow
        base_color: str = "#FFFFFF",        # Pure White
        stroke_color: str = "#000000",      # Deep Black Outline
        stroke_width: int = 6,
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
            r"C:\Windows\Fonts\impact.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]
        for font_path in font_candidates:
            if Path(font_path).exists():
                try:
                    return ImageFont.truetype(font_path, size)
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
        highlighting the word at active_index.
        """
        width = self.fmt["width"]
        height = int(self.fmt["font_size"] * 2.5)

        # High-res canvas with transparent background
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Measure dimensions of each word
        word_spacings = []
        space_width = draw.textlength(" ", font=self.font)
        total_text_width = 0

        for w_data in words_in_batch:
            w_text = w_data["word"].upper()
            w_len = draw.textlength(w_text, font=self.font)
            word_spacings.append((w_text, w_len))
            total_text_width += w_len

        total_text_width += space_width * max(0, len(words_in_batch) - 1)

        # Center the caption line horizontally
        start_x = (width - total_text_width) / 2
        y_pos = (height - self.fmt["font_size"]) / 2

        # Optional: Render dark rounded pill backdrop for contrast
        pill_pad_x = 28
        pill_pad_y = 12
        pill_box = [
            start_x - pill_pad_x,
            y_pos - pill_pad_y,
            start_x + total_text_width + pill_pad_x,
            y_pos + self.fmt["font_size"] + pill_pad_y + 10,
        ]
        draw.rounded_rectangle(pill_box, radius=18, fill=(0, 0, 0, 160))

        # Draw each word with stroke & color
        curr_x = start_x
        for idx, (w_text, w_len) in enumerate(word_spacings):
            color = self.highlight_color if idx == active_index else self.base_color

            # Draw stroke for maximum contrast
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
