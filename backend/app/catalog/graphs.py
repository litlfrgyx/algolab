"""Prehľadávanie grafu z cvičení 10 a 11 ÚSaA."""

from __future__ import annotations

from .common import GEN_GRAPH, GRAPH_KINDS, enum

GRAPH_INPUT = (
    "Neorientovaný graf: n je počet vrcholov 0 .. n-1, edges je zoznam hrán [u, v] "
    "a start je vrchol, z ktorého sa začína."
)


def _gen(gid: str, sizes: list[int], default: str = "sparse") -> dict:
    return {
        "id": gid, "name": "Náhodný graf", "code": GEN_GRAPH,
        "description": "Riedky, hustý, mriežkový, cestový alebo nesúvislý graf s n vrcholmi.",
        "sizes": sizes, "viz_size": 12,
        "params": [enum("kind", "Druh grafu", GRAPH_KINDS, default)],
    }


ADJ_LIST = '''
    adj = [[] for _ in range(g["n"])]
    for u, v, *_ in g["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    for row in adj:
        row.sort()
'''

CHECK_TRAVERSAL = '''
def check(input, output, expected=None):
    """Poradie musí obsahovať každý dosiahnuteľný vrchol práve raz a začínať vo vrchole start.

    Každý ďalší vrchol musí susediť s niektorým skôr navštíveným vrcholom.
    Táto podmienka platí pre prehľadávanie do hĺbky aj do šírky.
    """
    n, start = input["n"], input["start"]
    adj = [set() for _ in range(n)]
    for u, v, *_ in input["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    if not isinstance(output, list) or not output:
        return False, "Výstup má byť neprázdny zoznam vrcholov"
    if output[0] != start:
        return False, f"Prehľadávanie má začať vo vrchole {start}, začína v {output[0]}"
    if len(set(output)) != len(output):
        return False, "Niektorý vrchol je v poradí viackrát"
    if set(output) != seen:
        missing = sorted(seen - set(output))[:5]
        if missing:
            return False, f"Chýbajú dosiahnuteľné vrcholy, napríklad {missing}"
        return False, "Poradie obsahuje vrchol, ktorý nie je dosiahnuteľný"
    done = {start}
    for v in output[1:]:
        if not adj[v] & done:
            return False, f"Vrchol {v} nesusedí so žiadnym skôr navštíveným vrcholom"
        done.add(v)
    return True
'''

TRAVERSAL = {
    "id": "prob_graph_traversal",
    "name": "Prehľadanie grafu",
    "summary": "Navštív všetky vrcholy dosiahnuteľné zo štartového vrchola.",
    "description": (
        "Úloha z cvičenia 10. Prehľadávanie do hĺbky (DFS) ide čo najďalej po jednej ceste, "
        "prehľadávanie do šírky (BFS) spracúva vrcholy podľa vzdialenosti od štartu. Pri "
        "zozname susedov stojí každé z nich O(n + m). Matica susednosti vyžaduje O(n²) "
        "bez ohľadu na počet hrán, čo je vidieť hlavne na riedkych grafoch."
    ),
    "category": "graph",
    "input_type": "graph",
    "renderer": "graph",
    "input_description": GRAPH_INPUT,
    "output_description": "Zoznam vrcholov v poradí, v akom ich algoritmus navštívil.",
    "tags": ["usaa", "cv10"],
    "checker": CHECK_TRAVERSAL,
    "generators": [_gen("gen_graph_trav", [250, 500, 1000, 2000, 4000])],
    "algorithms": [
        {
            "id": "alg_dfs_rec", "name": "DFS rekurzívne",
            "description": "Navštívi vrchol a rekurzívne pokračuje do každého nenavštíveného suseda.",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(n + m), m je počet hrán. V riedkom grafe m ≈ 3n, v hustom m rastie ako n²", "param": "počet vrcholov",
            "properties": ["recursive"],
            "code": '''
def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    seen = [False] * g["n"]
    order = []

    def dfs(u):
        seen[u] = True
        order.append(u)
        tracker.visit(u)
        for v in adj[u]:
            if not seen[v]:
                tracker.edge(u, v, "tree", label=f"z {u} pokračuj do {v}")
                dfs(v)
            else:
                tracker.edge(u, v, "compare", label=f"{v} už je navštívený")

    dfs(g["start"])
    return order
''',
        },
        {
            "id": "alg_dfs_stack", "name": "DFS so zásobníkom",
            "description": "Vlastný zásobník nahrádza rekurziu. Vrchol sa označí ako navštívený až pri výbere zo zásobníka.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "O(n + m), zásobník môže obsahovať vrchol viackrát", "param": "počet vrcholov",
            "code": '''
def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    seen = [False] * g["n"]
    order = []
    stack = [g["start"]]
    while stack:
        tracker.frontier(stack, "zásobník")
        u = stack.pop()
        if seen[u]:
            continue
        seen[u] = True
        order.append(u)
        tracker.visit(u)
        for v in reversed(adj[u]):
            if not seen[v]:
                tracker.edge(u, v, "compare", label=f"vlož {v} na zásobník")
                stack.append(v)
    tracker.frontier([], "zásobník")
    return order
''',
        },
        {
            "id": "alg_bfs", "name": "BFS so zoznamom susedov",
            "description": "Front drží objavené vrcholy. Vrcholy sa spracúvajú v poradí, v akom boli objavené.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(n + m), m je počet hrán. V riedkom grafe m ≈ 3n, v hustom m rastie ako n²", "param": "počet vrcholov",
            "code": '''
from collections import deque


def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    seen = [False] * g["n"]
    seen[g["start"]] = True
    order = []
    queue = deque([g["start"]])
    while queue:
        tracker.frontier(queue, "front")
        u = queue.popleft()
        order.append(u)
        tracker.visit(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                queue.append(v)
                tracker.edge(u, v, "tree", label=f"objav {v} a pridaj ho do frontu")
            else:
                tracker.edge(u, v, "compare", label=f"{v} už bol objavený")
    tracker.frontier([], "front")
    return order
''',
        },
        {
            "id": "alg_bfs_matrix", "name": "BFS s maticou susednosti",
            "description": "Rovnaký postup ako BFS, ale susedov hľadá prechodom celého riadka matice.",
            "paradigm": "iterative", "best": "O(n^2)", "avg": "O(n^2)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "nezávisí od počtu hrán", "param": "počet vrcholov",
            "code": '''
from collections import deque


def solve(g, tracker):
    n = g["n"]
    tracker.graph(n, g["edges"])
    matrix = [[False] * n for _ in range(n)]
    for u, v, *_ in g["edges"]:
        matrix[u][v] = matrix[v][u] = True
    seen = [False] * n
    seen[g["start"]] = True
    order = []
    queue = deque([g["start"]])
    while queue:
        tracker.frontier(queue, "front")
        u = queue.popleft()
        order.append(u)
        tracker.visit(u)
        row = matrix[u]
        for v in range(n):
            tracker.count("matrix_read")
            if row[v] and not seen[v]:
                seen[v] = True
                queue.append(v)
                tracker.edge(u, v, "tree", label=f"objav {v} a pridaj ho do frontu")
    tracker.frontier([], "front")
    return order
''',
        },
    ],
    "experiments": [{
        "id": "exp_graph_traversal", "name": "Zoznam susedov oproti matici",
        "algorithms": ["alg_dfs_rec", "alg_dfs_stack", "alg_bfs", "alg_bfs_matrix"],
        "generator": "gen_graph_trav", "sizes": [250, 500, 1000, 2000], "repeats": 3,
        "variants": [
            {"label": "riedky graf", "params": {"kind": "sparse"}},
            {"label": "hustý graf", "params": {"kind": "dense"}},
        ],
    }],
}

CHECK_FOREST = '''
def check(input, output, expected=None):
    """Výstup musí byť kostrový les: hrany grafu bez cyklu, ktoré spoja každý komponent."""
    n = input["n"]
    graph_edges = {(min(u, v), max(u, v)) for u, v, *_ in input["edges"]}
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v, *_ in input["edges"]:
        parent[find(u)] = find(v)
    components = len({find(v) for v in range(n)})
    if not isinstance(output, list):
        return False, "Výstup má byť zoznam hrán"
    if len(output) != n - components:
        return False, f"Kostrový les má mať {n - components} hrán, výstup má {len(output)}"
    parent = list(range(n))
    for e in output:
        u, v = e[0], e[1]
        if (min(u, v), max(u, v)) not in graph_edges:
            return False, f"Hrana {u}-{v} nie je v grafe"
        ru, rv = find(u), find(v)
        if ru == rv:
            return False, f"Hrana {u}-{v} vytvára cyklus"
        parent[ru] = rv
    return True
'''

FOREST = {
    "id": "prob_spanning_forest",
    "name": "Kostrový les grafu",
    "summary": "Vyber hrany, ktoré spoja každý komponent grafu a nevytvoria cyklus.",
    "description": (
        "Úloha z cvičenia 11. Hrany, po ktorých prehľadávanie objaví nový vrchol, tvoria "
        "kostru komponentu. Ak sa prehľadávanie spustí z každého ešte nenavštíveného vrchola, "
        "vznikne kostrový les celého grafu. DFS a BFS dajú rôzne kostry, obe sú správne."
    ),
    "category": "graph",
    "input_type": "graph",
    "renderer": "graph",
    "input_description": GRAPH_INPUT + " Vrchol start sa tu nepoužíva, les pokrýva celý graf.",
    "output_description": "Zoznam hrán [u, v] kostrového lesa.",
    "tags": ["usaa", "cv11"],
    "checker": CHECK_FOREST,
    "generators": [_gen("gen_graph_forest", [250, 500, 1000, 2000, 4000], "disconnected")],
    "algorithms": [
        {
            "id": "alg_forest_dfs", "name": "Kostrový les pomocou DFS",
            "description": "Z každého nenavštíveného vrchola spustí DFS so zásobníkom a uloží hrany, po ktorých objavil nový vrchol.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n^2)", "note": "O(n + m)", "param": "počet vrcholov",
            "code": '''
def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    seen = [False] * g["n"]
    forest = []
    for s in range(g["n"]):
        if seen[s]:
            continue
        stack = [(s, -1)]
        while stack:
            u, p = stack.pop()
            if seen[u]:
                continue
            seen[u] = True
            if p >= 0:
                forest.append([p, u])
                tracker.edge(p, u, "tree", label=f"hrana {p}-{u} patrí do lesa")
            tracker.visit(u)
            for v in reversed(adj[u]):
                if not seen[v]:
                    stack.append((v, u))
    return forest
''',
        },
        {
            "id": "alg_forest_bfs", "name": "Kostrový les pomocou BFS",
            "description": "Z každého nenavštíveného vrchola spustí BFS. Hrana, po ktorej sa vrchol objaví, patrí do lesa.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(n + m)", "param": "počet vrcholov",
            "code": '''
from collections import deque


def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    seen = [False] * g["n"]
    forest = []
    for s in range(g["n"]):
        if seen[s]:
            continue
        seen[s] = True
        queue = deque([s])
        while queue:
            u = queue.popleft()
            tracker.visit(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    forest.append([u, v])
                    queue.append(v)
                    tracker.edge(u, v, "tree", label=f"hrana {u}-{v} patrí do lesa")
    return forest
''',
        },
    ],
    "experiments": [{
        "id": "exp_spanning_forest", "name": "Kostrový les cez DFS a BFS",
        "algorithms": ["alg_forest_dfs", "alg_forest_bfs"], "generator": "gen_graph_forest",
        "sizes": [500, 1000, 2000, 4000], "repeats": 3,
    }],
}

SHORTEST = {
    "id": "prob_unweighted_sp",
    "name": "Najkratšie cesty v neváženom grafe",
    "summary": "Zisti počet hrán na najkratšej ceste zo štartu do každého vrchola.",
    "description": (
        "Úloha z cvičenia 11. BFS spracúva vrcholy po vrstvách, preto prvé objavenie vrchola "
        "dá najkratšiu vzdialenosť. DFS je tu zámerne zaradené ako nesprávne riešenie: hĺbka "
        "vrchola v strome DFS nemusí byť najkratšia vzdialenosť. Kontrola správnosti to ukáže."
    ),
    "category": "graph",
    "input_type": "graph",
    "renderer": "graph",
    "input_description": GRAPH_INPUT,
    "output_description": "Zoznam dist, kde dist[v] je počet hrán najkratšej cesty, -1 pre nedosiahnuteľný vrchol.",
    "tags": ["usaa", "cv11"],
    "reference": "alg_sp_bfs",
    "checker": '''
def check(input, output, expected=None):
    """Porovná vzdialenosti s výsledkom referenčného BFS."""
    if not isinstance(output, list) or len(output) != input["n"]:
        return False, "Výstup má mať jednu vzdialenosť pre každý vrchol"
    for v, (a, b) in enumerate(zip(output, expected)):
        if a != b:
            return False, f"Vrchol {v}: vzdialenosť {a}, správne je {b}"
    return True
''',
    "generators": [_gen("gen_graph_sp", [250, 500, 1000, 2000, 4000])],
    "algorithms": [
        {
            "id": "alg_sp_bfs", "name": "BFS (vzdialenosti po vrstvách)",
            "description": "Vzdialenosť suseda je o jedna väčšia ako vzdialenosť vrchola, z ktorého bol objavený.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(n + m)", "param": "počet vrcholov",
            "code": '''
from collections import deque


def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    dist = [-1] * g["n"]
    dist[g["start"]] = 0
    tracker.node_label(g["start"], 0)
    queue = deque([g["start"]])
    while queue:
        tracker.frontier(queue, "front")
        u = queue.popleft()
        tracker.visit(u)
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                tracker.node_label(v, dist[v])
                tracker.edge(u, v, "tree", label=f"dist[{v}] = {dist[v]}")
                queue.append(v)
    tracker.frontier([], "front")
    return dist
''',
        },
        {
            "id": "alg_sp_dfs_wrong", "name": "DFS (zámerne nesprávne)",
            "description": "Vzdialenosť počíta ako hĺbku v strome DFS. Na grafe s cyklami dáva často dlhšie cesty.",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(n + m)", "param": "počet vrcholov",
            "properties": ["recursive", "intentionally_incorrect"],
            "code": '''
def solve(g, tracker):
    tracker.graph(g["n"], g["edges"])
''' + ADJ_LIST + '''
    dist = [-1] * g["n"]

    def dfs(u, d):
        dist[u] = d
        tracker.node_label(u, d)
        tracker.visit(u)
        for v in adj[u]:
            if dist[v] < 0:
                tracker.edge(u, v, "tree", label=f"hĺbka {v} je {d + 1}")
                dfs(v, d + 1)

    dfs(g["start"], 0)
    return dist
''',
        },
    ],
    "experiments": [{
        "id": "exp_unweighted_sp", "name": "BFS oproti DFS pri vzdialenostiach",
        "algorithms": ["alg_sp_bfs", "alg_sp_dfs_wrong"], "generator": "gen_graph_sp",
        "sizes": [250, 500, 1000, 2000], "repeats": 3,
    }],
}

PROBLEMS = [TRAVERSAL, FOREST, SHORTEST]
