"""Triedenie z cvičení 7, 8 a 9 ÚSaA."""

from __future__ import annotations

from .common import ARRAY_MODES, CHECK_SORTED, GEN_ARRAY, enum

SORT_SIZES = [250, 500, 1000, 2000]

SORTING = {
    "id": "prob_sorting",
    "name": "Triedenie poľa čísel",
    "summary": "Usporiadaj pole celých čísel od najmenšieho po najväčšie.",
    "description": (
        "Úloha z cvičení 7, 8 a 9. Jednoduché metódy (bublinkové triedenie, vkladanie, výber) "
        "majú v priemere O(n²), metódy rozdeľuj a panuj O(n log n). Radix sort čísla "
        "neporovnáva, triedi ich po cifrách a pri ohraničenom rozsahu hodnôt stojí O(n). "
        "Na zoradenom vstupe sa niektoré algoritmy zrýchlia a quicksort s posledným prvkom "
        "ako pivotom sa naopak spomalí na O(n²)."
    ),
    "category": "sorting",
    "input_type": "array",
    "renderer": "array",
    "input_description": "Pole nezáporných celých čísel.",
    "output_description": "Zoradené pole s tými istými prvkami.",
    "tags": ["usaa", "cv7", "cv8", "cv9"],
    "checker": CHECK_SORTED,
    "generators": [{
        "id": "gen_sort", "name": "Pole na triedenie", "code": GEN_ARRAY,
        "description": "Náhodné, zoradené, opačne zoradené, takmer zoradené pole alebo pole s veľa rovnakými hodnotami.",
        "sizes": SORT_SIZES, "viz_size": 14,
        "params": [enum("mode", "Rozloženie hodnôt", ARRAY_MODES, "random")],
    }],
    "algorithms": [
        {
            "id": "alg_bubble", "name": "Bublinkové triedenie",
            "description": "Opakovane porovnáva susedné prvky a vymení ich, ak sú v zlom poradí. Po každom prechode je najväčší prvok na konci.",
            "paradigm": "iterative", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(1)",
            "param": "počet prvkov", "properties": ["stable", "in_place"],
            "code": '''
def solve(data, tracker):
    a = data
    n = len(a)
    for end in range(n - 1, 0, -1):
        for j in range(end):
            tracker.compare(j, j + 1)
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                tracker.swap(j, j + 1)
        tracker.mark_sorted([end])
    tracker.mark_sorted([0])
    return a
''',
        },
        {
            "id": "alg_bubble_flag", "name": "Bublinkové triedenie s ukončením",
            "description": "Ak počas prechodu nenastala žiadna výmena, pole je zoradené a triedenie skončí.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(1)",
            "note": "na zoradenom vstupe stačí jeden prechod", "param": "počet prvkov",
            "properties": ["stable", "in_place", "adaptive"],
            "code": '''
def solve(data, tracker):
    a = data
    n = len(a)
    for end in range(n - 1, 0, -1):
        swapped = False
        for j in range(end):
            tracker.compare(j, j + 1)
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                tracker.swap(j, j + 1)
                swapped = True
        tracker.mark_sorted([end])
        if not swapped:
            tracker.mark_sorted(range(end), label="bez výmeny, pole je zoradené")
            break
    tracker.mark_sorted([0])
    return a
''',
        },
        {
            "id": "alg_insertion", "name": "Triedenie vkladaním",
            "description": "Ľavá časť poľa je zoradená. Ďalší prvok sa posúva doľava, kým nenájde svoje miesto.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(1)",
            "param": "počet prvkov", "properties": ["stable", "in_place", "adaptive"],
            "code": '''
def solve(data, tracker):
    a = data
    for i in range(1, len(a)):
        j = i
        tracker.pointer("i", i)
        while j > 0:
            tracker.compare(j - 1, j)
            if a[j - 1] <= a[j]:
                break
            a[j - 1], a[j] = a[j], a[j - 1]
            tracker.swap(j - 1, j)
            j -= 1
    tracker.pointer("i", None)
    tracker.mark_sorted(range(len(a)), label="pole je zoradené")
    return a
''',
        },
        {
            "id": "alg_selection", "name": "Triedenie výberom",
            "description": "V nezoradenej časti nájde najmenší prvok a vymení ho s prvým prvkom tejto časti.",
            "paradigm": "iterative", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(1)",
            "note": "vždy n(n − 1)/2 porovnaní, najviac n − 1 výmen", "param": "počet prvkov",
            "properties": ["in_place"],
            "code": '''
def solve(data, tracker):
    a = data
    n = len(a)
    for i in range(n - 1):
        m = i
        tracker.pointer("min", m)
        for j in range(i + 1, n):
            tracker.compare(j, m)
            if a[j] < a[m]:
                m = j
                tracker.pointer("min", m)
        if m != i:
            a[i], a[m] = a[m], a[i]
            tracker.swap(i, m)
        tracker.mark_sorted([i])
    tracker.pointer("min", None)
    tracker.mark_sorted(range(n))
    return a
''',
        },
        {
            "id": "alg_merge", "name": "Triedenie zlučovaním (merge sort)",
            "description": "Rozdelí pole na polovice, rekurzívne ich zoradí a zlúči do jedného zoradeného poľa.",
            "paradigm": "divide_and_conquer", "best": "O(n log n)", "avg": "O(n log n)",
            "worst": "O(n log n)", "space": "O(n)", "param": "počet prvkov",
            "properties": ["stable", "recursive"],
            "code": '''
def solve(data, tracker):
    a = data

    def sort(lo, hi):
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid, hi)
        tracker.pointer("lo", lo)
        tracker.pointer("hi", hi - 1)
        merged = []
        i, j = lo, mid
        while i < mid and j < hi:
            tracker.compare(i, j)
            if a[i] <= a[j]:
                merged.append(a[i])
                i += 1
            else:
                merged.append(a[j])
                j += 1
        merged.extend(a[i:mid])
        merged.extend(a[j:hi])
        for k, value in enumerate(merged):
            a[lo + k] = value
            tracker.set(lo + k, value)

    sort(0, len(a))
    tracker.pointer("lo", None)
    tracker.pointer("hi", None)
    tracker.mark_sorted(range(len(a)), label="pole je zoradené")
    return a
''',
        },
        {
            "id": "alg_heap", "name": "Triedenie haldou (heapsort)",
            "description": "Z poľa vytvorí max-haldu. Potom opakovane presunie koreň na koniec a haldu opraví.",
            "paradigm": "data_structure", "best": "O(n log n)", "avg": "O(n log n)",
            "worst": "O(n log n)", "space": "O(1)", "param": "počet prvkov", "properties": ["in_place"],
            "code": '''
def solve(data, tracker):
    a = data
    n = len(a)

    def sift_down(i, size):
        while True:
            big = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < size:
                    tracker.compare(c, big)
                    if a[c] > a[big]:
                        big = c
            if big == i:
                return
            a[i], a[big] = a[big], a[i]
            tracker.swap(i, big)
            i = big

    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        tracker.swap(0, end, label=f"presuň maximum na pozíciu {end}")
        tracker.mark_sorted([end])
        sift_down(0, end)
    tracker.mark_sorted([0])
    return a
''',
        },
        {
            "id": "alg_quick_last", "name": "Quicksort, pivot je posledný prvok",
            "description": "Lomutovo rozdelenie okolo posledného prvku úseku. Na zoradenom vstupe je každé rozdelenie najhoršie možné.",
            "paradigm": "divide_and_conquer", "best": "O(n log n)", "avg": "O(n log n)",
            "worst": "O(n^2)", "space": "O(n)", "note": "najhorší prípad nastane na zoradenom vstupe",
            "param": "počet prvkov", "properties": ["in_place", "recursive"],
            "code": '''
def solve(data, tracker):
    a = data

    def sort(lo, hi):
        if lo >= hi:
            if lo == hi:
                tracker.mark_sorted([lo])
            return
        tracker.pivot(hi)
        p = a[hi]
        i = lo
        for j in range(lo, hi):
            tracker.compare(j, hi)
            if a[j] < p:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    tracker.swap(i, j)
                i += 1
        a[i], a[hi] = a[hi], a[i]
        tracker.swap(i, hi, label=f"pivot {p} na pozíciu {i}")
        tracker.mark_sorted([i])
        sort(lo, i - 1)
        sort(i + 1, hi)

    sort(0, len(a) - 1)
    return a
''',
        },
        {
            "id": "alg_quick_random", "name": "Quicksort, náhodný pivot",
            "description": "Pivot sa vyberie náhodne, preto zoradený vstup nevedie na najhorší prípad.",
            "paradigm": "divide_and_conquer", "best": "O(n log n)", "avg": "O(n log n)",
            "worst": "O(n^2)", "space": "O(log n)", "note": "najhorší prípad je veľmi nepravdepodobný",
            "param": "počet prvkov", "properties": ["in_place", "recursive", "randomized"],
            "code": '''
import random


def solve(data, tracker):
    a = data
    rnd = random.Random(1)

    def sort(lo, hi):
        if lo >= hi:
            if lo == hi:
                tracker.mark_sorted([lo])
            return
        r = rnd.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        tracker.swap(r, hi, label="náhodný pivot presuň na koniec úseku")
        tracker.pivot(hi)
        p = a[hi]
        i = lo
        for j in range(lo, hi):
            tracker.compare(j, hi)
            if a[j] < p:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    tracker.swap(i, j)
                i += 1
        a[i], a[hi] = a[hi], a[i]
        tracker.swap(i, hi, label=f"pivot {p} na pozíciu {i}")
        tracker.mark_sorted([i])
        sort(lo, i - 1)
        sort(i + 1, hi)

    sort(0, len(a) - 1)
    return a
''',
        },
        {
            "id": "alg_radix_array", "name": "Radix sort (LSD, počítanie cifier)",
            "description": "Triedi podľa cifier od najnižšej. Pre každú cifru stabilne rozdelí prvky počítaním výskytov.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "O(d · (n + 10)), d je počet cifier. Generátor dáva hodnoty do 10n, preto d rastie ako log n a meranie ukáže n log n", "param": "počet prvkov",
            "properties": ["stable", "non_comparison"],
            "code": '''
def solve(data, tracker):
    a = data
    if not a:
        return a
    exp = 1
    biggest = max(a)
    while biggest // exp > 0:
        count = [0] * 10
        for x in a:
            count[(x // exp) % 10] += 1
            tracker.count("digit")
        for d in range(1, 10):
            count[d] += count[d - 1]
        out = [0] * len(a)
        for x in reversed(a):
            d = (x // exp) % 10
            count[d] -= 1
            out[count[d]] = x
        for i, x in enumerate(out):
            a[i] = x
            tracker.set(i, x, label=f"rozdelenie podľa cifry {exp}")
        exp *= 10
    tracker.mark_sorted(range(len(a)), label="pole je zoradené")
    return a
''',
        },
        {
            "id": "alg_radix_queues", "name": "Radix sort (LSD, desať frontov)",
            "description": "Verzia z cvičenia 9: prvky sa podľa cifry rozdelia do desiatich frontov a potom sa fronty spoja.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "O(d · n), d je počet cifier. Generátor dáva hodnoty do 10n, preto d rastie ako log n a meranie ukáže n log n", "param": "počet prvkov",
            "properties": ["stable", "non_comparison"],
            "code": '''
from collections import deque


def solve(data, tracker):
    a = data
    if not a:
        return a
    exp = 1
    biggest = max(a)
    while biggest // exp > 0:
        queues = [deque() for _ in range(10)]
        for x in a:
            queues[(x // exp) % 10].append(x)
            tracker.count("enqueue")
        i = 0
        for q in queues:
            while q:
                a[i] = q.popleft()
                tracker.set(i, a[i], label=f"spoj fronty podľa cifry {exp}")
                i += 1
        exp *= 10
    tracker.mark_sorted(range(len(a)), label="pole je zoradené")
    return a
''',
        },
    ],
    "experiments": [
        {
            "id": "exp_sorting_simple", "name": "Jednoduché triedenia oproti merge sortu",
            "algorithms": ["alg_bubble", "alg_bubble_flag", "alg_insertion", "alg_selection", "alg_merge"],
            "generator": "gen_sort", "sizes": SORT_SIZES, "repeats": 3,
            "variants": [
                {"label": "náhodné pole", "params": {"mode": "random"}},
                {"label": "zoradené pole", "params": {"mode": "sorted"}},
                {"label": "opačne zoradené pole", "params": {"mode": "reverse"}},
            ],
        },
        {
            "id": "exp_sorting_quick", "name": "Voľba pivota v quicksorte",
            "algorithms": ["alg_quick_last", "alg_quick_random", "alg_merge", "alg_heap"],
            "generator": "gen_sort", "sizes": SORT_SIZES, "repeats": 3,
            "variants": [
                {"label": "náhodné pole", "params": {"mode": "random"}},
                {"label": "zoradené pole", "params": {"mode": "sorted"}},
            ],
        },
        {
            "id": "exp_sorting_fast", "name": "Rýchle triedenia na väčších poliach",
            "algorithms": ["alg_merge", "alg_heap", "alg_quick_random", "alg_radix_array", "alg_radix_queues"],
            "generator": "gen_sort", "sizes": [5000, 10000, 20000, 40000], "repeats": 3,
        },
    ],
}

GEN_STRINGS = '''
import random

def generate(n, length="variable", alphabet=4, seed=42):
    """n reťazcov z malých písmen. Pri length="fixed" majú všetky dĺžku 8."""
    rnd = random.Random(seed)
    letters = "abcdefghijklmnopqrstuvwxyz"[: max(1, min(26, alphabet))]
    out = []
    for _ in range(n):
        size = 8 if length == "fixed" else rnd.randint(1, 12)
        out.append("".join(rnd.choice(letters) for _ in range(size)))
    return out
'''

STRING_SORT = {
    "id": "prob_string_sort",
    "name": "Triedenie reťazcov",
    "summary": "Usporiadaj zoznam slov lexikograficky, ako v slovníku.",
    "description": (
        "Úloha z cvičenia 9. LSD radix sort triedi podľa znakov od posledného, MSD radix sort "
        "od prvého a rekurzívne v každej skupine. Oba porovnávajú len jednotlivé znaky. "
        "Merge sort porovnáva celé reťazce. Počet krokov radix sortov rastie s dĺžkou slov."
    ),
    "category": "sorting",
    "input_type": "array",
    "renderer": "none",
    "input_description": "Zoznam reťazcov z malých písmen.",
    "output_description": "Lexikograficky zoradený zoznam.",
    "tags": ["usaa", "cv9"],
    "checker": CHECK_SORTED,
    "generators": [{
        "id": "gen_strings", "name": "Zoznam slov", "code": GEN_STRINGS,
        "description": "Náhodné slová s pevnou alebo premenlivou dĺžkou.",
        "sizes": [1000, 2000, 4000, 8000, 16000], "viz_size": 10,
        "params": [enum("length", "Dĺžka slov", {"variable": "1 až 12 znakov", "fixed": "presne 8 znakov"}, "variable")],
    }],
    "algorithms": [
        {
            "id": "alg_str_lsd", "name": "LSD radix sort", "viz": False,
            "description": "Stabilne triedi podľa pozície w − 1, potom w − 2 až po 0. Chýbajúci znak kratšieho slova má najmenšiu hodnotu.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "O(w · n), w je dĺžka najdlhšieho slova", "param": "počet slov",
            "properties": ["stable", "non_comparison"],
            "code": '''
def solve(words, tracker):
    if not words:
        return words
    width = max(len(w) for w in words)
    a = list(words)
    for pos in range(width - 1, -1, -1):
        buckets = [[] for _ in range(27)]
        for w in a:
            tracker.count("char")
            key = ord(w[pos]) - 96 if pos < len(w) else 0
            buckets[key].append(w)
        a = [w for b in buckets for w in b]
    return a
''',
        },
        {
            "id": "alg_str_msd", "name": "MSD radix sort", "viz": False,
            "description": "Rozdelí slová podľa prvého znaku a každú skupinu rekurzívne triedi podľa ďalšieho znaku.",
            "paradigm": "divide_and_conquer", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "O(w · n). Na rozlíšenie n slov treba asi log n znakov, preto meranie ukáže skôr n log n", "param": "počet slov",
            "properties": ["stable", "non_comparison", "recursive"],
            "code": '''
def solve(words, tracker):
    def sort(group, pos):
        if len(group) <= 1:
            return group
        done = []
        buckets = [[] for _ in range(26)]
        for w in group:
            tracker.count("char")
            if pos >= len(w):
                done.append(w)
            else:
                buckets[ord(w[pos]) - 97].append(w)
        out = done
        for b in buckets:
            out.extend(sort(b, pos + 1))
        return out

    return sort(list(words), 0)
''',
        },
        {
            "id": "alg_str_merge", "name": "Merge sort reťazcov", "viz": False,
            "description": "Klasický merge sort, ktorý porovnáva celé reťazce.",
            "paradigm": "divide_and_conquer", "best": "O(n log n)", "avg": "O(n log n)",
            "worst": "O(n log n)", "space": "O(n)", "note": "každé porovnanie stojí až O(w)",
            "param": "počet slov", "properties": ["stable", "recursive"],
            "code": '''
def solve(words, tracker):
    def sort(a):
        if len(a) < 2:
            return a
        mid = len(a) // 2
        left, right = sort(a[:mid]), sort(a[mid:])
        out = []
        i = j = 0
        while i < len(left) and j < len(right):
            tracker.count("compare")
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    return sort(list(words))
''',
        },
    ],
    "experiments": [{
        "id": "exp_string_sort", "name": "Radix sorty oproti merge sortu",
        "algorithms": ["alg_str_lsd", "alg_str_msd", "alg_str_merge"], "generator": "gen_strings",
        "sizes": [1000, 2000, 4000, 8000, 16000], "repeats": 3,
        "variants": [
            {"label": "premenlivá dĺžka", "params": {"length": "variable"}},
            {"label": "pevná dĺžka 8", "params": {"length": "fixed"}},
        ],
    }],
}

PROBLEMS = [SORTING, STRING_SORT]
