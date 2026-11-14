"""
TTS Provider factory and caching coordinator.
Instantiates providers based on configuration and environment variables,
and coordinates deterministic caching.
"""

import os
from typing import Optional, Dict, Any

from .base import (
    TTSProvider,
    TTSRequest,
    TTSResponse,
    ConfigurationError,
)
from .cache import AudioCacheManager
from .elevenlabs_provider import ElevenLabsProvider, load_env_file_if_needed
from .qwen_provider import Qwen3Provider
from .placeholder_provider import PlaceholderProvider

SUPPORTED_PROVIDERS = {
    "elevenlabs": ElevenLabsProvider,
    "qwen3": Qwen3Provider,
    "placeholder": PlaceholderProvider,
}


def get_tts_provider(
    provider_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> TTSProvider:
    """
    Factory function to obtain a configured TTS provider.
    Resolution order:
      1. provider_name parameter
      2. config["tts"]["provider"]
      3. os.environ["TTS_PROVIDER"]
      4. Default: "elevenlabs"
    """
    load_env_file_if_needed()

    resolved_name = (
        provider_name
        or (config.get("tts", {}).get("provider") if config else None)
        or os.environ.get("TTS_PROVIDER")
        or "elevenlabs"
    ).strip().lower()

    if resolved_name not in SUPPORTED_PROVIDERS:
        raise ConfigurationError(
            f"Unsupported TTS provider: '{resolved_name}'. "
            f"Supported providers: {list(SUPPORTED_PROVIDERS.keys())}."
        )

    cfg_tts = config.get("tts", {}) if config else {}

    if resolved_name == "elevenlabs":
        voice_id = cfg_tts.get("voice_id") or os.environ.get("ELEVENLABS_VOICE_ID")
        model_id = cfg_tts.get("model_id") or os.environ.get("ELEVENLABS_MODEL_ID")
        return ElevenLabsProvider(
            default_voice_id=voice_id,
            default_model_id=model_id,
        )
    elif resolved_name == "qwen3":
        python_bin = cfg_tts.get("python_bin") or os.environ.get("QWEN_TTS_PY")
        return Qwen3Provider(python_bin=python_bin)
    elif resolved_name == "placeholder":
        wps = float(cfg_tts.get("wps", 3.0))
        return PlaceholderProvider(wps=wps)

    raise ConfigurationError(f"Provider '{resolved_name}' failed instantiation.")


def synthesize_with_cache(
    request: TTSRequest,
    provider: TTSProvider,
    cache: Optional[AudioCacheManager] = None,
) -> TTSResponse:
    """
    Synthesizes speech with deterministic disk caching.
    Reuses valid cached audio to prevent repeated API credit consumption.
    """
    if cache is None:
        cache = AudioCacheManager()

    # 1. Attempt cache lookup
    cached_resp = cache.get(request, provider.name)
    if cached_resp is not None:
        return cached_resp

    # 2. Live synthesis on cache miss
    live_resp = provider.synthesize(request)

    # 3. Cache valid response
    cache.put(request, live_resp)

    return live_resp
