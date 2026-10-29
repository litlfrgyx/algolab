"""Vstavaný katalóg úloh, algoritmov, generátorov a experimentov.

Poradie: základy, dynamic programming, údajové štruktúry, stromy, triedenie,
grafy, množiny a ďalšie klasické úlohy.
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
