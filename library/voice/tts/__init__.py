"""
Papercraft Content Factory TTS Package.
Exports provider interfaces, caching, and factory functions.
"""

from .base import (
    TTSProvider,
    TTSRequest,
    TTSResponse,
    WordTimestamp,
    TTSError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    SynthesisError,
)
from .cache import AudioCacheManager
from .elevenlabs_provider import ElevenLabsProvider
from .qwen_provider import Qwen3Provider
from .placeholder_provider import PlaceholderProvider
from .factory import get_tts_provider, synthesize_with_cache

__all__ = [
    "TTSProvider",
    "TTSRequest",
    "TTSResponse",
    "WordTimestamp",
    "TTSError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "SynthesisError",
    "AudioCacheManager",
    "ElevenLabsProvider",
    "Qwen3Provider",
    "PlaceholderProvider",
    "get_tts_provider",
    "synthesize_with_cache",
]
