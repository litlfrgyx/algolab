"""Prehľadávanie binárneho stromu z cvičenia 6 ÚSaA."""

from __future__ import annotations

from .common import GEN_TREE, TREE_SHAPES, enum

TREE_INPUT = (
    "Strom v reprezentácii z cvičenia 6: values[i] je hodnota uzla i, left[i] a right[i] "
    "sú indexy potomkov, 0 znamená prázdny podstrom. Koreň je uzol root."
)


def _gen(gid: str) -> dict:
    return {
        "id": gid, "name": "Binárny strom", "code": GEN_TREE,
        "description": "Náhodný, vyvážený alebo zdegenerovaný strom s n uzlami.",
        "sizes": [500, 1000, 2000, 4000, 8000], "viz_size": 12,
        "params": [enum("shape", "Tvar stromu", TREE_SHAPES, "random")],
    }


PREORDER = {
    "id": "prob_preorder",
    "name": "Preorder prehľadávanie",
    "summary": "Navštív koreň, potom ľavý a nakoniec pravý podstrom.",
    "description": (
        "Úloha z cvičenia 6. Rekurzívna verzia nechá prácu na zásobník volaní, nerekurzívna "
        "používa vlastný zásobník. Obe navštívia každý uzol raz, rozdiel je v pamäti a v tom, "
        "že rekurzia na hlbokom strome narazí na limit hĺbky."
    ),
    "category": "traversal",
    "input_type": "tree",
    "renderer": "tree",
    "input_description": TREE_INPUT,
    "output_description": "Zoznam hodnôt uzlov v poradí preorder.",
    "tags": ["usaa", "cv6"],
    "reference": "alg_pre_rec",
    "generators": [_gen("gen_tree_pre")],
    "algorithms": [
        {
            "id": "alg_pre_rec", "name": "Preorder rekurzívne",
            "description": "visit(uzol): spracuj uzol, visit(ľavý), visit(pravý).",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "hĺbka rekurzie = výška stromu", "param": "počet uzlov", "properties": ["recursive"],
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    order = []

    def visit(i):
        if i == 0:
            return
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}")
        visit(left[i])
        visit(right[i])

    visit(tree["root"])
    return order
''',
        },
        {
            "id": "alg_pre_stack", "name": "Preorder so zásobníkom",
            "description": "Zásobník nahrádza rekurziu: vyber uzol, spracuj ho a vlož najprv pravého, potom ľavého potomka.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "počet uzlov",
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    order = []
    stack = [tree["root"]]
    while stack:
        i = stack.pop()
        if i == 0:
            continue
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}, v zásobníku {len(stack)}")
        stack.append(right[i])
        stack.append(left[i])
    return order
''',
        },
    ],
    "experiments": [{
        "id": "exp_preorder", "name": "Rekurzia oproti vlastnému zásobníku",
        "algorithms": ["alg_pre_rec", "alg_pre_stack"], "generator": "gen_tree_pre",
        "sizes": [500, 1000, 2000, 4000, 8000], "repeats": 3,
        "variants": [
            {"label": "náhodný strom", "params": {"shape": "random"}},
            {"label": "zdegenerovaný strom", "params": {"shape": "degenerate"}},
        ],
    }],
}

INORDER = {
    "id": "prob_inorder",
    "name": "Inorder prehľadávanie",
    "summary": "Navštív ľavý podstrom, potom koreň a nakoniec pravý podstrom.",
    "description": (
        "Úloha z cvičenia 6. Pri binárnom vyhľadávacom strome dáva inorder zoradené kľúče. "
        "Nerekurzívna verzia ide po ľavej vetve čo najhlbšie a uzly si ukladá na zásobník."
    ),
    "category": "traversal",
    "input_type": "tree",
    "renderer": "tree",
    "input_description": TREE_INPUT,
    "output_description": "Zoznam hodnôt uzlov v poradí inorder.",
    "tags": ["usaa", "cv6"],
    "reference": "alg_in_rec",
    "generators": [_gen("gen_tree_in")],
    "algorithms": [
        {
            "id": "alg_in_rec", "name": "Inorder rekurzívne",
            "description": "visit(uzol): visit(ľavý), spracuj uzol, visit(pravý).",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "počet uzlov", "properties": ["recursive"],
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    order = []

    def visit(i):
        if i == 0:
            return
        visit(left[i])
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}")
        visit(right[i])

    visit(tree["root"])
    return order
''',
        },
        {
            "id": "alg_in_stack", "name": "Inorder so zásobníkom",
            "description": "Ide doľava a ukladá uzly na zásobník. Keď vľavo nič nie je, vyberie uzol, spracuje ho a pokračuje vpravo.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "počet uzlov",
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    order, stack = [], []
    i = tree["root"]
    while stack or i != 0:
        while i != 0:
            stack.append(i)
            tracker.focus(i, "compare", label=f"vlož {values[i]} na zásobník")
            i = left[i]
        i = stack.pop()
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}")
        i = right[i]
    return order
''',
        },
    ],
    "experiments": [{
        "id": "exp_inorder", "name": "Inorder rekurzívne a so zásobníkom",
        "algorithms": ["alg_in_rec", "alg_in_stack"], "generator": "gen_tree_in",
        "sizes": [500, 1000, 2000, 4000, 8000], "repeats": 3,
    }],
}

POSTORDER = {
    "id": "prob_postorder",
    "name": "Postorder prehľadávanie",
    "summary": "Navštív ľavý a pravý podstrom a až nakoniec koreň.",
    "description": (
        "Úloha z cvičenia 6. Nerekurzívna verzia s dvoma zásobníkmi najprv vytvorí poradie "
        "koreň, pravý, ľavý a druhý zásobník ho otočí."
    ),
    "category": "traversal",
    "input_type": "tree",
    "renderer": "tree",
    "input_description": TREE_INPUT,
    "output_description": "Zoznam hodnôt uzlov v poradí postorder.",
    "tags": ["usaa", "cv6"],
    "reference": "alg_post_rec",
    "generators": [_gen("gen_tree_post")],
    "algorithms": [
        {
            "id": "alg_post_rec", "name": "Postorder rekurzívne",
            "description": "visit(uzol): visit(ľavý), visit(pravý), spracuj uzol.",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "počet uzlov", "properties": ["recursive"],
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    order = []

    def visit(i):
        if i == 0:
            return
        visit(left[i])
        visit(right[i])
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}")

    visit(tree["root"])
    return order
''',
        },
        {
            "id": "alg_post_two_stacks", "name": "Postorder s dvoma zásobníkmi",
            "description": "Prvý zásobník vytvorí poradie koreň, pravý, ľavý. Druhý ho otočí na ľavý, pravý, koreň.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "počet uzlov",
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    first, second = [tree["root"]], []
    while first:
        i = first.pop()
        if i == 0:
            continue
        second.append(i)
        tracker.focus(i, "compare", label=f"presuň {values[i]} na druhý zásobník")
        first.append(left[i])
        first.append(right[i])
    order = []
    while second:
        i = second.pop()
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}")
    return order
''',
        },
    ],
    "experiments": [{
        "id": "exp_postorder", "name": "Postorder rekurzívne a s dvoma zásobníkmi",
        "algorithms": ["alg_post_rec", "alg_post_two_stacks"], "generator": "gen_tree_post",
        "sizes": [500, 1000, 2000, 4000, 8000], "repeats": 3,
    }],
}

LEVELORDER = {
    "id": "prob_levelorder",
    "name": "Level-order prehľadávanie",
    "summary": "Navštív uzly po úrovniach, zhora nadol a zľava doprava.",
    "description": (
        "Úloha z cvičenia 6. S frontom stačí každý uzol navštíviť raz. Verzia bez frontu "
        "(levelorderNQ) prechádza strom od koreňa zvlášť pre každú úroveň, preto stojí najviac O(n · h). "
        "Na vyváženom strome je väčšina uzlov v posledných úrovniach, takže spolu vyjde len O(n). "
        "Na zdegenerovanom strome je to O(n²)."
    ),
    "category": "traversal",
    "input_type": "tree",
    "renderer": "tree",
    "input_description": TREE_INPUT,
    "output_description": "Zoznam hodnôt uzlov po úrovniach.",
    "tags": ["usaa", "cv6"],
    "reference": "alg_level_queue",
    "generators": [_gen("gen_tree_level")],
    "algorithms": [
        {
            "id": "alg_level_queue", "name": "Level-order s frontom",
            "description": "Front drží uzly, ktoré čakajú na spracovanie. Po spracovaní uzla sa do frontu pridajú jeho potomkovia.",
            "paradigm": "iterative", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "param": "počet uzlov",
            "code": '''
from collections import deque


def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")
    order = []
    queue = deque([tree["root"]])
    while queue:
        i = queue.popleft()
        if i == 0:
            continue
        tracker.count("visit")
        order.append(values[i])
        tracker.mark_node(i, "visited")
        tracker.focus(i, "active", label=f"spracuj {values[i]}, vo fronte {len(queue)}")
        queue.append(left[i])
        queue.append(right[i])
    return order
''',
        },
        {
            "id": "alg_level_nq", "name": "Level-order bez frontu (levelorderNQ)",
            "description": "Zistí výšku stromu a pre každú úroveň znova prejde strom od koreňa až po túto úroveň.",
            "paradigm": "recursive", "best": "O(n)", "avg": "O(n log n)", "worst": "O(n^2)", "space": "O(n)",
            "note": "najviac O(n · h), h je výška stromu. Vyvážený strom O(n), reťaz O(n²)", "param": "počet uzlov", "properties": ["recursive"],
            "code": '''
def solve(tree, tracker):
    values, left, right = tree["values"], tree["left"], tree["right"]
    tracker.tree_arrays(values, left, right, tree["root"], label="vstupný strom")

    def height(i):
        if i == 0:
            return 0
        return 1 + max(height(left[i]), height(right[i]))

    order = []

    def level(i, depth):
        if i == 0:
            return
        tracker.count("visit")
        if depth == 1:
            order.append(values[i])
            tracker.mark_node(i, "visited")
            tracker.focus(i, "active", label=f"spracuj {values[i]}")
        else:
            tracker.focus(i, "compare", label=f"prechádzam cez {values[i]}")
            level(left[i], depth - 1)
            level(right[i], depth - 1)

    for d in range(1, height(tree["root"]) + 1):
        level(tree["root"], d)
    return order
''',
        },
    ],
    "experiments": [{
        "id": "exp_levelorder", "name": "Front oproti prechodu po úrovniach",
        "algorithms": ["alg_level_queue", "alg_level_nq"], "generator": "gen_tree_level",
        "sizes": [250, 500, 1000, 2000, 4000], "repeats": 3,
        "variants": [
            {"label": "vyvážený strom", "params": {"shape": "balanced"}},
            {"label": "zdegenerovaný strom", "params": {"shape": "degenerate"}},
        ],
    }],
}

PROBLEMS = [PREORDER, INORDER, POSTORDER, LEVELORDER]
