"""Data providers — the only network-touching code in the data layer.

Pattern (MASTER_SPEC P5): fetch once → write a snapshot → everything downstream reads
offline from the pinned snapshot. Providers require the ``[data]`` extra.
"""

__all__ = ["use_system_trust"]


def use_system_trust() -> None:
    """Opt in to the OS certificate store for TLS (fixes CERTIFICATE_VERIFY_FAILED).

    On machines where antivirus/corporate middleboxes re-sign TLS, Python's bundled
    certifi CAs can't verify the chain while the OS store can. Call this once before
    fetching. Never disables verification — it only changes *which* trust store
    verifies.
    """
    import truststore  # [data] extra

    truststore.inject_into_ssl()
