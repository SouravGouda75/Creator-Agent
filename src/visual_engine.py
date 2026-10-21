import math
import random
import urllib.parse
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFilter
import requests
from src.config import FORMATS, HF_IMAGE_MODEL, HF_TOKEN, TEMP_DIR

class VisualEngine:
    """Fetches or generates high-definition visuals for scenes in target aspect ratios."""

    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token or HF_TOKEN

    def _generate_hf_image(self, prompt: str, width: int, height: int, output_path: Path) -> bool:
        """Attempts generation using Hugging Face router API."""
        if not self.hf_token:
            return False
        try:
            api_url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {"width": width, "height": height},
            }
            resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                output_path.write_bytes(resp.content)
                return True
        except Exception:
            pass
        return False

    def _generate_free_ai_image(self, prompt: str, width: int, height: int, output_path: Path) -> bool:
        """
        Generates realistic visuals using free FLUX/SDXL inference endpoint.
        Fast, zero setup, ideal for creators without requiring paid keys.
        """
        try:
            encoded_prompt = urllib.parse.quote(prompt[:200])
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={random.randint(100, 999999)}&model=flux"
            resp = requests.get(url, timeout=25)
            if resp.status_code == 200 and len(resp.content) > 5000:
                output_path.write_bytes(resp.content)
                return True
        except Exception:
            pass
        return False

    def _generate_stylized_backdrop(self, prompt: str, width: int, height: int, output_path: Path):
        """
        Offline fallback that creates aesthetic, cinematic gradients and geometric patterns.
        Guarantees that video production never breaks even when offline.
        """
        base = Image.new("RGB", (width, height), color=(15, 17, 26))
        draw = ImageDraw.Draw(base)

        # Select modern dynamic color palette
        palettes = [
            [(26, 35, 126), (13, 71, 161), (0, 188, 212)],     # Electric Blue / Cyan
            [(74, 20, 140), (136, 14, 79), (233, 30, 99)],     # Cyberpunk Purple / Pink
            [(1, 87, 155), (0, 77, 64), (0, 230, 118)],        # Emerald Aurora
            [(38, 50, 56), (98, 0, 234), (255, 110, 64)],      # Sunset Neon
        ]
        chosen = random.choice(palettes)

        # Draw smooth radial / vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(chosen[0][0] * (1 - ratio) + chosen[1][0] * ratio)
            g = int(chosen[0][1] * (1 - ratio) + chosen[1][1] * ratio)
            b = int(chosen[0][2] * (1 - ratio) + chosen[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Add luminous ambient circles
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for _ in range(5):
            cx = random.randint(100, width - 100)
            cy = random.randint(100, height - 100)
            radius = random.randint(200, 500)
            color = (*chosen[2], random.randint(30, 70))
            overlay_draw.ellipse(
                [(cx - radius, cy - radius), (cx + radius, cy + radius)],
                fill=color,
            )

        overlay = overlay.filter(ImageFilter.GaussianBlur(80))
        base.paste(overlay, (0, 0), overlay)
        base.save(output_path, "JPEG", quality=95)

    def prepare_visual(
        self,
        prompt: str,
        category: str = "reel",
        scene_id: int = 1,
    ) -> Path:
        """
        Prepares a high-resolution visual for the given scene prompt.
        Ensures exact target resolution matching the chosen category (Reel vs Video).
        """
        fmt = FORMATS.get(category, FORMATS["reel"])
        width, height = fmt["width"], fmt["height"]

        filename = f"scene_{scene_id}_{category}.jpg"
        output_path = TEMP_DIR / filename

        # 1. Try Hugging Face API if token available
        success = self._generate_hf_image(prompt, width, height, output_path)

        # 2. Try Free AI Image generation
        if not success:
            success = self._generate_free_ai_image(prompt, width, height, output_path)

        # 3. Fallback to aesthetic gradient backdrop
        if not success or not output_path.exists():
            self._generate_stylized_backdrop(prompt, width, height, output_path)

        # Ensure exact dimensions
        with Image.open(output_path) as img:
            if img.size != (width, height):
                # Resize with aspect ratio preserved, then center-crop
                img_ratio = img.width / img.height
                target_ratio = width / height

                if img_ratio > target_ratio:
                    new_height = height
                    new_width = int(height * img_ratio)
                else:
                    new_width = width
                    new_height = int(width / img_ratio)

                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                cropped = resized.crop((left, top, left + width, top + height))
                cropped.save(output_path, "JPEG", quality=95)

        return output_path
