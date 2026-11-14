"""
Package exporting the full 20-environment specification collection.
"""

from typing import List, Dict, Any
from .specs_01_05 import SPECS_01_05
from .specs_06_10 import SPECS_06_10
from .specs_11_15 import SPECS_11_15
from .specs_16_20 import SPECS_16_20

ENV_SPECS: List[Dict[str, Any]] = (
    SPECS_01_05 +
    SPECS_06_10 +
    SPECS_11_15 +
    SPECS_16_20
)

__all__ = ["ENV_SPECS"]
