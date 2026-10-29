"""Vstavaný katalóg úloh, algoritmov, generátorov a experimentov.

Poradie zodpovedá približne poradiu tém v predmete Údajové štruktúry
a algoritmy (ÚSaA) na KPI FEI TUKE, za nimi nasledujú úlohy mimo predmetu.
"""

from __future__ import annotations

from . import basics, dp, extra, graphs, sets, sorting, structures, trees

CATALOG: list[dict] = [
    *basics.PROBLEMS,
    *dp.PROBLEMS,
    *structures.PROBLEMS,
    *trees.PROBLEMS,
    *sorting.PROBLEMS,
    *graphs.PROBLEMS,
    *sets.PROBLEMS,
    *extra.PROBLEMS,
]
