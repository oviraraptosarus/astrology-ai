"""
ASTROLOGY AI MODES CONTROLLER
=============================
Provides unified switching and configuration access between:
1. `client_safe` (Default for public / client-facing deployment):
   Bounded framing, advisory disclaimers, crisis safety guardrails, vitality brackets.
2. `unconstrained` (For raw offline / Grandmaster execution):
   Unmoderated classical calculations, direct sloka verdicts, exact astronomical windows.
"""

import os
from typing import Union
from .client_safe.config import ClientSafeConfig
from .unconstrained.config import UnconstrainedConfig
from .guardrails import (
    SafetyDecision,
    check_query_safety,
    apply_output_guardrails,
    get_client_disclaimer,
    ADVISORY_DISCLAIMER
)

# Active execution mode state (default configurable via environment variable)
_ACTIVE_MODE = os.getenv("ASTRO_MODE", os.getenv("APP_MODE", "client_safe")).lower()
if _ACTIVE_MODE not in ["client_safe", "unconstrained"]:
    _ACTIVE_MODE = "client_safe"


def get_active_mode() -> str:
    """Return the currently active execution mode name ('client_safe' or 'unconstrained')."""
    global _ACTIVE_MODE
    return _ACTIVE_MODE


def set_active_mode(mode: str) -> str:
    """
    Switch active execution mode.
    Accepted values: 'client_safe', 'unconstrained', 'client', 'raw', 'grandmaster'
    """
    global _ACTIVE_MODE
    m = mode.lower().strip()
    if m in ["client_safe", "client", "safe", "bounded"]:
        _ACTIVE_MODE = "client_safe"
    elif m in ["unconstrained", "raw", "grandmaster", "unfiltered"]:
        _ACTIVE_MODE = "unconstrained"
    else:
        raise ValueError(f"Unknown mode '{mode}'. Choose 'client_safe' or 'unconstrained'.")
    return _ACTIVE_MODE


def get_mode_config() -> Union[ClientSafeConfig, UnconstrainedConfig]:
    """Return the active configuration class for the current mode."""
    mode = get_active_mode()
    if mode == "unconstrained":
        return UnconstrainedConfig
    return ClientSafeConfig


def is_client_safe() -> bool:
    """Return True if currently operating under client-safe guardrails."""
    return get_active_mode() == "client_safe"


def is_unconstrained() -> bool:
    """Return True if currently operating in unconstrained mode."""
    return get_active_mode() == "unconstrained"


__all__ = [
    "get_active_mode",
    "set_active_mode",
    "get_mode_config",
    "is_client_safe",
    "is_unconstrained",
    "ClientSafeConfig",
    "UnconstrainedConfig",
    "SafetyDecision",
    "check_query_safety",
    "apply_output_guardrails",
    "get_client_disclaimer",
    "ADVISORY_DISCLAIMER"
]
