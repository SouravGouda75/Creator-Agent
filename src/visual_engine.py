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
        Generates realistic visuals using free AI inference endpoint.
        Uses model=turbo for ultra-fast, timeout-free 8k generation.
        """
        try:
            enhanced = f"{prompt}, 8k resolution, cinematic commercial lighting, 3d octane render, highly detailed, photorealistic, minimalist studio, sharp focus, masterpiece"
            encoded_prompt = urllib.parse.quote(enhanced[:280])
            # Extra height for clean watermark slicing
            fetch_height = height + 60
            seed = random.randint(1000, 9999999)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={fetch_height}&nologo=true&seed={seed}&model=turbo"
            resp = requests.get(url, timeout=18)
            if resp.status_code == 200 and len(resp.content) > 5000:
                output_path.write_bytes(resp.content)
                return True
        except Exception:
            pass
        return False

    def _fetch_stock_broll(self, prompt: str, width: int, height: int, output_path: Path) -> bool:
        """
        Fetches high-definition cinematic stock photography matching the scene topic.
        Guarantees 100% photorealistic visuals when AI generator is busy or throttled.
        """
        stock_library = {
            "studio": [
                "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=1080&q=85", # Shure Studio Mic
                "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=1080&q=85", # Audio mixing board
            ],
            "workspace": [
                "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=1080&q=85", # Creative UI workspace
                "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1080&q=85", # Modern digital team
            ],
            "analytics": [
                "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=1080&q=85", # Social viral phone
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1080&q=85", # High growth analytics
            ],
            "creative": [
                "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1080&q=85", # Cyberpunk tech neon
                "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&q=85", # Futuristic circuit
            ],
        }

        # Match theme
        lower = prompt.lower()
        if any(k in lower for k in ["voice", "audio", "mic", "sound", "studio", "speak"]):
            chosen_url = random.choice(stock_library["studio"])
        elif any(k in lower for k in ["caption", "viral", "phone", "tiktok", "reel", "metric"]):
            chosen_url = random.choice(stock_library["analytics"])
        elif any(k in lower for k in ["tech", "ai", "future", "cyber", "render", "digital"]):
            chosen_url = random.choice(stock_library["creative"])
        else:
            chosen_url = random.choice(stock_library["workspace"])

        try:
            resp = requests.get(chosen_url, timeout=12)
            if resp.status_code == 200 and len(resp.content) > 5000:
                output_path.write_bytes(resp.content)
                return True
        except Exception:
            pass
        return False

    def _generate_stylized_backdrop(self, prompt: str, width: int, height: int, output_path: Path):
        """
        Offline fallback that creates a sleek, dark studio cinematography canvas
        with realistic soft spotlights (no weird rainbow circles).
        """
        base = Image.new("RGB", (width, height), color=(18, 20, 26))
        draw = ImageDraw.Draw(base)

        # Soft luxury studio glow from top-center
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        cx = width // 2
        cy = int(height * 0.35)
        overlay_draw.ellipse(
            [(cx - 450, cy - 450), (cx + 450, cy + 450)],
            fill=(40, 60, 95, 120),
        )
        overlay = overlay.filter(ImageFilter.GaussianBlur(120))
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
        Automatically strips watermarks and applies cinematic depth vignette.
        """
        fmt = FORMATS.get(category, FORMATS["reel"])
        width, height = fmt["width"], fmt["height"]

        filename = f"scene_{scene_id}_{category}.jpg"
        output_path = TEMP_DIR / filename

        # 1. Try Hugging Face API if token available
        success = self._generate_hf_image(prompt, width, height, output_path)

        # 2. Try Fast Free AI Image generation (turbo)
        if not success:
            success = self._generate_free_ai_image(prompt, width, height, output_path)

        # 3. Fallback to HD Stock B-Roll (100% photorealistic)
        if not success or not output_path.exists():
            success = self._fetch_stock_broll(prompt, width, height, output_path)

        # 4. Offline studio backdrop fallback (if no internet)
        if not success or not output_path.exists():
            self._generate_stylized_backdrop(prompt, width, height, output_path)

        # Watermark removal and exact dimensions
        with Image.open(output_path) as raw_img:
            # Crop bottom 60px to eradicate any API watermark/logo
            w_orig, h_orig = raw_img.size
            cleaned = raw_img.crop((0, 0, w_orig, max(100, h_orig - 60)))

            # Resize with aspect ratio preserved, then center-crop
            img_ratio = cleaned.width / cleaned.height
            target_ratio = width / height

            if img_ratio > target_ratio:
                new_height = height
                new_width = int(height * img_ratio)
            else:
                new_width = width
                new_height = int(width / img_ratio)

            resized = cleaned.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            cropped = resized.crop((left, top, left + width, top + height))

            # Apply subtle bottom dark vignette gradient for clean subtitle contrast
            vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            v_draw = ImageDraw.Draw(vignette)
            grad_start = int(height * 0.62)
            for y in range(grad_start, height):
                alpha = int(100 * ((y - grad_start) / (height - grad_start)))
                v_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

            final_frame = Image.alpha_composite(cropped.convert("RGBA"), vignette).convert("RGB")
            final_frame.save(output_path, "JPEG", quality=95)

        return output_path
