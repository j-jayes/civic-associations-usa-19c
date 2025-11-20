"""Verification module for checking extraction quality."""

from .similarity import compute_similarity
from .rules import verify_record

__all__ = [
    "compute_similarity",
    "verify_record",
]
