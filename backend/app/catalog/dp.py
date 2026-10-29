"""Dynamic programming: Fibonacciho čísla, kombinačné číslo, reťazec matíc, rozmieňanie mincí."""

from __future__ import annotations

from .common import GEN_NUMBER, enum

# ----------------------------------------------------------------------
#  Fibonacciho čísla
# ----------------------------------------------------------------------
FIBONACCI = {
    "id": "prob_fibonacci",
    "name": "Fibonacciho čísla",
    "summary": "Vypočítaj n-té Fibonacciho číslo F(n) = F(n-1) + F(n-2).",
    "description": (
        "Priamy prepis definície volá tie isté podproblémy stále znova, "
        "počet volaní rastie ako φⁿ. Zapamätanie výsledkov (memoizácia) alebo vyplnenie "
        "tabuľky zdola nahor znížia čas na O(n). Rýchle zdvojovanie potrebuje len O(log n) "
        "krokov, pri veľkom n však rozhoduje aj cena násobenia veľkých čísel."
    ),
    "category": "dynamic_programming",
    "input_type": "number",
    "renderer": "array",
    "input_description": "Celé číslo n ≥ 0.",
    "output_description": "Číslo F(n), pričom F(0) = 0 a F(1) = 1.",
    "reference": "alg_fib_two",
    "generators": [{
        "id": "gen_fib", "name": "Číslo n", "code": GEN_NUMBER,
        "description": "Vstupom je priamo veľkosť n.",
        "sizes": [5, 10, 15, 20, 25], "viz_size": 10, "test_size": 18,
    }],
    "algorithms": [
        {
            "id": "alg_fib_naive", "name": "Naive recursion", "viz": False,
            "description": "fib(n) = fib(n-1) + fib(n-2). Tie isté hodnoty sa počítajú mnohokrát.",
            "paradigm": "recursive", "best": "O(phi^n)", "avg": "O(phi^n)", "worst": "O(phi^n)",
            "space": "O(n)", "note": "φ ≈ 1,618", "param": "n", "properties": ["recursive"],
            "code": '''
def solve(n, tracker):
    def fib(k):
        tracker.count("call")
        if k < 2:
            return k
        return fib(k - 1) + fib(k - 2)

    return fib(n)
''',
        },
        {
            "id": "alg_fib_memo", "name": "Memoized recursion",
            "description": "Rovnaká rekurzia, ale každý vypočítaný výsledok sa uloží do tabuľky a znova sa nepočíta.",
            "paradigm": "dynamic_programming", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "n", "properties": ["recursive"],
            "code": '''
def solve(n, tracker):
    memo = [None] * (n + 1)
    tracker.array(memo, labels=[f"F({i})" for i in range(n + 1)])

    def fib(k):
        tracker.count("call")
        if memo[k] is not None:
            tracker.highlight([k], "compare", label=f"F({k}) už poznám")
            return memo[k]
        value = k if k < 2 else fib(k - 1) + fib(k - 2)
        memo[k] = value
        tracker.set(k, value, label=f"ulož F({k}) = {value}")
        return value

    return fib(n)
''',
        },
        {
            "id": "alg_fib_table", "name": "Bottom-up table",
            "description": "Vyplní tabuľku F(0), F(1), ..., F(n) zľava doprava.",
            "paradigm": "dynamic_programming", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "n",
            "code": '''
def solve(n, tracker):
    table = [0] * (n + 1)
    tracker.array(table, labels=[f"F({i})" for i in range(n + 1)])
    if n >= 1:
        table[1] = 1
        tracker.set(1, 1)
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
        tracker.set(i, table[i], label=f"F({i}) = F({i - 1}) + F({i - 2}) = {table[i]}")
    return table[n]
''',
        },
        {
            "id": "alg_fib_two", "name": "Two variables",
            "description": "Pamätá si len posledné dve hodnoty, preto stačí konštantná pamäť.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "param": "n",
            "code": '''
def solve(n, tracker):
    a, b = 0, 1
    pair = [a, b]
    tracker.array(pair, labels=["F(i)", "F(i+1)"])
    for i in range(n):
        a, b = b, a + b
        pair[0], pair[1] = a, b
        tracker.count("add")
        tracker.snapshot(f"i = {i + 1}: F(i) = {a}")
    return a
''',
        },
        {
            "id": "alg_fib_doubling", "name": "Fast doubling", "viz": False,
            "description": "Využíva vzťahy F(2k) = F(k)·(2F(k+1) − F(k)) a F(2k+1) = F(k)² + F(k+1)².",
            "paradigm": "divide_and_conquer", "best": "O(log n)", "avg": "O(log n)", "worst": "O(log n)",
            "space": "O(log n)", "note": "počet aritmetických operácií", "param": "n",
            "properties": ["recursive"],
            "code": '''
def solve(n, tracker):
    def pair(k):
        tracker.count("call")
        if k == 0:
            return 0, 1
        a, b = pair(k // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        tracker.count("multiply", 3)
        return (d, c + d) if k % 2 else (c, d)

    return pair(n)[0]
''',
        },
    ],
    "experiments": [
        {
            "id": "exp_fib_small", "name": "Exponenciálna rekurzia oproti lineárnym riešeniam",
            "algorithms": ["alg_fib_naive", "alg_fib_memo", "alg_fib_table", "alg_fib_two", "alg_fib_doubling"],
            "generator": "gen_fib", "sizes": [5, 10, 15, 20, 25], "repeats": 3,
        },
        {
            "id": "exp_fib_large", "name": "Lineárne riešenia a rýchle zdvojovanie pre veľké n",
            "algorithms": ["alg_fib_memo", "alg_fib_table", "alg_fib_two", "alg_fib_doubling"],
            "generator": "gen_fib", "sizes": [500, 1000, 2000, 4000, 8000], "repeats": 3,
        },
    ],
}

# ----------------------------------------------------------------------
#  Kombinačné číslo
# ----------------------------------------------------------------------
GEN_BINOM = '''
import random

def generate(n, k_mode="half", seed=42):
    """Dvojica n, k pre kombinačné číslo C(n, k)."""
    rnd = random.Random(seed)
    if k_mode == "half":
        k = n // 2
    elif k_mode == "small":
        k = min(3, n)
    else:
        k = rnd.randint(0, n)
    return {"n": n, "k": k}
'''

BINOMIAL = {
    "id": "prob_binomial",
    "name": "Kombinačné číslo",
    "summary": "Vypočítaj C(n, k), počet k-prvkových podmnožín n-prvkovej množiny.",
    "description": (
        "Pascalov vzťah C(n, k) = C(n-1, k-1) + C(n-1, k) vedie na "
        "exponenciálnu rekurziu. Tabuľka (Pascalov trojuholník) stojí O(n · k). "
        "Multiplikatívny vzorec potrebuje len k násobení a delení."
    ),
    "category": "dynamic_programming",
    "input_type": "composite",
    "renderer": "grid",
    "input_description": "Objekt {\"n\": n, \"k\": k}, kde 0 ≤ k ≤ n.",
    "output_description": "Číslo C(n, k).",
    "reference": "alg_binom_mult",
    "generators": [{
        "id": "gen_binom", "name": "Dvojica n, k", "code": GEN_BINOM,
        "description": "k je polovica n, malé číslo alebo náhodná hodnota.",
        "sizes": [6, 10, 14, 18, 20], "viz_size": 7, "test_size": 14,
        "params": [enum("k_mode", "Voľba k", {"half": "k = n / 2", "small": "k = 3",
                                               "random": "náhodné k"}, "half")],
    }],
    "algorithms": [
        {
            "id": "alg_binom_naive", "name": "Naive recursion (Pascal's rule)", "viz": False,
            "description": "C(n, k) = C(n-1, k-1) + C(n-1, k), C(n, 0) = C(n, n) = 1.",
            "paradigm": "recursive", "best": "O(1)", "avg": "O(2^n)", "worst": "O(2^n)",
            "space": "O(n)", "note": "počet volaní je približne 2 · C(n, k), pri k = n/2 rastie ako 2ⁿ/√n", "param": "n",
            "properties": ["recursive"],
            "code": '''
def solve(data, tracker):
    def c(n, k):
        tracker.count("call")
        if k == 0 or k == n:
            return 1
        return c(n - 1, k - 1) + c(n - 1, k)

    return c(data["n"], data["k"])
''',
        },
        {
            "id": "alg_binom_memo", "name": "Memoized recursion",
            "description": "Rekurzia podľa Pascalovho vzťahu, výsledky sa ukladajú do tabuľky.",
            "paradigm": "dynamic_programming", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "O(n · k), pri k = n/2 je to O(n²)", "param": "n", "properties": ["recursive"],
            "code": '''
def solve(data, tracker):
    n, k = data["n"], data["k"]
    tracker.grid(n + 1, k + 1, row_labels=range(n + 1), col_labels=range(k + 1))
    memo = {}

    def c(i, j):
        tracker.count("call")
        if (i, j) in memo:
            return memo[(i, j)]
        value = 1 if j == 0 or j == i else c(i - 1, j - 1) + c(i - 1, j)
        memo[(i, j)] = value
        tracker.set_cell(i, j, value, label=f"C({i}, {j}) = {value}")
        return value

    return c(n, k)
''',
        },
        {
            "id": "alg_binom_table", "name": "Pascal's triangle",
            "description": "Vyplní tabuľku po riadkoch. Každá bunka je súčet bunky nad ňou a bunky vľavo hore.",
            "paradigm": "dynamic_programming", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "O(n · k), pri k = n/2 je to O(n²)", "param": "n",
            "code": '''
def solve(data, tracker):
    n, k = data["n"], data["k"]
    tracker.grid(n + 1, k + 1, row_labels=range(n + 1), col_labels=range(k + 1))
    t = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(min(i, k) + 1):
            if j == 0 or j == i:
                t[i][j] = 1
            else:
                tracker.read_cell(i - 1, j - 1)
                tracker.read_cell(i - 1, j)
                t[i][j] = t[i - 1][j - 1] + t[i - 1][j]
            tracker.set_cell(i, j, t[i][j])
    return t[n][k]
''',
        },
        {
            "id": "alg_binom_mult", "name": "Multiplicative formula", "viz": False,
            "description": "C(n, k) = n/1 · (n-1)/2 · ... · (n-k+1)/k. Každý medzivýsledok je celé číslo.",
            "paradigm": "iterative", "best": "O(1)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "O(k) násobení, k ≤ n/2", "param": "n",
            "code": '''
def solve(data, tracker):
    n, k = data["n"], data["k"]
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
        tracker.count("multiply")
    tracker.count("return")
    return result
''',
        },
    ],
    "experiments": [
        {
            "id": "exp_binom_small", "name": "Rekurzia oproti tabuľke",
            "algorithms": ["alg_binom_naive", "alg_binom_memo", "alg_binom_table", "alg_binom_mult"],
            "generator": "gen_binom", "sizes": [6, 10, 14, 18, 20], "repeats": 3,
        },
        {
            "id": "exp_binom_large", "name": "Tabuľka oproti vzorcu pre veľké n",
            "algorithms": ["alg_binom_table", "alg_binom_mult"],
            "generator": "gen_binom", "sizes": [100, 200, 400, 800, 1600], "repeats": 3,
        },
    ],
}

# ----------------------------------------------------------------------
#  Násobenie reťazca matíc
# ----------------------------------------------------------------------
GEN_CHAIN = '''
import random

def generate(n, seed=42, max_dim=50):
    """Rozmery n matíc: matica i má rozmer p[i] × p[i+1]."""
    rnd = random.Random(seed)
    return [rnd.randint(2, max_dim) for _ in range(n + 1)]
'''

MATRIX_CHAIN = {
    "id": "prob_matrix_chain",
    "name": "Násobenie reťazca matíc",
    "summary": "Nájdi uzátvorkovanie, pri ktorom súčin matíc A₁ · A₂ · ... · Aₙ stojí najmenej násobení.",
    "description": (
        "Skúšanie všetkých uzátvorkovaní rastie exponenciálne. Tabuľka "
        "m[i][j] s najlacnejším súčinom matíc i až j sa vypĺňa podľa dĺžky úseku a stojí O(n³)."
    ),
    "category": "dynamic_programming",
    "input_type": "array",
    "renderer": "grid",
    "input_description": "Zoznam p dĺžky n + 1. Matica i má rozmer p[i-1] × p[i].",
    "output_description": "Najmenší počet skalárnych násobení.",
    "reference": "alg_chain_dp",
    "generators": [{
        "id": "gen_chain", "name": "Rozmery matíc", "code": GEN_CHAIN,
        "description": "Náhodné rozmery od 2 do 50.",
        "sizes": [4, 6, 8, 10, 12], "viz_size": 5, "test_size": 8,
    }],
    "algorithms": [
        {
            "id": "alg_chain_naive", "name": "Naive recursion", "viz": False,
            "description": "Pre každý úsek skúsi každé miesto posledného násobenia a rekurzívne vyrieši obe časti.",
            "paradigm": "recursive", "best": "O(3^n)", "avg": "O(3^n)", "worst": "O(3^n)",
            "space": "O(n)", "note": "počet volaní je 3ⁿ⁻¹", "param": "počet matíc",
            "properties": ["recursive"],
            "code": '''
def solve(p, tracker):
    def cost(i, j):
        tracker.count("call")
        if i == j:
            return 0
        best = None
        for k in range(i, j):
            c = cost(i, k) + cost(k + 1, j) + p[i - 1] * p[k] * p[j]
            if best is None or c < best:
                best = c
        return best

    return cost(1, len(p) - 1)
''',
        },
        {
            "id": "alg_chain_memo", "name": "Memoized recursion",
            "description": "Rovnaká rekurzia, cena každého úseku sa vypočíta len raz.",
            "paradigm": "dynamic_programming", "best": "O(n^3)", "avg": "O(n^3)", "worst": "O(n^3)",
            "space": "O(n^2)", "param": "počet matíc", "properties": ["recursive"],
            "code": '''
def solve(p, tracker):
    n = len(p) - 1
    tracker.grid(n, n, row_labels=range(1, n + 1), col_labels=range(1, n + 1))
    memo = {}

    def cost(i, j):
        tracker.count("call")
        if (i, j) in memo:
            return memo[(i, j)]
        if i == j:
            best = 0
        else:
            best = min(cost(i, k) + cost(k + 1, j) + p[i - 1] * p[k] * p[j] for k in range(i, j))
        memo[(i, j)] = best
        tracker.set_cell(i - 1, j - 1, best, label=f"m[{i}][{j}] = {best}")
        return best

    return cost(1, n)
''',
        },
        {
            "id": "alg_chain_dp", "name": "Bottom-up dynamic programming",
            "description": "Najprv vyplní úseky dĺžky 1, potom 2 a tak ďalej až po celý reťazec.",
            "paradigm": "dynamic_programming", "best": "O(n^3)", "avg": "O(n^3)", "worst": "O(n^3)",
            "space": "O(n^2)", "param": "počet matíc",
            "code": '''
def solve(p, tracker):
    n = len(p) - 1
    tracker.grid(n, n, row_labels=range(1, n + 1), col_labels=range(1, n + 1))
    m = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        tracker.set_cell(i - 1, i - 1, 0)
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            best = None
            for k in range(i, j):
                tracker.count("compare")
                c = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                if best is None or c < best:
                    best = c
            m[i][j] = best
            tracker.read_cell(i - 1, j - 2)
            tracker.read_cell(i, j - 1)
            tracker.set_cell(i - 1, j - 1, best, label=f"m[{i}][{j}] = {best}")
    return m[1][n]
''',
        },
    ],
    "experiments": [
        {
            "id": "exp_chain_small", "name": "Exponenciálna rekurzia oproti tabuľke",
            "algorithms": ["alg_chain_naive", "alg_chain_memo", "alg_chain_dp"],
            "generator": "gen_chain", "sizes": [4, 6, 8, 10, 12], "repeats": 3,
        },
        {
            "id": "exp_chain_large", "name": "Memoizácia oproti tabuľke",
            "algorithms": ["alg_chain_memo", "alg_chain_dp"],
            "generator": "gen_chain", "sizes": [20, 40, 60, 80, 100], "repeats": 3,
        },
    ],
}

# ----------------------------------------------------------------------
#  Rozmieňanie mincí
# ----------------------------------------------------------------------
COIN_SETS = {
    "nekanonicka": "mince 100, 25, 20, 5, 1",
    "kanonicka": "mince 50, 20, 10, 5, 2, 1 (euro)",
}

GEN_COINS = '''
import random

COINS = {"nekanonicka": [100, 25, 20, 5, 1], "kanonicka": [50, 20, 10, 5, 2, 1]}

def generate(n, coin_set="nekanonicka", mode="random", seed=42):
    """Suma na rozmenenie a sada mincí. Pri mode="exact" je suma presne n."""
    rnd = random.Random(seed)
    amount = n if mode == "exact" else n + rnd.randint(0, max(1, n // 10))
    return {"coins": COINS[coin_set], "amount": amount}
'''

CHECK_COINS = '''
def check(input, output, expected=None):
    """Mince musia patriť do sady, dať presne sumu a byť ich najmenej, koľko sa dá."""
    if not isinstance(output, list):
        return False, "Výstup má byť zoznam mincí"
    allowed = set(input["coins"])
    for c in output:
        if c not in allowed:
            return False, f"Minca {c} nie je v sade"
    if sum(output) != input["amount"]:
        return False, f"Súčet mincí je {sum(output)}, suma je {input['amount']}"
    if expected is not None and len(output) > len(expected):
        return False, f"Použitých {len(output)} mincí, stačí {len(expected)}"
    return True
'''

COIN_CHANGE = {
    "id": "prob_coin_change",
    "name": "Rozmieňanie mincí",
    "summary": "Rozmeň sumu na čo najmenej mincí z danej sady.",
    "description": (
        "Greedy algoritmus berie vždy najväčšiu mincu, ktorá sa ešte "
        "zmestí. Pri eurových minciach dá vždy optimum, pri sade 100, 25, 20, 5, 1 nie: "
        "sumu 40 rozmení na 25 + 5 + 5 + 5 namiesto 20 + 20. Dynamic programming "
        "vypočíta optimum pre každú sumu od 0 po cieľovú."
    ),
    "category": "dynamic_programming",
    "input_type": "composite",
    "renderer": "array",
    "input_description": "Objekt {\"coins\": sada mincí, \"amount\": suma}. Sada vždy obsahuje mincu 1.",
    "output_description": "Zoznam použitých mincí.",
    "reference": "alg_coins_dp",
    "checker": CHECK_COINS,
    "generators": [{
        "id": "gen_coins", "name": "Suma a sada mincí", "code": GEN_COINS,
        "description": "Suma približne n a jedna z dvoch sád mincí.",
        "sizes": [1000, 2000, 4000, 8000, 16000], "viz_size": 40, "test_size": 40,
        "params": [
            enum("coin_set", "Sada mincí", COIN_SETS, "nekanonicka"),
            enum("mode", "Suma", {"random": "n plus náhodný posun", "exact": "presne n"}, "random"),
        ],
    }],
    "algorithms": [
        {
            "id": "alg_coins_greedy", "name": "Greedy",
            "description": "Opakovane vezme najväčšiu mincu, ktorá nepresiahne zvyšok sumy.",
            "paradigm": "greedy", "best": "O(n)", "avg": "O(n)", "worst": "O(n)",
            "space": "O(n)", "note": "suma a, najviac a/c odberov najväčšej mince c", "param": "suma",
            "properties": ["intentionally_incorrect"],
            "code": '''
def solve(data, tracker):
    coins = sorted(data["coins"], reverse=True)
    tracker.array(coins, labels=[str(c) for c in coins])
    rest = data["amount"]
    used = []
    for i, c in enumerate(coins):
        tracker.highlight([i], "compare", label=f"zvyšok {rest}, skúšam mincu {c}")
        while c <= rest:
            rest -= c
            used.append(c)
            tracker.count("take")
            tracker.highlight([i], "active", label=f"vezmi {c}, zvyšok {rest}")
    return used
''',
        },
        {
            "id": "alg_coins_dp", "name": "Dynamic programming",
            "description": "best[s] je najmenší počet mincí pre sumu s. Pre každú mincu c platí best[s] ≤ best[s - c] + 1.",
            "paradigm": "dynamic_programming", "best": "O(n)", "avg": "O(n)", "worst": "O(n)",
            "space": "O(n)", "note": "O(a · k), a je suma, k počet druhov mincí", "param": "suma",
            "code": '''
def solve(data, tracker):
    coins, amount = data["coins"], data["amount"]
    inf = amount + 1
    best = [0] + [inf] * amount
    last = [0] * (amount + 1)
    shown = [0] + ["∞"] * amount
    tracker.array(shown)
    for s in range(1, amount + 1):
        for c in coins:
            tracker.count("compare")
            if c <= s and best[s - c] + 1 < best[s]:
                best[s] = best[s - c] + 1
                last[s] = c
        shown[s] = best[s]
        tracker.highlight([s - last[s]], "compare")
        tracker.set(s, best[s], label=f"suma {s}: {best[s]} mincí, posledná {last[s]}")
    used = []
    s = amount
    while s > 0:
        used.append(last[s])
        s -= last[s]
    return used
''',
        },
    ],
    "experiments": [{
        "id": "exp_coins", "name": "Greedy oproti dynamic programming",
        "algorithms": ["alg_coins_greedy", "alg_coins_dp"], "generator": "gen_coins",
        "sizes": [1000, 2000, 4000, 8000, 16000], "repeats": 3,
        "variants": [
            {"label": "mince 100, 25, 20, 5, 1", "params": {"coin_set": "nekanonicka"}},
            {"label": "eurové mince", "params": {"coin_set": "kanonicka"}},
        ],
    }],
}

PROBLEMS = [FIBONACCI, BINOMIAL, MATRIX_CHAIN, COIN_CHANGE]
