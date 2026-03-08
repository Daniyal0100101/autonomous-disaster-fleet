"""
conftest.py — stub out the google-genai SDK before any backend module is imported.

The google-genai package depends on the `cryptography` C extension which is
broken in this environment. Since ai_decision.py imports it at module level,
we install a lightweight mock into sys.modules before the first import of main.
"""
import sys
import types
from unittest.mock import MagicMock

# Build a minimal fake package hierarchy so `from google import genai` works.
_google = types.ModuleType("google")
_genai = types.ModuleType("google.genai")
_google.genai = _genai
sys.modules.setdefault("google", _google)
sys.modules.setdefault("google.genai", _genai)

# The ai_decision module calls `genai.Client(api_key=...)`. Stub it out.
_genai.Client = MagicMock()
