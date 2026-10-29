"""Implementácia objektu `tracker`, ktorý dostáva funkcia solve(data, tracker).

Jeden objekt slúži na dve veci naraz:
  * meranie: počíta operácie (porovnania, výmeny, návštevy vrcholov...). Tento
    počet nezávisí od rýchlosti počítača ani od jazyka.
  * vizualizácia: ak je max_steps > 0, po každej udalosti uloží snímok stavu,
    ktorý frontend prehrá krok za krokom.

V režime merania (max_steps = 0) sa po zvýšení počítadla metóda hneď vráti,
takže réžia na jednu operáciu je malá.

Podporované vykresľovače (renderer):
  array  pole čísel (triedenie, vyhľadávanie, halda, tabuľka DP v jednom riadku)
  grid   dvojrozmerná tabuľka (dynamické programovanie)
  graph  graf s vrcholmi a hranami
  tree   strom (binárny alebo s viacerými kľúčmi v uzle)
  string text a posúvaná vzorka
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

# Udalosti, ktoré sa iba zobrazujú a nepočítajú sa ako operácia algoritmu.
VISUAL_ONLY = frozenset(
    {"highlight", "sorted", "snapshot", "structure", "focus", "shift", "found", "label"}
)


def _num(x: Any) -> Any:
    """Hodnota do snímku: čísla a reťazce nechá, ostatné prevedie na text."""
    if x is None or isinstance(x, (int, float, str, bool)):
        return x
    return str(x)


class RecordingTracker:
    def __init__(self, max_steps: int, data: Any = None) -> None:
        self.max_steps = max_steps
        self.recording = max_steps > 0
        self.steps: list[dict] = []
        self.counts: dict[str, int] = {}
        self.truncated = False
        self.renderer: str | None = None
        self.structure: dict | None = None

        # pole
        self._array: list | None = data if isinstance(data, list) and _flat_numbers(data) else None
        self._array_labels: list[str] | None = None
        self._pointers: dict[str, int] = {}
        self._sorted: set[int] = set()
        # tabuľka
        self._grid: list[list[Any]] | None = None
        self._row_labels: list[str] | None = None
        self._col_labels: list[str] | None = None
        # graf
        self._node_roles: dict[int, str] = {}
        self._edge_roles: dict[tuple[int, int], str] = {}
        self._labels: dict[int, str] = {}
        self._frontier: dict | None = None
        # strom
        self._tree_nodes: list[dict] = []
        self._tree_root: Any = None
        self._tree_roles: dict[Any, str] = {}
        # reťazec
        self._text: str | None = None
        self._pattern: str | None = None
        self._offset = 0
        self._found: set[int] = set()

        # dočasné zvýraznenia, ktoré sa zobrazia v najbližšom kroku
        self._pending: list[tuple[str, Any, str]] = []

    # ------------------------------------------------------------------
    #  Počítanie a záznam krokov
    # ------------------------------------------------------------------
    def count(self, name: str, k: int = 1) -> None:
        """Zvýši počítadlo operácie bez záznamu kroku (lacné meranie)."""
        c = self.counts
        c[name] = c.get(name, 0) + k

    def _can_record(self) -> bool:
        if not self.recording:
            return False
        if len(self.steps) >= self.max_steps:
            self.truncated = True
            return False
        return True

    def _emit(
        self,
        type: str,
        label: str,
        transient: Iterable[tuple[str, Any, str]] = (),
        code_line: int | None = None,
    ) -> None:
        transient = list(self._pending) + list(transient)
        self._pending = []
        kind = self.renderer or ("array" if self._array is not None else "none")
        step: dict[str, Any] = {"kind": kind, "index": len(self.steps), "type": type, "label": label}
        if code_line is not None:
            step["code_line"] = code_line

        if kind == "array":
            arr = self._array if self._array is not None else []
            roles = {i: "sorted" for i in self._sorted}
            for target, key, role in transient:
                if target == "a":
                    roles[key] = role
            step["array"] = [_num(x) for x in arr]
            step["highlights"] = [{"index": i, "role": r} for i, r in sorted(roles.items())]
            if self._pointers:
                step["pointers"] = dict(self._pointers)
            if self._array_labels:
                step["labels"] = list(self._array_labels)
        elif kind == "grid":
            grid = self._grid or []
            step["grid"] = [[_num(c) for c in row] for row in grid]
            step["highlights"] = [
                {"row": key[0], "col": key[1], "role": role}
                for target, key, role in transient
                if target == "g"
            ]
            if self._row_labels:
                step["row_labels"] = self._row_labels
            if self._col_labels:
                step["col_labels"] = self._col_labels
        elif kind == "graph":
            nodes = dict(self._node_roles)
            edges = dict(self._edge_roles)
            for target, key, role in transient:
                if target == "n":
                    nodes[key] = role
                elif target == "e":
                    edges[key] = role
            step["node_roles"] = {str(k): v for k, v in nodes.items()}
            step["edge_roles"] = [{"u": u, "v": v, "role": r} for (u, v), r in edges.items()]
            if self._labels:
                step["labels"] = {str(k): v for k, v in self._labels.items()}
            if self._frontier is not None:
                step["frontier"] = dict(self._frontier)
        elif kind == "tree":
            roles = dict(self._tree_roles)
            for target, key, role in transient:
                if target == "t":
                    roles[key] = role
            step["nodes"] = [dict(n) for n in self._tree_nodes]
            step["root"] = self._tree_root
            step["highlights"] = [{"id": k, "role": r} for k, r in roles.items()]
        elif kind == "string":
            text_roles = {i: "sorted" for i in self._found}
            pat_roles: dict[int, str] = {}
            for target, key, role in transient:
                if target == "s":
                    text_roles[key] = role
                elif target == "p":
                    pat_roles[key] = role
            step["value"] = self._text or ""
            step["pattern"] = self._pattern
            step["offset"] = self._offset
            step["highlights"] = [{"index": i, "role": r} for i, r in sorted(text_roles.items())]
            step["pattern_highlights"] = [{"index": i, "role": r} for i, r in sorted(pat_roles.items())]
        self.steps.append(step)

    # ------------------------------------------------------------------
    #  Všeobecné metódy
    # ------------------------------------------------------------------
    def step(
        self,
        type: str,
        payload: dict[str, Any] | None = None,
        *,
        label: str | None = None,
        code_line: int | None = None,
    ) -> None:
        """Ľubovoľná udalosť. Počíta sa, ak nejde o čisto zobrazovaciu udalosť."""
        if type not in VISUAL_ONLY:
            self.count(type)
        if not self._can_record():
            return
        payload = payload or {}
        transient = [("a", payload[k], "active") for k in ("i", "j") if isinstance(payload.get(k), int)]
        self._emit(type, label or type, transient, code_line)

    def snapshot(self, label: str = "", *, code_line: int | None = None) -> None:
        if self._can_record():
            self._emit("snapshot", label or "stav", (), code_line)

    def highlight(
        self, indices: Sequence[int], role: str = "active", *, label: str | None = None,
        code_line: int | None = None,
    ) -> None:
        if self.recording and self._can_record():
            self._emit("highlight", label or f"zvýrazni {list(indices)}",
                       [("a", i, role) for i in indices], code_line)

    def pointer(self, name: str, index: int | None) -> None:
        """Pomenovaný ukazovateľ pod prvkom poľa (i, j, lo, hi, mid). None ho skryje."""
        if index is None:
            self._pointers.pop(name, None)
        else:
            self._pointers[name] = index

    # ------------------------------------------------------------------
    #  Pole
    # ------------------------------------------------------------------
    def array(self, values: list, labels: Sequence[str] | None = None) -> None:
        """Naviaže iné pole na vykresľovanie (napr. tabuľku DP alebo haldu)."""
        self.renderer = "array"
        self._array = values
        self._array_labels = list(labels) if labels else None
        self._sorted = set()

    def compare(self, i: int, j: int, *, label: str | None = None, code_line: int | None = None) -> None:
        c = self.counts
        c["compare"] = c.get("compare", 0) + 1
        if self.recording and self._can_record():
            self._emit("compare", label or f"porovnaj [{i}] a [{j}]",
                       [("a", i, "compare"), ("a", j, "compare")], code_line)

    def swap(self, i: int, j: int, *, label: str | None = None, code_line: int | None = None) -> None:
        c = self.counts
        c["swap"] = c.get("swap", 0) + 1
        if self.recording and self._can_record():
            self._emit("swap", label or f"vymeň [{i}] a [{j}]",
                       [("a", i, "swap"), ("a", j, "swap")], code_line)

    def set(self, i: int, value: Any = None, *, label: str | None = None, code_line: int | None = None) -> None:
        """Zápis do poľa (pole už algoritmus zmenil, tu sa len zaznamená)."""
        c = self.counts
        c["set"] = c.get("set", 0) + 1
        if self.recording and self._can_record():
            shown = value if value is not None else (self._array[i] if self._array else "")
            self._emit("set", label or f"zapíš {shown} na [{i}]", [("a", i, "swap")], code_line)

    def pivot(self, i: int, *, label: str | None = None, code_line: int | None = None) -> None:
        c = self.counts
        c["pivot"] = c.get("pivot", 0) + 1
        if self.recording and self._can_record():
            self._emit("pivot", label or f"pivot je [{i}]", [("a", i, "pivot")], code_line)

    def mark_sorted(self, indices: Sequence[int], *, label: str | None = None) -> None:
        self._sorted.update(indices)
        if self._can_record():
            self._emit("sorted", label or f"{list(indices)} je na správnom mieste")

    def unmark_sorted(self) -> None:
        self._sorted = set()

    # ------------------------------------------------------------------
    #  Tabuľka (dynamické programovanie)
    # ------------------------------------------------------------------
    def grid(
        self, rows: int, cols: int, *, row_labels: Sequence[Any] | None = None,
        col_labels: Sequence[Any] | None = None, fill: Any = None,
    ) -> None:
        self.renderer = "grid"
        self._grid = [[fill for _ in range(cols)] for _ in range(rows)]
        self._row_labels = [str(x) for x in row_labels] if row_labels is not None else None
        self._col_labels = [str(x) for x in col_labels] if col_labels is not None else None

    def set_cell(
        self, row: int, col: int, value: Any, *, role: str = "active", label: str | None = None,
        code_line: int | None = None,
    ) -> None:
        self.count("cell")
        if self._grid is not None and 0 <= row < len(self._grid) and 0 <= col < len(self._grid[row]):
            self._grid[row][col] = value
        if self._can_record():
            self._emit("cell", label or f"T[{row}][{col}] = {value}", [("g", (row, col), role)], code_line)

    def read_cell(self, row: int, col: int) -> None:
        """Označí bunku, z ktorej sa počíta, zobrazí sa v najbližšom kroku."""
        if self.recording:
            self._pending.append(("g", (row, col), "compare"))

    # ------------------------------------------------------------------
    #  Graf
    # ------------------------------------------------------------------
    def graph(self, n: int, edges: Iterable[Sequence[Any]], *, directed: bool = False,
              weighted: bool = False) -> None:
        self.renderer = "graph"
        self.structure = {
            "type": "graph",
            "n": n,
            "edges": [list(e) for e in edges],
            "directed": directed,
            "weighted": weighted,
        }

    def _ekey(self, u: int, v: int) -> tuple[int, int]:
        directed = bool(self.structure and self.structure.get("directed"))
        return (u, v) if directed or u <= v else (v, u)

    def visit(self, v: int, *, label: str | None = None, code_line: int | None = None) -> None:
        self.count("visit")
        self._node_roles[v] = "visited"
        if self._can_record():
            self._emit("visit", label or f"navštív vrchol {v}", [("n", v, "active")], code_line)

    def edge(self, u: int, v: int, role: str = "compare", *, label: str | None = None,
             code_line: int | None = None) -> None:
        """Preskúmanie hrany. Roly 'tree' a 'path' zostanú zvýraznené natrvalo."""
        self.count("edge")
        key = self._ekey(u, v)
        if role in ("tree", "path", "sorted"):
            self._edge_roles[key] = role
        if self._can_record():
            self._emit("edge", label or f"hrana {u} → {v}", [("e", key, role)], code_line)

    def relax(self, u: int, v: int, new_value: Any = None, *, label: str | None = None,
              code_line: int | None = None) -> None:
        self.count("relax")
        if new_value is not None:
            self._labels[v] = str(new_value)
        if self._can_record():
            text = label or (f"uvoľni {u} → {v}: d[{v}] = {new_value}" if new_value is not None
                             else f"uvoľni {u} → {v}")
            self._emit("relax", text, [("e", self._ekey(u, v), "compare"), ("n", v, "compare")], code_line)

    def node_label(self, v: int, text: Any) -> None:
        self._labels[v] = str(text)

    def node_role(self, v: int, role: str | None) -> None:
        if role is None:
            self._node_roles.pop(v, None)
        else:
            self._node_roles[v] = role

    def frontier(self, items: Iterable[Any], name: str = "front") -> None:
        """Obsah frontu alebo zásobníka, ktorý sa zobrazí pod grafom.

        Pri meraní (bez záznamu krokov) sa obsah nekopíruje, inak by každé volanie stálo O(n).
        """
        if not self.recording:
            return
        self._frontier = {"name": name, "items": [_num(x) for x in items]}

    # ------------------------------------------------------------------
    #  Strom
    # ------------------------------------------------------------------
    def tree_arrays(self, values: Sequence[Any], left: Sequence[int], right: Sequence[int],
                    root: int, *, label: str | None = None, code_line: int | None = None) -> None:
        """Strom v reprezentácii z cvičenia 6 ÚSaA: indexy potomkov, 0 = prázdny podstrom."""
        self.renderer = "tree"
        if not self.recording:
            return
        nodes = []
        for i in range(1, len(values)):
            if values[i] is None:
                continue
            nodes.append({
                "id": i,
                "label": str(values[i]),
                "children": [left[i] or None, right[i] or None],
            })
        self._tree_nodes = nodes
        self._tree_root = root or None
        if label is not None and self._can_record():
            self._emit("structure", label, (), code_line)

    def tree(self, root: Any, *, label: str | None = None, extra: str | None = None,
             code_line: int | None = None) -> None:
        """Snímok stromu z objektov alebo slovníkov.

        Binárny uzol má atribúty (alebo kľúče) key, left, right.
        Uzol s viacerými kľúčmi (2-3 strom) má keys a children.
        Identifikátorom uzla je jeho kľúč, aby sa uzol pri rotácii plynulo presunul.
        """
        self.renderer = "tree"
        if not (self.recording and self._can_record()):
            return  # pri meraní sa snímok stromu nepočíta, inak by každá operácia stála O(n)
        nodes: list[dict] = []

        def get(obj: Any, name: str) -> Any:
            if isinstance(obj, dict):
                return obj.get(name)
            return getattr(obj, name, None)

        def walk(node: Any) -> Any:
            if node is None:
                return None
            keys = get(node, "keys")
            if keys is not None:
                node_id = "|".join(str(k) for k in keys)
                children = [walk(c) for c in (get(node, "children") or [])]
                entry = {"id": node_id, "label": " | ".join(str(k) for k in keys), "children": children}
            else:
                key = get(node, "key")
                if key is None:
                    key = get(node, "value")
                node_id = key
                entry = {"id": node_id, "label": str(key),
                         "children": [walk(get(node, "left")), walk(get(node, "right"))]}
            if extra is not None:
                value = get(node, extra)
                if value is not None:
                    entry["extra"] = str(value)
            nodes.append(entry)
            return node_id

        self._tree_root = walk(root)
        self._tree_nodes = nodes
        if label is not None:
            self._emit("structure", label, (), code_line)

    def focus(self, node_id: Any, role: str = "active", *, label: str | None = None,
              code_line: int | None = None) -> None:
        """Zvýrazní uzol stromu (napr. pri porovnaní kľúča)."""
        if self._can_record():
            self._emit("focus", label or f"uzol {node_id}", [("t", node_id, role)], code_line)

    def mark_node(self, node_id: Any, role: str | None = "visited") -> None:
        if role is None:
            self._tree_roles.pop(node_id, None)
        else:
            self._tree_roles[node_id] = role

    def clear_marks(self) -> None:
        self._tree_roles = {}

    # ------------------------------------------------------------------
    #  Reťazec
    # ------------------------------------------------------------------
    def string(self, text: str, pattern: str | None = None) -> None:
        self.renderer = "string"
        self._text = text
        self._pattern = pattern
        self._offset = 0
        self._found = set()

    def match(self, i: int, j: int | None = None, *, label: str | None = None,
              code_line: int | None = None) -> None:
        c = self.counts
        c["compare"] = c.get("compare", 0) + 1
        if self.recording and self._can_record():
            tr = [("s", i, "match")]
            if j is not None:
                tr.append(("p", j, "match"))
            self._emit("match", label or f"zhoda na pozícii {i}", tr, code_line)

    def mismatch(self, i: int, j: int | None = None, *, label: str | None = None,
                 code_line: int | None = None) -> None:
        c = self.counts
        c["compare"] = c.get("compare", 0) + 1
        if self.recording and self._can_record():
            tr = [("s", i, "swap")]
            if j is not None:
                tr.append(("p", j, "swap"))
            self._emit("mismatch", label or f"nezhoda na pozícii {i}", tr, code_line)

    def shift(self, offset: int, *, label: str | None = None, code_line: int | None = None) -> None:
        self._offset = offset
        if self._can_record():
            self._emit("shift", label or f"posuň vzorku na pozíciu {offset}", (), code_line)

    def found(self, start: int, length: int | None = None, *, label: str | None = None) -> None:
        m = length if length is not None else len(self._pattern or "")
        self._found.update(range(start, start + m))
        if self._can_record():
            self._emit("found", label or f"výskyt na pozícii {start}")

    # ------------------------------------------------------------------
    def to_steps(self) -> list[dict]:
        return self.steps

    def operation_counts(self) -> dict[str, int]:
        counts = dict(self.counts)
        counts["total"] = sum(self.counts.values())
        return counts


def _flat_numbers(data: list) -> bool:
    """Pole sa vykresľuje automaticky len vtedy, ak obsahuje čísla."""
    return all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in data[:50])
