"""Úlohy mimo predmetu ÚSaA: vyhľadávanie, najkratšie cesty, kostra, vyhľadávanie vzorky, LCS.

Dopĺňajú katalóg o klasické algoritmy z literatúry (Cormen a kol., Sedgewick a Wayne),
na ktorých sa dobre ukazuje rozdiel medzi priemerným a najhorším prípadom.
"""

from __future__ import annotations

from .common import GEN_GRAPH, GRAPH_KINDS, enum, number

# ----------------------------------------------------------------------
#  Vyhľadávanie v zoradenom poli
# ----------------------------------------------------------------------
GEN_SEARCH = '''
import random

def generate(n, spread="uniform", queries=50, seed=42):
    """Zoradené pole dĺžky n a zoznam hľadaných hodnôt (asi polovica sa v poli nachádza)."""
    rnd = random.Random(seed)
    if spread == "uniform":
        array = [3 * i + rnd.randint(0, 2) for i in range(n)]
    elif spread == "skewed":
        # takmer rovnomerné hodnoty a na konci jedna obrovská, interpolácia sa potom posúva po jednom
        array = list(range(n - 1)) + [n ** 3]
    else:
        array = sorted(rnd.randint(0, 10 * n) for _ in range(n))
    q = min(queries, max(3, n // 4))
    wanted = []
    for _ in range(q):
        if rnd.random() < 0.5:
            wanted.append(rnd.choice(array))
        else:
            wanted.append(rnd.randint(array[0], array[-1]) if array else 0)
    return {"array": array, "queries": wanted}
'''

CHECK_SEARCH = '''
def check(input, output, expected=None):
    """Pre každú hodnotu musí byť vrátený index, na ktorom sa nachádza, alebo -1."""
    a, qs = input["array"], input["queries"]
    present = set(a)
    if not isinstance(output, list) or len(output) != len(qs):
        return False, f"Výstup má mať {len(qs)} indexov"
    for k, (x, i) in enumerate(zip(qs, output)):
        if x in present:
            if not isinstance(i, int) or not (0 <= i < len(a)) or a[i] != x:
                return False, f"Hodnota {x} je v poli, vrátený index {i} je zlý"
        elif i != -1:
            return False, f"Hodnota {x} v poli nie je, správny výsledok je -1, nie {i}"
    return True
'''

SEARCH = {
    "id": "prob_search",
    "name": "Vyhľadávanie v zoradenom poli",
    "summary": "Pre každú hľadanú hodnotu nájdi jej index v zoradenom poli alebo vráť -1.",
    "description": (
        "Lineárne vyhľadávanie prezrie pole od začiatku. Binárne vyhľadávanie v každom kroku "
        "odstráni polovicu úseku. Interpolačné vyhľadávanie odhadne polohu z hodnoty, ako keď "
        "hľadáme v telefónnom zozname. Pri rovnomerne rozložených hodnotách stačí v priemere "
        "O(log log n) krokov, pri nerovnomernom rozložení sa spomalí až na O(n)."
    ),
    "category": "searching",
    "input_type": "composite",
    "renderer": "array",
    "input_description": "Objekt {\"array\": zoradené pole, \"queries\": hľadané hodnoty}.",
    "output_description": "Zoznam indexov, -1 pre hodnotu, ktorá v poli nie je.",
    "tags": ["mimo-kurzu"],
    "checker": CHECK_SEARCH,
    "generators": [{
        "id": "gen_search", "name": "Zoradené pole a dopyty", "code": GEN_SEARCH,
        "description": "Rovnomerné, náhodné hodnoty alebo pole s jednou extrémne veľkou hodnotou na konci.",
        "sizes": [1000, 2000, 4000, 8000, 16000], "viz_size": 16,
        "params": [
            enum("spread", "Rozloženie hodnôt", {"uniform": "rovnomerné", "random": "náhodné",
                                                  "skewed": "jedna extrémne veľká hodnota"}, "uniform"),
            number("queries", "Počet dopytov", 50),
        ],
    }],
    "algorithms": [
        {
            "id": "alg_search_linear", "name": "Lineárne vyhľadávanie",
            "description": "Porovná hľadanú hodnotu postupne s každým prvkom poľa.",
            "paradigm": "iterative", "best": "O(1)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "na jeden dopyt", "param": "dĺžka poľa",
            "code": '''
def solve(data, tracker):
    a = data["array"]
    tracker.array(a)
    out = []
    for x in data["queries"]:
        found = -1
        for i, y in enumerate(a):
            tracker.count("compare")
            tracker.highlight([i], "compare", label=f"hľadám {x}, a[{i}] = {y}")
            if y == x:
                found = i
                break
        out.append(found)
    return out
''',
        },
        {
            "id": "alg_search_binary", "name": "Binárne vyhľadávanie",
            "description": "Porovná hodnotu so stredom úseku a pokračuje v ľavej alebo pravej polovici.",
            "paradigm": "divide_and_conquer", "best": "O(1)", "avg": "O(log n)", "worst": "O(log n)",
            "space": "O(1)", "note": "na jeden dopyt", "param": "dĺžka poľa",
            "code": '''
def solve(data, tracker):
    a = data["array"]
    tracker.array(a)
    out = []
    for x in data["queries"]:
        lo, hi, found = 0, len(a) - 1, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            tracker.count("compare")
            tracker.pointer("lo", lo)
            tracker.pointer("hi", hi)
            tracker.pointer("mid", mid)
            tracker.highlight([mid], "compare", label=f"hľadám {x}, stred a[{mid}] = {a[mid]}")
            if a[mid] == x:
                found = mid
                break
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid - 1
        out.append(found)
    for name in ("lo", "hi", "mid"):
        tracker.pointer(name, None)
    return out
''',
        },
        {
            "id": "alg_search_interp", "name": "Interpolačné vyhľadávanie",
            "description": "Odhadne polohu hodnoty lineárnou interpoláciou medzi krajnými prvkami úseku.",
            "paradigm": "iterative", "best": "O(1)", "avg": "O(log log n)", "worst": "O(n)",
            "space": "O(1)", "note": "priemer platí pre rovnomerne rozložené hodnoty", "param": "dĺžka poľa",
            "code": '''
def solve(data, tracker):
    a = data["array"]
    tracker.array(a)
    out = []
    for x in data["queries"]:
        lo, hi, found = 0, len(a) - 1, -1
        while lo <= hi and a[lo] <= x <= a[hi]:
            if a[hi] == a[lo]:
                pos = lo
            else:
                pos = lo + (x - a[lo]) * (hi - lo) // (a[hi] - a[lo])
            tracker.count("compare")
            tracker.pointer("lo", lo)
            tracker.pointer("hi", hi)
            tracker.highlight([pos], "compare", label=f"hľadám {x}, odhad a[{pos}] = {a[pos]}")
            if a[pos] == x:
                found = pos
                break
            if a[pos] < x:
                lo = pos + 1
            else:
                hi = pos - 1
        out.append(found)
    tracker.pointer("lo", None)
    tracker.pointer("hi", None)
    return out
''',
        },
    ],
    "experiments": [{
        "id": "exp_search", "name": "Binárne a interpolačné vyhľadávanie",
        "algorithms": ["alg_search_linear", "alg_search_binary", "alg_search_interp"],
        "generator": "gen_search", "sizes": [1000, 2000, 4000, 8000, 16000], "repeats": 3,
        "variants": [
            {"label": "rovnomerné hodnoty", "params": {"spread": "uniform"}},
            {"label": "jedna obrovská hodnota", "params": {"spread": "skewed"}},
        ],
    }],
}

# ----------------------------------------------------------------------
#  Vážené grafy
# ----------------------------------------------------------------------
GEN_WGRAPH = GEN_GRAPH.replace("weighted=False", "weighted=True")
WGRAPH_INPUT = (
    "Neorientovaný vážený graf: n je počet vrcholov, edges je zoznam hrán [u, v, w] "
    "s kladnou váhou w a start je štartový vrchol."
)
WEIGHTED_KINDS = {k: GRAPH_KINDS[k] for k in ("sparse", "dense", "grid", "disconnected")}


def _wgen(gid: str, sizes: list[int]) -> dict:
    return {
        "id": gid, "name": "Náhodný vážený graf", "code": GEN_WGRAPH,
        "description": "Riedky, hustý, mriežkový alebo nesúvislý graf s váhami 1 až 20.",
        "sizes": sizes, "viz_size": 10,
        "params": [enum("kind", "Druh grafu", WEIGHTED_KINDS, "sparse")],
    }


WADJ = '''
    adj = [[] for _ in range(g["n"])]
    for u, v, w in g["edges"]:
        adj[u].append((v, w))
        adj[v].append((u, w))
'''

SSSP = {
    "id": "prob_sssp",
    "name": "Najkratšie cesty vo váženom grafe",
    "summary": "Nájdi dĺžku najkratšej cesty zo štartu do každého vrchola.",
    "description": (
        "Dijkstrov algoritmus vyberá vždy najbližší ešte nespracovaný vrchol. S obyčajným poľom "
        "stojí výber O(n), spolu O(n²). S binárnou haldou stojí O((n + m) log n), čo je výhodné "
        "na riedkych grafoch. Bellmanov-Fordov algoritmus opakovane uvoľňuje všetky hrany, "
        "zvládne aj záporné váhy, ale stojí O(n · m)."
    ),
    "category": "graph",
    "input_type": "weighted_graph",
    "renderer": "graph",
    "input_description": WGRAPH_INPUT,
    "output_description": "Zoznam dist, kde dist[v] je dĺžka najkratšej cesty, -1 pre nedosiahnuteľný vrchol.",
    "tags": ["mimo-kurzu"],
    "reference": "alg_dijkstra_heap",
    "generators": [_wgen("gen_sssp", [250, 500, 1000, 2000])],
    "algorithms": [
        {
            "id": "alg_dijkstra_array", "name": "Dijkstra s poľom",
            "description": "Najbližší nespracovaný vrchol hľadá prechodom celého poľa vzdialeností.",
            "paradigm": "greedy", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(n)",
            "note": "O(n² + m)", "param": "počet vrcholov",
            "code": '''
def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"], weighted=True)
''' + WADJ + '''
    inf = float("inf")
    dist = [inf] * n
    done = [False] * n
    dist[g["start"]] = 0
    tracker.node_label(g["start"], 0)
    for _ in range(n):
        u, best = -1, inf
        for v in range(n):
            tracker.count("scan")
            if not done[v] and dist[v] < best:
                u, best = v, dist[v]
        if u < 0:
            break
        done[u] = True
        tracker.visit(u, label=f"najbližší nespracovaný vrchol je {u}, dist = {best}")
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                tracker.relax(u, v, dist[v])
    return [d if d < inf else -1 for d in dist]
''',
        },
        {
            "id": "alg_dijkstra_heap", "name": "Dijkstra s binárnou haldou",
            "description": "Kandidáti sú v halde podľa vzdialenosti. Zastarané záznamy sa pri výbere preskočia.",
            "paradigm": "greedy", "best": "O(n log n)", "avg": "O(n log n)", "worst": "other",
            "space": "O(n)", "note": "O((n + m) log n), v hustom grafe O(n² log n). Operácia s haldou sa počíta ako jedna, preto počet operácií ukáže O(n + m)", "param": "počet vrcholov",
            "code": '''
import heapq


def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"], weighted=True)
''' + WADJ + '''
    inf = float("inf")
    dist = [inf] * n
    dist[g["start"]] = 0
    tracker.node_label(g["start"], 0)
    heap = [(0, g["start"])]
    while heap:
        tracker.frontier((v for _, v in heap), "halda")
        d, u = heapq.heappop(heap)
        tracker.count("pop")
        if d > dist[u]:
            continue
        tracker.visit(u, label=f"vyber {u} z haldy, dist = {d}")
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
                tracker.relax(u, v, dist[v])
    tracker.frontier([], "halda")
    return [d if d < inf else -1 for d in dist]
''',
        },
        {
            "id": "alg_bellman_ford", "name": "Bellman-Ford",
            "description": "Najviac n − 1 krát uvoľní všetky hrany. Skončí skôr, ak sa v prechode nič nezmení.",
            "paradigm": "dynamic_programming", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^3)",
            "space": "O(n)", "note": "O(n · m)", "param": "počet vrcholov",
            "code": '''
def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"], weighted=True)
    inf = float("inf")
    dist = [inf] * n
    dist[g["start"]] = 0
    tracker.node_label(g["start"], 0)
    for rnd in range(n - 1):
        changed = False
        for u, v, w in g["edges"]:
            for a, b in ((u, v), (v, u)):
                tracker.count("edge")
                if dist[a] + w < dist[b]:
                    dist[b] = dist[a] + w
                    tracker.relax(a, b, dist[b], label=f"prechod {rnd + 1}: d[{b}] = {dist[b]}")
                    changed = True
        if not changed:
            break
    return [d if d < inf else -1 for d in dist]
''',
        },
    ],
    "experiments": [{
        "id": "exp_sssp", "name": "Dijkstra s poľom a haldou, Bellman-Ford",
        "algorithms": ["alg_dijkstra_array", "alg_dijkstra_heap", "alg_bellman_ford"],
        "generator": "gen_sssp", "sizes": [250, 500, 1000, 2000], "repeats": 3,
        "variants": [
            {"label": "riedky graf", "params": {"kind": "sparse"}},
            {"label": "hustý graf", "params": {"kind": "dense"}},
        ],
    }],
}

CHECK_MST = '''
def check(input, output, expected=None):
    """Výstup musí byť kostrový les grafu s rovnakou celkovou váhou ako referenčné riešenie."""
    n = input["n"]
    weight = {}
    for u, v, w in input["edges"]:
        weight[(min(u, v), max(u, v))] = w
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v, _ in input["edges"]:
        parent[find(u)] = find(v)
    need = n - len({find(v) for v in range(n)})
    if not isinstance(output, list) or len(output) != need:
        return False, f"Kostra má mať {need} hrán"
    parent = list(range(n))
    total = 0
    for e in output:
        u, v = e[0], e[1]
        key = (min(u, v), max(u, v))
        if key not in weight:
            return False, f"Hrana {u}-{v} nie je v grafe"
        if find(u) == find(v):
            return False, f"Hrana {u}-{v} vytvára cyklus"
        parent[find(u)] = find(v)
        total += weight[key]
    if expected is not None:
        best = sum(e[2] for e in expected)
        if total != best:
            return False, f"Celková váha {total}, minimálna je {best}"
    return True
'''

MST = {
    "id": "prob_mst",
    "name": "Minimálna kostra grafu",
    "summary": "Vyber hrany s najmenším súčtom váh, ktoré spoja všetky vrcholy.",
    "description": (
        "Kruskalov algoritmus zoradí hrany podľa váhy a pridáva tie, ktoré nevytvoria cyklus. "
        "Na test cyklu používa štruktúru disjunktných množín. Primov algoritmus rozširuje strom "
        "od jedného vrchola o najlacnejšiu hranu von. S haldou sa hodí na riedke grafy, "
        "s maticou a poľom na husté grafy."
    ),
    "category": "greedy",
    "input_type": "weighted_graph",
    "renderer": "graph",
    "input_description": WGRAPH_INPUT + " Pri nesúvislom grafe sa hľadá minimálny kostrový les.",
    "output_description": "Zoznam hrán [u, v, w] kostry.",
    "tags": ["mimo-kurzu"],
    "reference": "alg_kruskal",
    "checker": CHECK_MST,
    "generators": [_wgen("gen_mst", [250, 500, 1000, 2000])],
    "algorithms": [
        {
            "id": "alg_kruskal", "name": "Kruskal",
            "description": "Hrany zoradené podľa váhy, disjunktné množiny so spájaním podľa výšky a skracovaním ciest.",
            "paradigm": "greedy", "best": "O(n log n)", "avg": "O(n log n)", "worst": "other",
            "space": "O(n)", "note": "O(m log m) kvôli zoradeniu hrán. Zabudované zoradenie sa nepočíta, preto počet operácií ukáže O(m)", "param": "počet vrcholov",
            "code": '''
def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"], weighted=True)
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            tracker.count("find")
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = []
    for u, v, w in sorted(g["edges"], key=lambda e: e[2]):
        tracker.count("edge")
        ru, rv = find(u), find(v)
        if ru == rv:
            tracker.edge(u, v, "compare", label=f"hrana {u}-{v} ({w}) by vytvorila cyklus")
            continue
        if rank[ru] < rank[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        if rank[ru] == rank[rv]:
            rank[ru] += 1
        tree.append([u, v, w])
        tracker.edge(u, v, "tree", label=f"pridaj hranu {u}-{v} s váhou {w}")
        if len(tree) == n - 1:
            break
    return tree
''',
        },
        {
            "id": "alg_prim_heap", "name": "Prim s haldou",
            "description": "Halda drží hrany vedúce zo stromu von. Vyberie najlacnejšiu, ktorá vedie do nového vrchola.",
            "paradigm": "greedy", "best": "O(n log n)", "avg": "O(n log n)", "worst": "other",
            "space": "O(n)", "note": "O(m log n), v hustom grafe O(n² log n). Operácia s haldou sa počíta ako jedna, preto počet operácií ukáže O(m)", "param": "počet vrcholov",
            "code": '''
import heapq


def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"], weighted=True)
''' + WADJ + '''
    inside = [False] * n
    tree = []
    for s in range(n):
        if inside[s]:
            continue
        inside[s] = True
        tracker.visit(s)
        heap = [(w, s, v) for v, w in adj[s]]
        heapq.heapify(heap)
        while heap:
            w, u, v = heapq.heappop(heap)
            tracker.count("pop")
            if inside[v]:
                continue
            inside[v] = True
            tree.append([u, v, w])
            tracker.edge(u, v, "tree", label=f"najlacnejšia hrana von je {u}-{v} ({w})")
            tracker.visit(v)
            for x, wx in adj[v]:
                if not inside[x]:
                    heapq.heappush(heap, (wx, v, x))
    return tree
''',
        },
        {
            "id": "alg_prim_matrix", "name": "Prim s maticou",
            "description": "Pre každý vrchol mimo stromu si pamätá najlacnejšiu hranu do stromu. Ďalší vrchol vyberá prechodom poľa.",
            "paradigm": "greedy", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(n^2)",
            "note": "nezávisí od počtu hrán", "param": "počet vrcholov",
            "code": '''
def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"], weighted=True)
    inf = float("inf")
    matrix = [[inf] * n for _ in range(n)]
    for u, v, w in g["edges"]:
        matrix[u][v] = matrix[v][u] = w
    inside = [False] * n
    cost = [inf] * n
    via = [-1] * n
    tree = []
    for _ in range(n):
        u, best = -1, inf
        for v in range(n):
            tracker.count("scan")
            if not inside[v] and (u < 0 or cost[v] < best):
                u, best = v, cost[v]
        inside[u] = True
        if via[u] >= 0:
            tree.append([via[u], u, matrix[via[u]][u]])
            tracker.edge(via[u], u, "tree", label=f"pridaj {via[u]}-{u} ({matrix[via[u]][u]})")
        tracker.visit(u)
        row = matrix[u]
        for v in range(n):
            tracker.count("matrix_read")
            if not inside[v] and row[v] < cost[v]:
                cost[v] = row[v]
                via[v] = u
    return tree
''',
        },
    ],
    "experiments": [{
        "id": "exp_mst", "name": "Kruskal a Prim na riedkych a hustých grafoch",
        "algorithms": ["alg_kruskal", "alg_prim_heap", "alg_prim_matrix"],
        "generator": "gen_mst", "sizes": [250, 500, 1000, 2000], "repeats": 3,
        "variants": [
            {"label": "riedky graf", "params": {"kind": "sparse"}},
            {"label": "hustý graf", "params": {"kind": "dense"}},
        ],
    }],
}

# ----------------------------------------------------------------------
#  Vyhľadávanie vzorky v texte
# ----------------------------------------------------------------------
GEN_PATTERN = '''
import random

def generate(n, kind="random", pattern_len=20, seed=42):
    """Text dĺžky n a vzorka. Pri kind="random" sa vzorka v texte niekoľkokrát vyskytuje."""
    rnd = random.Random(seed)
    m = max(2, min(pattern_len, n // 6))
    if kind == "repetitive":
        return {"text": "a" * n, "pattern": "a" * (m - 1) + "b"}
    if kind == "repetitive_front":
        return {"text": "a" * n, "pattern": "b" + "a" * (m - 1)}
    letters = "ACGT" if kind == "dna" else "abcdefghij"
    text = [rnd.choice(letters) for _ in range(n)]
    pattern = "".join(rnd.choice(letters) for _ in range(m))
    for _ in range(max(1, n // 200)):
        pos = rnd.randrange(0, n - m + 1)
        text[pos:pos + m] = list(pattern)
    return {"text": "".join(text), "pattern": pattern}
'''

PATTERN_KINDS = {
    "random": "náhodný text (10 písmen)",
    "dna": "DNA (písmená A, C, G, T)",
    "repetitive": "text aaa…a, vzorka aa…ab",
    "repetitive_front": "text aaa…a, vzorka baa…a",
}

PATTERN = {
    "id": "prob_pattern",
    "name": "Vyhľadávanie vzorky v texte",
    "summary": "Nájdi všetky pozície, na ktorých sa vzorka nachádza v texte.",
    "description": (
        "Naivný algoritmus skúša každú pozíciu a porovnáva znak po znaku, v najhoršom prípade "
        "O(n · m). KMP si z vopred spracovanej vzorky pamätá, o koľko sa môže posunúť, a nikdy "
        "sa v texte nevracia, preto stojí O(n + m). Horspool porovnáva odzadu a pri nezhode "
        "skáče podľa tabuľky posunov, v praxi je často najrýchlejší. Rabin-Karp porovnáva "
        "odtlačky (hash) úsekov textu."
    ),
    "category": "string",
    "input_type": "string",
    "renderer": "string",
    "input_description": "Objekt {\"text\": text, \"pattern\": vzorka}.",
    "output_description": "Zoznam začiatočných pozícií všetkých výskytov vzorky.",
    "tags": ["mimo-kurzu"],
    "reference": "alg_kmp",
    "generators": [{
        "id": "gen_pattern", "name": "Text a vzorka", "code": GEN_PATTERN,
        "description": "Náhodný text, DNA alebo opakujúci sa text, ktorý vyvolá najhorší prípad.",
        "sizes": [5000, 10000, 20000, 40000, 80000], "viz_size": 30,
        "params": [enum("kind", "Druh textu", PATTERN_KINDS, "random"),
                   number("pattern_len", "Dĺžka vzorky", 20)],
    }],
    "algorithms": [
        {
            "id": "alg_naive_match", "name": "Naivné vyhľadávanie",
            "description": "Pre každú pozíciu porovná vzorku s textom zľava doprava až po prvú nezhodu.",
            "paradigm": "brute_force", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)", "space": "O(1)",
            "note": "O(n · m), m je dĺžka vzorky", "param": "dĺžka textu",
            "code": '''
def solve(data, tracker):
    t, p = data["text"], data["pattern"]
    tracker.string(t, p)
    n, m = len(t), len(p)
    out = []
    for s in range(n - m + 1):
        tracker.shift(s)
        j = 0
        while j < m and t[s + j] == p[j]:
            tracker.match(s + j, j)
            j += 1
        if j == m:
            out.append(s)
            tracker.found(s)
        else:
            tracker.mismatch(s + j, j)
    return out
''',
        },
        {
            "id": "alg_kmp", "name": "Knuth-Morris-Pratt",
            "description": "Tabuľka prefixov povie, aká dlhá časť vzorky sa zhoduje aj po posune. Ukazovateľ v texte ide len dopredu.",
            "paradigm": "dynamic_programming", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "note": "O(n + m), pamäť O(m)", "param": "dĺžka textu",
            "code": '''
def solve(data, tracker):
    t, p = data["text"], data["pattern"]
    tracker.string(t, p)
    n, m = len(t), len(p)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and p[i] != p[k]:
            tracker.count("prefix")
            k = fail[k - 1]
        if p[i] == p[k]:
            k += 1
        fail[i] = k
    out = []
    j = 0
    for i in range(n):
        while j > 0 and t[i] != p[j]:
            tracker.mismatch(i, j)
            j = fail[j - 1]
            tracker.shift(i - j)
        if t[i] == p[j]:
            tracker.match(i, j)
            j += 1
            if j == m:
                out.append(i - m + 1)
                tracker.found(i - m + 1)
                j = fail[j - 1]
                tracker.shift(i - j + 1)
        else:
            tracker.mismatch(i, j)
            tracker.shift(i + 1)
    return out
''',
        },
        {
            "id": "alg_horspool", "name": "Boyer-Moore-Horspool",
            "description": "Porovnáva vzorku odzadu. Posun určí znak textu pod posledným znakom vzorky.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)", "space": "O(1)",
            "note": "najlepšie O(n / m), najhoršie O(n · m)", "param": "dĺžka textu",
            "code": '''
def solve(data, tracker):
    t, p = data["text"], data["pattern"]
    tracker.string(t, p)
    n, m = len(t), len(p)
    shift = {}
    for i in range(m - 1):
        shift[p[i]] = m - 1 - i
    out = []
    s = 0
    while s <= n - m:
        tracker.shift(s)
        j = m - 1
        while j >= 0 and t[s + j] == p[j]:
            tracker.match(s + j, j)
            j -= 1
        if j < 0:
            out.append(s)
            tracker.found(s)
        else:
            tracker.mismatch(s + j, j)
        s += shift.get(t[s + m - 1], m)
    return out
''',
        },
        {
            "id": "alg_rabin_karp", "name": "Rabin-Karp",
            "description": "Počíta odtlačok každého úseku textu dĺžky m posúvaním okna. Znaky porovnáva len pri zhode odtlačkov.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)", "space": "O(1)",
            "note": "najhoršie O(n · m), keď sa odtlačky často zhodujú", "param": "dĺžka textu",
            "properties": ["hashing"],
            "code": '''
def solve(data, tracker):
    t, p = data["text"], data["pattern"]
    tracker.string(t, p)
    n, m = len(t), len(p)
    if m > n:
        return []
    base, mod = 256, 1_000_003
    high = pow(base, m - 1, mod)
    hp = ht = 0
    for i in range(m):
        hp = (hp * base + ord(p[i])) % mod
        ht = (ht * base + ord(t[i])) % mod
    out = []
    for s in range(n - m + 1):
        tracker.count("hash")
        tracker.shift(s, label=f"posun {s}: odtlačok úseku {ht}, vzorky {hp}")
        if ht == hp:
            j = 0
            while j < m and t[s + j] == p[j]:
                tracker.match(s + j, j)
                j += 1
            if j == m:
                out.append(s)
                tracker.found(s)
            else:
                tracker.mismatch(s + j, j)
        if s < n - m:
            ht = ((ht - ord(t[s]) * high) * base + ord(t[s + m])) % mod
    return out
''',
        },
    ],
    "experiments": [{
        "id": "exp_pattern", "name": "Vyhľadávanie vzorky na rôznych textoch",
        "algorithms": ["alg_naive_match", "alg_kmp", "alg_horspool", "alg_rabin_karp"],
        "generator": "gen_pattern", "sizes": [5000, 10000, 20000, 40000], "repeats": 3,
        "variants": [
            {"label": "náhodný text", "params": {"kind": "random"}},
            {"label": "aaa…a, vzorka aa…ab", "params": {"kind": "repetitive"}},
            {"label": "aaa…a, vzorka baa…a", "params": {"kind": "repetitive_front"}},
        ],
    }],
}

# ----------------------------------------------------------------------
#  Najdlhšia spoločná podpostupnosť
# ----------------------------------------------------------------------
GEN_LCS = '''
import random

def generate(n, alphabet="dna", seed=42):
    """Dva reťazce dĺžky n."""
    rnd = random.Random(seed)
    letters = {"dna": "ACGT", "binary": "01", "letters": "abcdefghijklmnopqrstuvwxyz"}[alphabet]
    a = "".join(rnd.choice(letters) for _ in range(n))
    b = "".join(rnd.choice(letters) for _ in range(n))
    return {"a": a, "b": b}
'''

LCS = {
    "id": "prob_lcs",
    "name": "Najdlhšia spoločná podpostupnosť",
    "summary": "Zisti dĺžku najdlhšej postupnosti znakov, ktorá sa v rovnakom poradí nachádza v oboch reťazcoch.",
    "description": (
        "Klasická úloha dynamického programovania (Cormen a kol., kapitola 15). Rekurzia bez "
        "pamäte rieši tie isté dvojice predpôn znova a znova. Tabuľka L[i][j] s dĺžkou LCS "
        "predpôn a[:i] a b[:j] sa vypĺňa po riadkoch v čase O(n · m)."
    ),
    "category": "dynamic_programming",
    "input_type": "string",
    "renderer": "grid",
    "input_description": "Objekt {\"a\": reťazec, \"b\": reťazec}.",
    "output_description": "Dĺžka najdlhšej spoločnej podpostupnosti.",
    "tags": ["mimo-kurzu"],
    "reference": "alg_lcs_dp",
    "generators": [{
        "id": "gen_lcs", "name": "Dva reťazce", "code": GEN_LCS,
        "description": "Náhodné reťazce nad abecedou DNA, 0 a 1 alebo malých písmen.",
        "sizes": [4, 6, 8, 10, 11], "viz_size": 7, "test_size": 8,
        "params": [enum("alphabet", "Abeceda", {"dna": "A, C, G, T", "binary": "0 a 1",
                                                 "letters": "26 malých písmen"}, "dna")],
    }],
    "algorithms": [
        {
            "id": "alg_lcs_naive", "name": "Rekurzia bez pamäte", "viz": False,
            "description": "Ak sa posledné znaky zhodujú, pridá 1 a skráti oba reťazce. Inak skúsi skrátiť jeden alebo druhý.",
            "paradigm": "recursive", "best": "O(n)", "avg": "other", "worst": "other", "space": "O(n)",
            "note": "najhoršie O(2^(n+m)), pri n = m rastie ako 4ⁿ", "param": "dĺžka reťazcov",
            "properties": ["recursive"],
            "code": '''
def solve(data, tracker):
    a, b = data["a"], data["b"]

    def lcs(i, j):
        tracker.count("call")
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return lcs(i - 1, j - 1) + 1
        return max(lcs(i - 1, j), lcs(i, j - 1))

    return lcs(len(a), len(b))
''',
        },
        {
            "id": "alg_lcs_memo", "name": "Rekurzia s memoizáciou",
            "description": "Rovnaká rekurzia, výsledok pre každú dvojicu (i, j) sa vypočíta len raz.",
            "paradigm": "dynamic_programming", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "O(n · m)", "param": "dĺžka reťazcov", "properties": ["recursive"],
            "code": '''
def solve(data, tracker):
    a, b = data["a"], data["b"]
    tracker.grid(len(a) + 1, len(b) + 1, row_labels=["-"] + list(a), col_labels=["-"] + list(b))
    memo = {}

    def lcs(i, j):
        tracker.count("call")
        if (i, j) in memo:
            return memo[(i, j)]
        if i == 0 or j == 0:
            value = 0
        elif a[i - 1] == b[j - 1]:
            value = lcs(i - 1, j - 1) + 1
        else:
            value = max(lcs(i - 1, j), lcs(i, j - 1))
        memo[(i, j)] = value
        tracker.set_cell(i, j, value, label=f"L[{i}][{j}] = {value}")
        return value

    return lcs(len(a), len(b))
''',
        },
        {
            "id": "alg_lcs_dp", "name": "Tabuľka po riadkoch",
            "description": "L[i][j] = L[i-1][j-1] + 1 pri zhode znakov, inak väčšia z hodnôt L[i-1][j] a L[i][j-1].",
            "paradigm": "dynamic_programming", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "O(n · m)", "param": "dĺžka reťazcov",
            "code": '''
def solve(data, tracker):
    a, b = data["a"], data["b"]
    n, m = len(a), len(b)
    tracker.grid(n + 1, m + 1, row_labels=["-"] + list(a), col_labels=["-"] + list(b), fill=0)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                tracker.read_cell(i - 1, j - 1)
                L[i][j] = L[i - 1][j - 1] + 1
                tracker.set_cell(i, j, L[i][j], role="match", label=f"{a[i - 1]} = {b[j - 1]}, L[{i}][{j}] = {L[i][j]}")
            else:
                tracker.read_cell(i - 1, j)
                tracker.read_cell(i, j - 1)
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
                tracker.set_cell(i, j, L[i][j], label=f"{a[i - 1]} ≠ {b[j - 1]}, L[{i}][{j}] = {L[i][j]}")
    return L[n][m]
''',
        },
    ],
    "experiments": [
        {
            "id": "exp_lcs_small", "name": "Rekurzia oproti tabuľke",
            "algorithms": ["alg_lcs_naive", "alg_lcs_memo", "alg_lcs_dp"], "generator": "gen_lcs",
            "sizes": [4, 6, 8, 10, 11], "repeats": 3,
        },
        {
            "id": "exp_lcs_large", "name": "Memoizácia oproti tabuľke",
            "algorithms": ["alg_lcs_memo", "alg_lcs_dp"], "generator": "gen_lcs",
            "sizes": [100, 200, 400, 600, 800], "repeats": 3,
        },
    ],
}

PROBLEMS = [SEARCH, SSSP, MST, PATTERN, LCS]
