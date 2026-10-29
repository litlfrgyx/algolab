"""Kontrakt `tracker` objektu — strana PRODUCENTA krokov vizualizácie.

Toto je rozhranie (Protocol), ktoré dostane používateľský algoritmus ako
druhý parameter: `def solve(data, tracker)`. Reálnu implementáciu poskytne
executor na backende; ten z volaní trackera poskladá schemas.Step objekty
a spočíta operation_counts.

Tento súbor zámerne neobsahuje implementáciu — slúži ako:
  * zmluva medzi autormi algoritmov a systémom,
  * podklad pre šablónu kódu v editore,
  * definícia toho, AKO vznikajú typy krokov a roly zvýraznenia v steps.ts.

Príklad (Bubble Sort s vizualizáciou):

    def solve(data, tracker):
        n = len(data)
        for i in range(n):
            for j in range(n - i - 1):
                tracker.compare(j, j + 1, code_line=4)
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
                    tracker.swap(j, j + 1, code_line=6)
            tracker.mark_sorted([n - i - 1])
        return data

Algoritmus bez `tracker` parametra (`def solve(data)`) je plne platný —
len sa nedá krok-za-krokom vizualizovať (supports_visualization = False),
benchmark však funguje rovnako.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable

# Roly musia zodpovedať HighlightRole v schemas.py / steps.ts
Role = str


@runtime_checkable
class Tracker(Protocol):
    """Rozhranie, na ktoré sa spoliehajú používateľské algoritmy."""

    # --- Generická forma (zodpovedá `tracker.step("compare", {...})` z návrhu) ---
    def step(
        self,
        type: str,
        payload: dict[str, Any] | None = None,
        *,
        label: str | None = None,
        code_line: int | None = None,
    ) -> None:
        """Zaznamená ľubovoľný krok. Snímok stavu doplní executor automaticky."""
        ...

    # --- Pohodlné skratky pre renderer POLE ---
    def compare(self, i: int, j: int, *, code_line: int | None = None) -> None: ...
    def swap(self, i: int, j: int, *, code_line: int | None = None) -> None: ...
    def pivot(self, i: int, *, code_line: int | None = None) -> None: ...
    def highlight(
        self,
        indices: Sequence[int],
        role: Role = "active",
        *,
        code_line: int | None = None,
    ) -> None: ...
    def pointer(self, name: str, index: int) -> None:
        """Pomenovaný ukazovateľ (i, j, lo, hi, mid) zobrazený pod prvkami."""
        ...
    def mark_sorted(self, indices: Sequence[int]) -> None: ...

    # --- Renderer GRID (DP, matice, backtracking) ---
    def set_cell(
        self,
        row: int,
        col: int,
        value: Any,
        *,
        role: Role = "active",
        code_line: int | None = None,
    ) -> None: ...

    # --- Renderer REŤAZEC ---
    def match(self, index: int, *, code_line: int | None = None) -> None: ...

    # --- Explicitný snímok aktuálneho stavu ---
    def snapshot(self, label: str = "", *, code_line: int | None = None) -> None: ...
