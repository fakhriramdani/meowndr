"""
Base classes and types for the Papercraft Content Factory TTS provider system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import re


@dataclass
class WordTimestamp:
    """Word-level timing information aligned to spoken audio."""
    word: str
    start_sec: float
    end_sec: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "w": self.word,
            "s": round(self.start_sec, 3),
            "e": round(self.end_sec, 3),
        }


@dataclass
class TTSRequest:
    """Request payload for synthesizing speech from a script line."""
    text: str
    line_id: str
    speaker: str = "cat_scientist"
    voice_id: Optional[str] = None
    model_id: Optional[str] = None
    voice_settings: Dict[str, Any] = field(default_factory=dict)
    language: str = "id"
    output_format: str = "mp3_44100_128"
    speed: float = 1.0

    def normalized_text(self) -> str:
        """Normalized string for deterministic caching."""
        return " ".join(self.text.strip().split())


@dataclass
class TTSResponse:
    """Synthesized audio output and timing metadata."""
    audio_bytes: bytes
    duration_sec: float
    words: List[WordTimestamp]
    provider: str
    model_id: str
    voice_id: str
    sample_rate: int = 48000
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_metadata(self) -> Dict[str, Any]:
        """Metadata for cache persistence, strictly excluding API keys/secrets."""
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "voice_id": self.voice_id,
            "duration_sec": round(self.duration_sec, 3),
            "sample_rate": self.sample_rate,
            "word_count": len(self.words),
            "words": [w.to_dict() for w in self.words],
            "extra": self.metadata,
        }


class TTSError(Exception):
    """Base exception for all TTS provider errors."""
    pass


class ConfigurationError(TTSError):
    """Raised when configuration, voice ID, or model ID is invalid or missing."""
    pass


class AuthenticationError(TTSError):
    """Raised when API credentials are missing, unauthorized, or invalid."""
    pass


class RateLimitError(TTSError):
    """Raised when provider rate limits or quotas are exceeded."""
    pass


class SynthesisError(TTSError):
    """Raised when speech generation fails on provider or audio processing."""
    pass


class TTSProvider(ABC):
    """Abstract base class for all TTS providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'elevenlabs', 'qwen3', 'placeholder')."""
        pass

    @abstractmethod
    def validate_configuration(self) -> None:
        """Validate required credentials and settings. Raises ConfigurationError or AuthenticationError."""
        pass

    @abstractmethod
    def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Synthesize a single speech request into WAV audio and word timestamps."""
        pass
