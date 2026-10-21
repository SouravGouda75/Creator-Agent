from pathlib import Path
from typing import Any
from faster_whisper import WhisperModel
from src.config import (
    WHISPER_MODEL_SIZE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_CPU_THREADS,
)

class Transcriber:
    """Handles Speech-To-Text transcription with word-level timestamps using Whisper."""

    def __init__(self, model_size: str = WHISPER_MODEL_SIZE):
        self.model_size = model_size
        self._model: WhisperModel | None = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE,
                cpu_threads=WHISPER_CPU_THREADS,
            )
        return self._model

    def transcribe(self, audio_path: Path | str) -> dict[str, Any]:
        """
        Transcribes the given audio and extracts word-level timing data.
        Returns:
            {
                "full_text": str,
                "language": str,
                "duration": float,
                "words": [{"word": str, "start": float, "end": float}, ...],
                "segments": [{"text": str, "start": float, "end": float}, ...]
            }
        """
        audio_path_str = str(audio_path)
        segments_gen, info = self.model.transcribe(
            audio_path_str,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
        )

        all_words = []
        all_segments = []
        full_text_parts = []

        for segment in segments_gen:
            full_text_parts.append(segment.text.strip())
            all_segments.append({
                "text": segment.text.strip(),
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
            })
            if segment.words:
                for w in segment.words:
                    word_clean = w.word.strip()
                    if word_clean:
                        all_words.append({
                            "word": word_clean,
                            "start": round(w.start, 2),
                            "end": round(w.end, 2),
                        })

        return {
            "full_text": " ".join(full_text_parts),
            "language": info.language,
            "duration": round(info.duration, 2),
            "words": all_words,
            "segments": all_segments,
        }

    @staticmethod
    def create_caption_batches(words: list[dict[str, Any]], words_per_batch: int = 3) -> list[dict[str, Any]]:
        """
        Groups words into compact caption cards for dynamic highlight display.
        Each batch has:
            - batch_index: int
            - start: float
            - end: float
            - text: str
            - words: list of word dicts with start/end
        """
        if not words:
            return []

        batches = []
        for i in range(0, len(words), words_per_batch):
            chunk = words[i : i + words_per_batch]
            batch_start = chunk[0]["start"]
            batch_end = chunk[-1]["end"]
            # Ensure positive duration
            if batch_end <= batch_start:
                batch_end = batch_start + 0.5

            batches.append({
                "batch_index": len(batches),
                "start": batch_start,
                "end": batch_end,
                "text": " ".join(w["word"] for w in chunk),
                "words": chunk,
            })
        return batches
