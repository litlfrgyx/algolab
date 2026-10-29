"""Základné úlohy z cvičení 1, 2 a 8 ÚSaA: maximum a minimum, súčet, faktoriál, mocnina."""

from __future__ import annotations

from .common import ARRAY_MODES, GEN_ARRAY, GEN_NUMBER, enum

MAXMIN = {
    "id": "prob_maxmin",
    "name": "Maximum a minimum poľa",
    "summary": "Nájdi najmenší a najväčší prvok poľa s čo najmenej porovnaniami.",
    "description": (
        "Úloha z cvičení 1 a 8. Všetky algoritmy majú lineárnu zložitosť, líšia sa však "
        "konštantou, teda počtom porovnaní. Naivný prechod potrebuje 2n − 2 porovnaní, "
        "MAXMIN metódou rozdeľuj a panuj 3n/2 − 2. Rozdiel ukáže počítadlo operácií."
    ),
    "category": "divide_and_conquer",
    "input_type": "array",
    "renderer": "array",
    "input_description": "Pole celých čísel, aspoň jeden prvok.",
    "output_description": "Dvojica [minimum, maximum].",
    "tags": ["usaa", "cv1", "cv8"],
    "checker": '''
def check(input, output, expected=None):
    want = [min(input), max(input)]
    if list(output) == want:
        return True
    return False, f"Výsledok {output}, správne je {want}"
''',
    "generators": [{
        "id": "gen_maxmin", "name": "Pole celých čísel", "code": GEN_ARRAY,
        "description": "Náhodné pole, voliteľne zoradené alebo opačne zoradené.",
        "sizes": [1000, 5000, 20000, 50000, 100000], "viz_size": 12,
        "params": [enum("mode", "Rozloženie hodnôt", {k: ARRAY_MODES[k] for k in ("random", "sorted", "reverse")}, "random")],
    }],
    "algorithms": [
        {
            "id": "alg_maxmin_naive", "name": "Naivný prechod",
            "description": "Každý prvok sa porovná s doterajším maximom aj minimom.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "presne 2n − 2 porovnaní", "param": "počet prvkov",
            "code": '''
def solve(data, tracker):
    imin = imax = 0
    tracker.pointer("min", 0)
    tracker.pointer("max", 0)
    for i in range(1, len(data)):
        tracker.compare(i, imax)
        if data[i] > data[imax]:
            imax = i
            tracker.pointer("max", imax)
        tracker.compare(i, imin)
        if data[i] < data[imin]:
            imin = i
            tracker.pointer("min", imin)
    return [data[imin], data[imax]]
''',
        },
        {
            "id": "alg_maxmin_dc", "name": "MAXMIN (rozdeľuj a panuj)",
            "description": "Pole sa rozdelí na polovice, v každej sa rekurzívne nájde minimum a maximum a výsledky sa spoja dvoma porovnaniami.",
            "paradigm": "divide_and_conquer", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(log n)",
            "note": "3n/2 − 2 porovnaní pre n mocninu dvoch", "param": "počet prvkov", "properties": ["recursive"],
            "code": '''
def solve(data, tracker):
    def maxmin(lo, hi):
        # vráti indexy (minimum, maximum) v úseku data[lo..hi]
        tracker.pointer("lo", lo)
        tracker.pointer("hi", hi)
        if lo == hi:
            return lo, lo
        if hi == lo + 1:
            tracker.compare(lo, hi)
            if data[lo] < data[hi]:
                return lo, hi
            return hi, lo
        mid = (lo + hi) // 2
        min1, max1 = maxmin(lo, mid)
        min2, max2 = maxmin(mid + 1, hi)
        tracker.compare(min1, min2)
        mn = min1 if data[min1] <= data[min2] else min2
        tracker.compare(max1, max2)
        mx = max1 if data[max1] >= data[max2] else max2
        return mn, mx

    imin, imax = maxmin(0, len(data) - 1)
    tracker.pointer("lo", None)
    tracker.pointer("hi", None)
    tracker.highlight([imin, imax], "match", label="nájdené minimum a maximum")
    return [data[imin], data[imax]]
''',
        },
        {
            "id": "alg_maxmin_pairs", "name": "Prechod po dvojiciach",
            "description": "Prvky sa spracúvajú po dvojiciach: najprv sa porovnajú navzájom, menší sa porovná s minimom a väčší s maximom.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "približne 3n/2 porovnaní", "param": "počet prvkov",
            "code": '''
def solve(data, tracker):
    n = len(data)
    if n % 2 == 1:
        imin = imax = 0
        start = 1
    else:
        tracker.compare(0, 1)
        imin, imax = (0, 1) if data[0] <= data[1] else (1, 0)
        start = 2
    for i in range(start, n - 1, 2):
        tracker.compare(i, i + 1)
        small, big = (i, i + 1) if data[i] <= data[i + 1] else (i + 1, i)
        tracker.compare(small, imin)
        if data[small] < data[imin]:
            imin = small
        tracker.compare(big, imax)
        if data[big] > data[imax]:
            imax = big
        tracker.pointer("min", imin)
        tracker.pointer("max", imax)
    return [data[imin], data[imax]]
''',
        },
    ],
    "experiments": [{
        "id": "exp_maxmin", "name": "Počet porovnaní pri hľadaní minima a maxima",
        "algorithms": ["alg_maxmin_naive", "alg_maxmin_dc", "alg_maxmin_pairs"],
        "generator": "gen_maxmin", "sizes": [1000, 4000, 16000, 64000], "repeats": 3,
        "variants": [{"label": "náhodné pole", "params": {"mode": "random"}}],
    }],
}

SUM = {
    "id": "prob_sum",
    "name": "Súčet 1 + 2 + … + n",
    "summary": "Sčítaj čísla od 1 po n. Cyklom, alebo jediným vzorcom?",
    "description": (
        "Úloha z cvičenia 2, kde sa na nej vysvetľuje časová zložitosť RAM programu. "
        "Cyklus vykoná n sčítaní, Gaussov vzorec n(n + 1)/2 len konštantný počet operácií."
    ),
    "category": "numeric",
    "input_type": "number",
    "renderer": "none",
    "input_description": "Celé číslo n ≥ 1.",
    "output_description": "Súčet 1 + 2 + … + n.",
    "tags": ["usaa", "cv2"],
    "checker": '''
def check(input, output, expected=None):
    want = input * (input + 1) // 2
    return output == want, f"Správny súčet je {want}"
''',
    "generators": [{
        "id": "gen_sum", "name": "Číslo n", "code": GEN_NUMBER,
        "description": "Vstupom je samotné číslo n.",
        "sizes": [10000, 50000, 200000, 500000, 1000000], "viz_size": 10, "params": [],
    }],
    "algorithms": [
        {
            "id": "alg_sum_loop", "name": "Cyklus", "viz": False,
            "description": "Postupne pripočíta každé číslo od 1 po n.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "param": "hodnota n",
            "code": '''
def solve(n, tracker):
    s = 0
    for i in range(1, n + 1):
        s += i
        tracker.count("add")
    return s
''',
        },
        {
            "id": "alg_sum_formula", "name": "Gaussov vzorec", "viz": False,
            "description": "Výsledok dá priamo vzorec n(n + 1)/2.",
            "paradigm": "iterative", "best": "O(1)", "avg": "O(1)", "worst": "O(1)", "space": "O(1)",
            "param": "hodnota n",
            "code": '''
def solve(n, tracker):
    tracker.count("add")
    tracker.count("multiply")
    return n * (n + 1) // 2
''',
        },
    ],
    "experiments": [{
        "id": "exp_sum", "name": "Cyklus oproti vzorcu",
        "algorithms": ["alg_sum_loop", "alg_sum_formula"], "generator": "gen_sum",
        "sizes": [10000, 50000, 200000, 500000, 1000000], "repeats": 3,
    }],
}

FACTORIAL = {
    "id": "prob_factorial",
    "name": "Faktoriál",
    "summary": "Vypočítaj n! = 1 · 2 · … · n cyklom alebo rekurziou.",
    "description": (
        "Úloha z cvičení 1 a 2. Oba spôsoby vykonajú n násobení, zložitosť je teda lineárna "
        "pri jednotkovom kritériu. Pri logaritmickom kritériu rastie čas rýchlejšie, lebo "
        "čísla majú stále viac číslic. Rozdiel je dobre vidieť v grafe času oproti grafu operácií."
    ),
    "category": "recursive",
    "input_type": "number",
    "renderer": "none",
    "input_description": "Celé číslo n ≥ 0 (najviac asi 900 kvôli hĺbke rekurzie).",
    "output_description": "Hodnota n!.",
    "tags": ["usaa", "cv1", "cv2"],
    "checker": '''
import math

def check(input, output, expected=None):
    return output == math.factorial(input), "Výsledok sa nezhoduje s n!"
''',
    "generators": [{
        "id": "gen_factorial", "name": "Číslo n", "code": GEN_NUMBER,
        "description": "Vstupom je samotné číslo n.",
        "sizes": [100, 200, 400, 600, 800], "viz_size": 8, "params": [],
    }],
    "algorithms": [
        {
            "id": "alg_fact_iter", "name": "Cyklus", "viz": False,
            "description": "Postupne násobí čísla 2, 3, …, n.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "n násobení (jednotkové kritérium)", "param": "hodnota n",
            "code": '''
def solve(n, tracker):
    result = 1
    for i in range(2, n + 1):
        result *= i
        tracker.count("multiply")
    return result
''',
        },
        {
            "id": "alg_fact_rec", "name": "Rekurzia", "viz": False,
            "description": "n! = n · (n − 1)!, pričom 0! = 1.",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "n násobení, hĺbka rekurzie n", "param": "hodnota n", "properties": ["recursive"],
            "code": '''
def solve(n, tracker):
    def fact(k):
        tracker.count("call")
        if k <= 1:
            return 1
        tracker.count("multiply")
        return k * fact(k - 1)

    return fact(n)
''',
        },
    ],
    "experiments": [{
        "id": "exp_factorial", "name": "Faktoriál cyklom a rekurziou",
        "algorithms": ["alg_fact_iter", "alg_fact_rec"], "generator": "gen_factorial",
        "sizes": [100, 200, 400, 600, 800], "repeats": 3,
    }],
}

POWER2 = {
    "id": "prob_power2",
    "name": "Mocnina 2ⁿ",
    "summary": "Vypočítaj 2ⁿ opakovaným násobením, rýchlym umocňovaním alebo bitovým posunom.",
    "description": (
        "Úloha z cvičenia 1. Opakované násobenie potrebuje n násobení, rýchle umocňovanie "
        "len približne 2 log₂ n, pretože číslo opakovane umocňuje na druhú. Bitový posun je "
        "jedna operácia jazyka."
    ),
    "category": "numeric",
    "input_type": "number",
    "renderer": "none",
    "input_description": "Celé číslo n ≥ 0.",
    "output_description": "Hodnota 2ⁿ.",
    "tags": ["usaa", "cv1"],
    "checker": '''
def check(input, output, expected=None):
    return output == 2 ** input, "Výsledok sa nezhoduje s 2^n"
''',
    "generators": [{
        "id": "gen_power2", "name": "Číslo n", "code": GEN_NUMBER,
        "description": "Vstupom je samotné číslo n.",
        "sizes": [1000, 4000, 16000, 32000, 64000], "viz_size": 10, "params": [],
    }],
    "algorithms": [
        {
            "id": "alg_pow_repeat", "name": "Opakované násobenie", "viz": False,
            "description": "Začne s hodnotou 1 a n-krát ju vynásobí dvoma.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "n násobení", "param": "hodnota n",
            "code": '''
def solve(n, tracker):
    result = 1
    for _ in range(n):
        result *= 2
        tracker.count("multiply")
    return result
''',
        },
        {
            "id": "alg_pow_fast", "name": "Rýchle umocňovanie", "viz": False,
            "description": "Používa 2^(2k) = (2^k)² a 2^(2k+1) = 2 · (2^k)², preto stačí logaritmický počet násobení.",
            "paradigm": "divide_and_conquer", "best": "O(log n)", "avg": "O(log n)", "worst": "O(log n)", "space": "O(1)",
            "note": "približne 2 log₂ n násobení", "param": "hodnota n",
            "code": '''
def solve(n, tracker):
    result = 1
    base = 2
    while n > 0:
        if n % 2 == 1:
            result *= base
            tracker.count("multiply")
        base *= base
        tracker.count("multiply")
        n //= 2
    return result
''',
        },
        {
            "id": "alg_pow_shift", "name": "Bitový posun", "viz": False,
            "description": "Číslo 1 posunie o n bitov doľava.",
            "paradigm": "iterative", "best": "O(1)", "avg": "O(1)", "worst": "O(1)", "space": "O(1)",
            "note": "jedna operácia jazyka, interne úmerná počtu bitov", "param": "hodnota n",
            "code": '''
def solve(n, tracker):
    tracker.count("shift")
    return 1 << n
''',
        },
    ],
    "experiments": [{
        "id": "exp_power2", "name": "Tri spôsoby výpočtu 2^n",
        "algorithms": ["alg_pow_repeat", "alg_pow_fast", "alg_pow_shift"], "generator": "gen_power2",
        "sizes": [1000, 4000, 16000, 32000, 64000], "repeats": 3,
    }],
}

PROBLEMS = [MAXMIN, SUM, FACTORIAL, POWER2]
