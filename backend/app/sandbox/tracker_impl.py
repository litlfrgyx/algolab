"""Konkrétna implementácia `tracker` objektu (producent krokov).

Odovzdáva sa do používateľského `solve(data, tracker)`. Zaznamenáva kroky
ako slovníky v tvare schemas.ArrayStep a počíta operácie. Tým istým objektom
sa pokrýva:
  * vizualizácia (max_steps > 0 → ukladá plné snímky stavu),
  * meranie (max_steps = 0 → iba počíta operácie, žiadne snímky → rýchle).

Výkonová poznámka: konvenčné metódy najprv inkrementujú počítadlo a až POTOM,
ak sa má krok zaznamenať, stavajú label/highlights. V režime merania
(max_steps=0) je teda réžia na jednu operáciu minimálna.

Obmedzenie: snímok stavu = `list(self._data)`, kde `_data` je referencia na
vstup odovzdaný do solve. Funguje pre algoritmy, ktoré menia `data` na mieste
(napr. triedenia). Renderer je zatiaľ 'array'.
"""

from __future__ import annotations

from typing import Any, Sequence

_OPERATION_TYPES = frozenset({"compare", "swap", "pivot"})


class RecordingTracker:
    def __init__(self, max_steps: int) -> None:
        self.max_steps = max_steps
        self.steps: list[dict] = []
        self.counts: dict[str, int] = {}
        self.truncated = False
        self._data: Sequence[Any] = []
        self._pending_pointers: dict[str, int] = {}

    def bind(self, data: Sequence[Any]) -> None:
        """Naviaže referenciu na vstup, ktorý sa snímkuje pri každom kroku."""
        self._data = data

    # -- interné --
    def _count(self, type: str) -> None:
        if type in _OPERATION_TYPES:
            self.counts[type] = self.counts.get(type, 0) + 1

    def _can_record(self) -> bool:
        if len(self.steps) >= self.max_steps:
            self.truncated = True
            return False
        return True

    def _append(
        self,
        type: str,
        label: str,
        highlights: list[dict],
        code_line: int | None,
        pointers: dict[str, int] | None,
    ) -> None:
        merged = dict(self._pending_pointers)
        if pointers:
            merged.update(pointers)
        self._pending_pointers = {}
        step: dict[str, Any] = {
            "kind": "array",
            "index": len(self.steps),
            "type": type,
            "label": label,
            "array": list(self._data),
            "highlights": highlights,
        }
        if code_line is not None:
            step["code_line"] = code_line
        if merged:
            step["pointers"] = merged
        self.steps.append(step)

    # -- generická forma (tracker.step("compare", {...})) --
    def step(
        self,
        type: str,
        payload: dict[str, Any] | None = None,
        *,
        label: str | None = None,
        code_line: int | None = None,
    ) -> None:
        self._count(type)
        if not self._can_record():
            return
        payload = payload or {}
        highlights = [
            {"index": payload[k], "role": "active"}
            for k in ("i", "j")
            if isinstance(payload.get(k), int)
        ]
        self._append(type, label or f"{type} {payload}", highlights, code_line, None)

    # -- pohodlné skratky (pole) --
    def compare(self, i: int, j: int, *, code_line: int | None = None) -> None:
        self._count("compare")
        if not self._can_record():
            return
        self._append(
            "compare",
            f"compare [{i}] vs [{j}]",
            [{"index": i, "role": "compare"}, {"index": j, "role": "compare"}],
            code_line,
            {"i": i, "j": j},
        )

    def swap(self, i: int, j: int, *, code_line: int | None = None) -> None:
        self._count("swap")
        if not self._can_record():
            return
        self._append(
            "swap",
            f"swap [{i}] <-> [{j}]",
            [{"index": i, "role": "swap"}, {"index": j, "role": "swap"}],
            code_line,
            {"i": i, "j": j},
        )

    def pivot(self, i: int, *, code_line: int | None = None) -> None:
        self._count("pivot")
        if not self._can_record():
            return
        self._append("pivot", f"pivot index {i}", [{"index": i, "role": "pivot"}], code_line, None)

    def highlight(
        self, indices: Sequence[int], role: str = "active", *, code_line: int | None = None
    ) -> None:
        if not self._can_record():
            return
        self._append(
            "highlight",
            f"highlight {list(indices)}",
            [{"index": x, "role": role} for x in indices],
            code_line,
            None,
        )

    def pointer(self, name: str, index: int) -> None:
        self._pending_pointers[name] = index

    def mark_sorted(self, indices: Sequence[int]) -> None:
        if not self._can_record():
            return
        self._append(
            "sorted",
            f"{list(indices)} na mieste",
            [{"index": x, "role": "sorted"} for x in indices],
            None,
            None,
        )

    # -- grid / reťazec (zatiaľ minimálne; pripravené pre Fázu 2) --
    def set_cell(
        self, row: int, col: int, value: Any, *, role: str = "active", code_line: int | None = None
    ) -> None:
        if not self._can_record():
            return
        self._append("set", f"cell[{row}][{col}]={value}", [], code_line, None)

    def match(self, index: int, *, code_line: int | None = None) -> None:
        self._count("compare")
        if not self._can_record():
            return
        self._append("match", f"match [{index}]", [{"index": index, "role": "match"}], code_line, None)

    def snapshot(self, label: str = "", *, code_line: int | None = None) -> None:
        if not self._can_record():
            return
        self._append("snapshot", label or "snapshot", [], code_line, None)

    def to_steps(self) -> list[dict]:
        return self.steps
