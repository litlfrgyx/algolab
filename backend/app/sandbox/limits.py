"""Limity zdrojov pre sandbox proces.

`resource.setrlimit` je dostupné len na POSIX (Linux/macOS). Na Windows sa
ticho preskočí — preto je primárnou izoláciou Docker (Linux kontajner), kde
limity reálne platia. Na Windows pri vývoji slúži ako ochrana iba timeout.
"""

from __future__ import annotations


def apply_limits(cpu_seconds: int, memory_bytes: int) -> bool:
    """Nastaví CPU a pamäťový limit v aktuálnom procese. Vráti True ak sa podarilo."""
    try:
        import resource  # iba POSIX
    except ImportError:
        return False

    applied = False
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        applied = True
    except (ValueError, OSError):
        pass
    try:
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        applied = True
    except (ValueError, OSError):
        pass
    return applied
