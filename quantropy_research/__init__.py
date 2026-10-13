"""Offline research primitives; importing this package starts no services."""

from .covariance import ledoit_wolf_identity, sample_covariance
from .portfolio import ResearchProfile, allocate, compare_policies

__all__ = ["ledoit_wolf_identity", "sample_covariance", "ResearchProfile",
           "allocate", "compare_policies"]
