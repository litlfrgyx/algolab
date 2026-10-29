"""Spoločné časti katalógu: generátory a popisy parametrov."""

from __future__ import annotations


def enum(name: str, label: str, options: dict[str, str], default: str) -> dict:
    return {"name": name, "label": label, "type": "enum", "options": list(options),
            "option_labels": options, "default": default}


def number(name: str, label: str, default: int) -> dict:
    return {"name": name, "label": label, "type": "number", "default": default}


ARRAY_MODES = {
    "random": "náhodné poradie",
    "sorted": "už zoradené",
    "reverse": "opačne zoradené",
    "nearly_sorted": "takmer zoradené",
    "few_unique": "veľa rovnakých hodnôt",
}

GEN_ARRAY = '''
import random

def generate(n, mode="random", seed=42):
    """Pole n celých čísel s danou vlastnosťou."""
    rnd = random.Random(seed)
    if mode == "few_unique":
        data = [rnd.randint(1, 5) for _ in range(n)]
    else:
        data = [rnd.randint(1, 99) if n <= 60 else rnd.randint(0, 10 * n) for _ in range(n)]
    if mode == "sorted":
        data.sort()
    elif mode == "reverse":
        data.sort(reverse=True)
    elif mode == "nearly_sorted":
        data.sort()
        for _ in range(max(1, n // 20)):
            i, j = rnd.randrange(n), rnd.randrange(n)
            data[i], data[j] = data[j], data[i]
    return data
'''

GEN_NUMBER = '''
def generate(n, seed=0):
    """Vstupom je samotné číslo n."""
    return n
'''

GRAPH_KINDS = {
    "sparse": "riedky (asi 3 hrany na vrchol)",
    "dense": "hustý (asi 10 % všetkých dvojíc)",
    "grid": "mriežka",
    "path": "cesta (reťaz vrcholov)",
    "disconnected": "viac komponentov",
}

GEN_GRAPH = '''
import random

def generate(n, kind="sparse", seed=42, weighted=False, max_weight=20):
    """Neorientovaný graf s n vrcholmi 0 .. n-1.

    Výsledok: {"n": n, "edges": [[u, v] alebo [u, v, w]], "start": 0}
    """
    rnd = random.Random(seed)
    edges = set()

    def add(u, v):
        if u != v:
            edges.add((min(u, v), max(u, v)))

    if kind == "grid":
        side = max(1, int(n ** 0.5))
        n = side * side
        for r in range(side):
            for c in range(side):
                v = r * side + c
                if c + 1 < side:
                    add(v, v + 1)
                if r + 1 < side:
                    add(v, v + side)
    elif kind == "path":
        for v in range(1, n):
            add(v - 1, v)
    else:
        parts = 3 if kind == "disconnected" and n >= 6 else 1
        size = n // parts
        for p in range(parts):
            lo = p * size
            hi = n if p == parts - 1 else lo + size
            for v in range(lo + 1, hi):
                add(rnd.randrange(lo, v), v)  # náhodný strom zaručí súvislosť komponentu
            span = hi - lo
            if kind == "dense":
                extra = int(0.1 * span * (span - 1) / 2)
            else:
                extra = 2 * span
            for _ in range(extra):
                add(rnd.randrange(lo, hi), rnd.randrange(lo, hi))
    out = []
    for u, v in sorted(edges):
        out.append([u, v, rnd.randint(1, max_weight)] if weighted else [u, v])
    return {"n": n, "edges": out, "start": 0}
'''

GEN_TREE = '''
import random

def generate(n, shape="random", seed=42):
    """Binárny strom s n uzlami uložený v troch poliach.

    values[i] je hodnota uzla i, left[i] a right[i] sú indexy potomkov,
    0 znamená prázdny podstrom. Index 0 sa nepoužíva, koreň je uzol 1.
    """
    rnd = random.Random(seed)
    n = max(1, n)
    values = [None] + [rnd.randint(1, 99) for _ in range(n)]
    left = [0] * (n + 1)
    right = [0] * (n + 1)
    if shape == "balanced":
        for i in range(1, n + 1):
            if 2 * i <= n:
                left[i] = 2 * i
            if 2 * i + 1 <= n:
                right[i] = 2 * i + 1
    elif shape == "degenerate":
        for i in range(1, n):
            if rnd.random() < 0.5:
                left[i] = i + 1
            else:
                right[i] = i + 1
    else:
        for i in range(2, n + 1):
            while True:
                parent = rnd.randrange(1, i)
                side = rnd.choice((left, right))
                if side[parent] == 0:
                    side[parent] = i
                    break
    return {"values": values, "left": left, "right": right, "root": 1}
'''

TREE_SHAPES = {"random": "náhodný tvar", "balanced": "vyvážený", "degenerate": "zdegenerovaný (reťaz)"}

CHECK_SORTED = '''
def check(input, output, expected=None):
    """Výstup musí byť zoradený a obsahovať presne tie isté prvky ako vstup."""
    if not isinstance(output, list):
        return False, "Výstup nie je zoznam"
    if len(output) != len(input):
        return False, f"Výstup má {len(output)} prvkov, vstup {len(input)}"
    target = sorted(input)
    if output == target:
        return True
    for i, (a, b) in enumerate(zip(output, target)):
        if a != b:
            return False, f"Prvý rozdiel na indexe {i}: {a} namiesto {b}"
    return False, "Výstup nie je zoradený"
'''
