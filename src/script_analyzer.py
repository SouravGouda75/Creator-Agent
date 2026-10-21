import json
import re
from pathlib import Path
from typing import Any, Optional
import requests
from src.config import HF_TOKEN

class ScriptAnalyzer:
    """Analyzes raw documents, notes, or prompts and crafts structured video scripts."""

    def __init__(self, ollama_model: str = "llama3.2:3b", hf_token: Optional[str] = None):
        self.ollama_model = ollama_model
        self.hf_token = hf_token or HF_TOKEN

    def read_document(self, doc_path: Path | str) -> str:
        """Reads content from a text, markdown, or text-based document."""
        p = Path(doc_path)
        if not p.exists():
            raise FileNotFoundError(f"Document file not found: {p}")
        return p.read_text(encoding="utf-8", errors="ignore")

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Calls local Ollama server if available."""
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": self.ollama_model, "prompt": prompt, "stream": False},
                timeout=20,
            )
            if resp.status_code == 200:
                return resp.json().get("response")
        except Exception:
            pass
        return None

    def _call_hf_api(self, prompt: str) -> Optional[str]:
        """Calls Hugging Face router API if token is provided."""
        if not self.hf_token:
            return None
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 800, "temperature": 0.7},
            }
            resp = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                headers=headers,
                json=payload,
                timeout=25,
            )
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
        except Exception:
            pass
        return None

    def _synthesize_structured_fallback(self, content: str, category: str, duration_sec: int) -> dict[str, Any]:
        """
        Robust fallback parser that splits content into engaging scenes
        with narration and visual prompts even without external LLM connections.
        """
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        clean_text = " ".join(lines)
        sentences = re.split(r"(?<=[.!?]) +", clean_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

        # Determine target scene count
        # For Reels: 3-5 scenes (~10-15s per scene)
        # For Long videos: 6-12 scenes
        num_scenes = max(3, min(len(sentences), 5 if category == "reel" else 10))
        if not sentences:
            sentences = [
                "Welcome to this exciting update that you cannot afford to miss.",
                "Here is the core breakthrough that changes everything you know.",
                "Make sure to follow and share this for more amazing insights.",
            ]
            num_scenes = 3

        # Chunk sentences into scenes
        chunk_size = max(1, len(sentences) // num_scenes)
        scenes = []
        for i in range(num_scenes):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size if i < num_scenes - 1 else len(sentences)
            scene_text = " ".join(sentences[start_idx:end_idx]).strip()
            if not scene_text:
                continue

            # Generate descriptive visual prompt based on scene text
            words = [w for w in re.findall(r"\b[A-Za-z]{4,}\b", scene_text)]
            key_subject = " ".join(words[:4]) if words else "modern creative visuals"
            visual_prompt = f"cinematic high quality commercial shot of {key_subject}, professional 4k lighting, vibrant colors"

            scenes.append({
                "scene_id": i + 1,
                "narration": scene_text,
                "visual_prompt": visual_prompt,
                "keywords": words[:3],
            })

        title = sentences[0][:50] if sentences else "Creative Video Production"
        return {
            "title": title,
            "category": category,
            "target_duration": duration_sec,
            "scenes": scenes,
        }

    def generate_script(
        self,
        content_or_doc: str,
        category: str = "reel",
        target_duration: int = 60,
    ) -> dict[str, Any]:
        """
        Analyzes source content and returns a structured scene-by-scene script.
        """
        # If it is a file path, load it
        if Path(content_or_doc).exists() and Path(content_or_doc).is_file():
            content = self.read_document(content_or_doc)
        else:
            content = content_or_doc

        system_prompt = f"""
You are a professional video director and viral scriptwriter.
Convert the provided notes into an engaging video script for a {category} (approx {target_duration} seconds).
Format your response STRICTLY as valid JSON with no markdown wrapping:
{{
  "title": "Short punchy video title",
  "category": "{category}",
  "scenes": [
    {{
      "scene_id": 1,
      "narration": "Exact spoken voiceover text for this scene (engaging, natural, conversational)",
      "visual_prompt": "Ultra realistic cinematic visual description for AI image generator"
    }}
  ]
}}
Source Content:
{content[:2500]}
"""

        # 1. Try local Ollama
        response_text = self._call_ollama(system_prompt)

        # 2. Try Hugging Face API if Ollama was not active
        if not response_text:
            response_text = self._call_hf_api(system_prompt)

        # 3. Parse JSON from LLM output
        if response_text:
            try:
                # Find JSON block
                json_match = re.search(r"\{[\s\S]*\}", response_text)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    if "scenes" in parsed and len(parsed["scenes"]) > 0:
                        parsed["target_duration"] = target_duration
                        return parsed
            except Exception:
                pass

        # 4. Fallback to smart synthesizer
        return self._synthesize_structured_fallback(content, category, target_duration)
