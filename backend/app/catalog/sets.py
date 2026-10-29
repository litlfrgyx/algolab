"""Implementácie množiny: zoznam, stromy a hašovacie tabuľky."""

from __future__ import annotations

from .common import enum

SET_MODES = {
    "random": "náhodné vkladanie, hľadanie a mazanie",
    "sorted": "kľúče vkladané vzostupne",
    "collisions": "násobky 1009 (kolízie v tabuľke s m = 1009)",
    "deletes": "najprv vkladanie, potom veľa mazania",
}

GEN_SET_OPS = '''
import random

def generate(n, mode="random", seed=42):
    """n operácií nad množinou: ["insert", x], ["find", x] alebo ["delete", x]."""
    rnd = random.Random(seed)
    ops = []
    if mode == "sorted":
        half = n // 2
        for x in range(half):
            ops.append(["insert", 2 * x])
        for _ in range(n - half):
            ops.append(["find", rnd.randrange(0, 2 * half + 2)])
        return ops
    if mode == "deletes":
        keys = rnd.sample(range(4 * n + 4), n // 2)
        for x in keys:
            ops.append(["insert", x])
        rnd.shuffle(keys)
        for i in range(n - len(keys)):
            if i % 3 == 2:
                ops.append(["find", rnd.choice(keys)])
            else:
                ops.append(["delete", keys[i % len(keys)]])
        return ops
    scale = 1009 if mode == "collisions" else 1
    present = []
    for _ in range(n):
        r = rnd.random()
        if r < 0.6 or not present:
            x = rnd.randrange(0, 2 * n + 1) * scale
            if x not in present:
                present.append(x)
            ops.append(["insert", x])
        elif r < 0.8:
            ops.append(["find", rnd.choice(present) if rnd.random() < 0.6 else rnd.randrange(0, 2 * n + 1) * scale])
        else:
            ops.append(["delete", present.pop(rnd.randrange(len(present)))])
    return ops
'''

CHECK_SET = '''
def check(input, output, expected=None):
    """Výsledky hľadaní a výsledný obsah sa porovnajú so zabudovanou množinou Pythonu."""
    s = set()
    found = []
    for op, x in input:
        if op == "insert":
            s.add(x)
        elif op == "delete":
            s.discard(x)
        else:
            found.append(x in s)
    if not isinstance(output, dict):
        return False, "Výstup má byť objekt s kľúčmi found a items"
    got = output.get("found")
    if got != found:
        if not isinstance(got, list) or len(got) != len(found):
            return False, f"Očakávaných {len(found)} výsledkov hľadania"
        k = next(i for i, (a, b) in enumerate(zip(got, found)) if a != b)
        return False, f"Hľadanie číslo {k + 1}: výsledok {got[k]}, správne je {found[k]}"
    items = sorted(s)
    if output.get("items") != items:
        return False, f"Výsledná množina má mať {len(items)} prvkov, obsah sa nezhoduje"
    return True
'''

RUN_OPS = '''
    found = []
    for op, x in ops:
        if op == "insert":
            insert(x)
        elif op == "delete":
            delete(x)
        else:
            found.append(find(x))
'''

SET_OPS = {
    "id": "prob_set_ops",
    "name": "Operácie nad množinou",
    "summary": "Vykonaj postupnosť vkladaní, hľadaní a mazaní a vráť výsledky hľadaní.",
    "description": (
        "Rovnakú množinu možno uložiť do neusporiadaného zoznamu, "
        "binárneho vyhľadávacieho stromu, vyváženého AVL stromu, 2-3 stromu alebo hašovacej "
        "tabuľky. Zoznam stojí O(n) na operáciu. Nevyvážený strom degeneruje pri vzostupne "
        "vkladaných kľúčoch. Hašovacia tabuľka je v priemere najrýchlejšia, ale pri zlých "
        "kľúčoch sa všetko ocitne v jednom zozname."
    ),
    "category": "set",
    "input_type": "operations",
    "renderer": "tree",
    "input_description": "Zoznam operácií [\"insert\", x], [\"find\", x] alebo [\"delete\", x], x je nezáporné celé číslo.",
    "output_description": "Objekt {\"found\": výsledky hľadaní v poradí, \"items\": zoradený obsah množiny na konci}.",
    "checker": CHECK_SET,
    "generators": [{
        "id": "gen_set_ops", "name": "Postupnosť operácií", "code": GEN_SET_OPS,
        "description": "Náhodné operácie, vzostupné kľúče, kolízne kľúče alebo veľa mazaní.",
        "sizes": [250, 500, 1000, 2000, 4000], "viz_size": 24,
        "params": [enum("mode", "Druh operácií", SET_MODES, "random")],
    }],
    "algorithms": [
        {
            "id": "alg_set_list", "name": "Unsorted list", "viz": False,
            "description": "Prvky sú v zozname v poradí vloženia. Hľadanie prechádza zoznam od začiatku.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(n) na operáciu, n je počet operácií", "param": "počet operácií",
            "code": '''
def solve(ops, tracker):
    items = []

    def index(x):
        for i, y in enumerate(items):
            tracker.count("compare")
            if y == x:
                return i
        return -1

    def find(x):
        return index(x) >= 0

    def insert(x):
        if index(x) < 0:
            items.append(x)

    def delete(x):
        i = index(x)
        if i >= 0:
            items[i] = items[-1]
            items.pop()
''' + RUN_OPS + '''
    return {"found": found, "items": sorted(items)}
''',
        },
        {
            "id": "alg_set_bst", "name": "Binary search tree",
            "description": "Menšie kľúče idú doľava, väčšie doprava. Mazanie uzla s dvoma potomkami ho nahradí najmenším kľúčom pravého podstromu.",
            "paradigm": "data_structure", "best": "O(n log n)", "avg": "O(n log n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "O(h) na operáciu, pri vzostupných kľúčoch h = n", "param": "počet operácií",
            "code": '''
class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def solve(ops, tracker):
    root = None

    def find(x):
        node = root
        while node is not None:
            tracker.count("compare")
            tracker.focus(node.key, "compare", label=f"hľadám {x}, porovnám s {node.key}")
            if x == node.key:
                tracker.focus(node.key, "active", label=f"{x} nájdené")
                return True
            node = node.left if x < node.key else node.right
        return False

    def insert(x):
        nonlocal root
        if root is None:
            root = Node(x)
            tracker.tree(root, label=f"vlož {x} ako koreň")
            return
        node = root
        while True:
            tracker.count("compare")
            tracker.focus(node.key, "compare", label=f"vkladám {x}, porovnám s {node.key}")
            if x == node.key:
                return
            if x < node.key:
                if node.left is None:
                    node.left = Node(x)
                    break
                node = node.left
            else:
                if node.right is None:
                    node.right = Node(x)
                    break
                node = node.right
        tracker.tree(root, label=f"vlož {x}")

    def delete(x):
        nonlocal root
        parent, node = None, root
        while node is not None and node.key != x:
            tracker.count("compare")
            parent, node = node, (node.left if x < node.key else node.right)
        if node is None:
            return
        if node.left is not None and node.right is not None:
            sp, s = node, node.right
            while s.left is not None:
                tracker.count("compare")
                sp, s = s, s.left
            tracker.focus(s.key, "pivot", label=f"{x} nahradím nasledovníkom {s.key}")
            node.key = s.key
            parent, node = sp, s
        child = node.left if node.left is not None else node.right
        if parent is None:
            root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child
        tracker.tree(root, label=f"vymaž {x}")
''' + RUN_OPS + '''
    items = []
    stack, node = [], root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        items.append(node.key)
        node = node.right
    return {"found": found, "items": items}
''',
        },
        {
            "id": "alg_set_avl", "name": "AVL tree",
            "description": "Binárny vyhľadávací strom, ktorý po každej zmene rotáciami udrží rozdiel výšok podstromov najviac 1.",
            "paradigm": "data_structure", "best": "O(n log n)", "avg": "O(n log n)", "worst": "O(n log n)",
            "space": "O(n)", "note": "O(log n) na operáciu", "param": "počet operácií",
            "properties": ["recursive"],
            "code": '''
class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1


def h(node):
    return node.height if node is not None else 0


def update(node):
    node.height = 1 + max(h(node.left), h(node.right))


def rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    update(y)
    update(x)
    return x


def rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    update(x)
    update(y)
    return y


def solve(ops, tracker):
    root = None

    def balance(node):
        update(node)
        diff = h(node.left) - h(node.right)
        if diff > 1:
            if h(node.left.left) < h(node.left.right):
                tracker.count("rotation")
                node.left = rotate_left(node.left)
            tracker.count("rotation")
            return rotate_right(node)
        if diff < -1:
            if h(node.right.right) < h(node.right.left):
                tracker.count("rotation")
                node.right = rotate_right(node.right)
            tracker.count("rotation")
            return rotate_left(node)
        return node

    def ins(node, x):
        if node is None:
            return Node(x)
        tracker.count("compare")
        tracker.focus(node.key, "compare", label=f"vkladám {x}, porovnám s {node.key}")
        if x < node.key:
            node.left = ins(node.left, x)
        elif x > node.key:
            node.right = ins(node.right, x)
        else:
            return node
        return balance(node)

    def remove_min(node):
        if node.left is None:
            return node.right, node.key
        node.left, key = remove_min(node.left)
        return balance(node), key

    def rem(node, x):
        if node is None:
            return None
        tracker.count("compare")
        if x < node.key:
            node.left = rem(node.left, x)
        elif x > node.key:
            node.right = rem(node.right, x)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            node.right, node.key = remove_min(node.right)
        return balance(node)

    def find(x):
        node = root
        while node is not None:
            tracker.count("compare")
            tracker.focus(node.key, "compare", label=f"hľadám {x}, porovnám s {node.key}")
            if x == node.key:
                return True
            node = node.left if x < node.key else node.right
        return False

    def insert(x):
        nonlocal root
        root = ins(root, x)
        tracker.tree(root, label=f"vlož {x} a vyváž strom", extra="height")

    def delete(x):
        nonlocal root
        root = rem(root, x)
        tracker.tree(root, label=f"vymaž {x} a vyváž strom", extra="height")
''' + RUN_OPS + '''
    items = []

    def walk(node):
        if node is not None:
            walk(node.left)
            items.append(node.key)
            walk(node.right)

    walk(root)
    return {"found": found, "items": items}
''',
        },
        {
            "id": "alg_set_23", "name": "2-3 tree",
            "description": "Uzol má jeden alebo dva kľúče a všetky listy sú v rovnakej hĺbke. Preplnený uzol sa rozdelí, podtečený si požičia kľúč od súrodenca alebo sa s ním zlúči.",
            "paradigm": "data_structure", "best": "O(n log n)", "avg": "O(n log n)", "worst": "O(n log n)",
            "space": "O(n)", "note": "O(log n) na operáciu", "param": "počet operácií",
            "properties": ["recursive"],
            "code": '''
class Node:
    def __init__(self, keys, children=None):
        self.keys = keys
        self.children = children or []


def position(node, x, tracker):
    i = 0
    while i < len(node.keys):
        tracker.count("compare")
        if x <= node.keys[i]:
            break
        i += 1
    return i


def solve(ops, tracker):
    root = None

    def show(label):
        tracker.tree(root, label=label)

    def find(x):
        node = root
        while node is not None:
            tracker.focus("|".join(str(k) for k in node.keys), "compare", label=f"hľadám {x} v uzle {node.keys}")
            i = position(node, x, tracker)
            if i < len(node.keys) and node.keys[i] == x:
                return True
            node = node.children[i] if node.children else None
        return False

    def ins(node, x):
        i = position(node, x, tracker)
        if i < len(node.keys) and node.keys[i] == x:
            return None
        if not node.children:
            node.keys.insert(i, x)
        else:
            split = ins(node.children[i], x)
            if split is None:
                return None
            mid, right = split
            node.keys.insert(i, mid)
            node.children.insert(i + 1, right)
        if len(node.keys) == 3:
            tracker.count("split")
            right = Node([node.keys[2]], node.children[2:])
            mid = node.keys[1]
            node.keys = [node.keys[0]]
            node.children = node.children[:2]
            return mid, right
        return None

    def insert(x):
        nonlocal root
        if root is None:
            root = Node([x])
        else:
            split = ins(root, x)
            if split is not None:
                mid, right = split
                root = Node([mid], [root, right])
        show(f"vlož {x}")

    def fix(parent, i):
        child = parent.children[i]
        if child.keys:
            return
        if i > 0 and len(parent.children[i - 1].keys) == 2:
            tracker.count("borrow")
            left = parent.children[i - 1]
            child.keys.insert(0, parent.keys[i - 1])
            parent.keys[i - 1] = left.keys.pop()
            if left.children:
                child.children.insert(0, left.children.pop())
        elif i + 1 < len(parent.children) and len(parent.children[i + 1].keys) == 2:
            tracker.count("borrow")
            right = parent.children[i + 1]
            child.keys.append(parent.keys[i])
            parent.keys[i] = right.keys.pop(0)
            if right.children:
                child.children.append(right.children.pop(0))
        elif i > 0:
            tracker.count("merge")
            left = parent.children[i - 1]
            left.keys.append(parent.keys.pop(i - 1))
            left.children.extend(child.children)
            parent.children.pop(i)
        else:
            tracker.count("merge")
            right = parent.children[1]
            right.keys.insert(0, parent.keys.pop(0))
            right.children[0:0] = child.children
            parent.children.pop(0)

    def rem(node, x):
        i = position(node, x, tracker)
        if i < len(node.keys) and node.keys[i] == x:
            if not node.children:
                node.keys.pop(i)
                return True
            pred = node.children[i]
            while pred.children:
                pred = pred.children[-1]
            node.keys[i] = pred.keys[-1]
            rem(node.children[i], node.keys[i])
            fix(node, i)
            return True
        if not node.children:
            return False
        found = rem(node.children[i], x)
        fix(node, i)
        return found

    def delete(x):
        nonlocal root
        if root is None:
            return
        rem(root, x)
        if not root.keys:
            root = root.children[0] if root.children else None
        show(f"vymaž {x}")
''' + RUN_OPS + '''
    items = []

    def walk(node):
        if node is None:
            return
        if not node.children:
            items.extend(node.keys)
            return
        for i, child in enumerate(node.children):
            walk(child)
            if i < len(node.keys):
                items.append(node.keys[i])

    walk(root)
    return {"found": found, "items": items}
''',
        },
        {
            "id": "alg_set_chain", "name": "Hashing with chaining (m = 1009)", "viz": False,
            "description": "Tabuľka má pevne 1009 políčok. Kľúče s rovnakou hodnotou x mod 1009 sú v spoločnom zozname.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "priemerne O(1 + n/m) na operáciu, pri kolíziách O(n)",
            "param": "počet operácií",
            "code": '''
M = 1009


def solve(ops, tracker):
    table = [[] for _ in range(M)]

    def find(x):
        for y in table[x % M]:
            tracker.count("compare")
            if y == x:
                return True
        return False

    def insert(x):
        tracker.count("hash")
        if not find(x):
            table[x % M].append(x)

    def delete(x):
        bucket = table[x % M]
        for i, y in enumerate(bucket):
            tracker.count("compare")
            if y == x:
                bucket[i] = bucket[-1]
                bucket.pop()
                return
''' + RUN_OPS + '''
    items = sorted(x for bucket in table for x in bucket)
    return {"found": found, "items": items}
''',
        },
        {
            "id": "alg_set_linear", "name": "Open addressing, linear probing", "viz": False,
            "description": "Pri kolízii skúša nasledujúce políčka. Zmazané políčko dostane značku, aby hľadanie nezastalo. Pri zaplnení nad polovicu sa tabuľka zväčší.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "zhluky kľúčov predlžujú skúšanie", "param": "počet operácií",
            "code": '''
DELETED = -1


def next_prime(k):
    k = max(k, 2)
    while True:
        if all(k % d for d in range(2, int(k ** 0.5) + 1)):
            return k
        k += 1


def solve(ops, tracker):
    m = 1009
    table = [None] * m
    size = 0
    tombs = 0

    def probe(x, i):
        return (x + i) % m

    def slot(x):
        """Index kľúča x alebo -1."""
        for i in range(m):
            j = probe(x, i)
            tracker.count("probe")
            if table[j] is None:
                return -1
            if table[j] == x:
                return j
        return -1

    def rehash():
        nonlocal m, table, tombs
        tracker.count("rehash")
        old = [y for y in table if y is not None and y != DELETED]
        m = next_prime(max(1009, 4 * (len(old) + 1)))
        table = [None] * m
        tombs = 0
        for y in old:
            i = 0
            while table[probe(y, i)] is not None:
                i += 1
            table[probe(y, i)] = y

    def find(x):
        return slot(x) >= 0

    def insert(x):
        nonlocal size, tombs
        if slot(x) >= 0:
            return
        if 2 * (size + tombs + 1) > m:
            rehash()
        i = 0
        while True:
            j = probe(x, i)
            tracker.count("probe")
            if table[j] is None or table[j] == DELETED:
                if table[j] == DELETED:
                    tombs -= 1
                table[j] = x
                size += 1
                return
            i += 1

    def delete(x):
        nonlocal size, tombs
        j = slot(x)
        if j >= 0:
            table[j] = DELETED
            size -= 1
            tombs += 1
''' + RUN_OPS + '''
    items = sorted(y for y in table if y is not None and y != DELETED)
    return {"found": found, "items": items}
''',
        },
        {
            "id": "alg_set_quadratic", "name": "Open addressing, quadratic probing", "viz": False,
            "description": "Pri kolízii skúša políčka vo vzdialenosti 1, 4, 9, 16 a ďalej. Tým sa zmenšia zhluky. Veľkosť tabuľky je prvočíslo a zaplnenie najviac polovica.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n^2)",
            "space": "O(n)", "note": "prvočíselné m a zaplnenie do 1/2 zaručia voľné políčko",
            "param": "počet operácií",
            "code": '''
DELETED = -1


def next_prime(k):
    k = max(k, 2)
    while True:
        if all(k % d for d in range(2, int(k ** 0.5) + 1)):
            return k
        k += 1


def solve(ops, tracker):
    m = 1009
    table = [None] * m
    size = 0
    tombs = 0

    def probe(x, i):
        return (x + i * i) % m

    def slot(x):
        for i in range(m):
            j = probe(x, i)
            tracker.count("probe")
            if table[j] is None:
                return -1
            if table[j] == x:
                return j
        return -1

    def rehash():
        nonlocal m, table, tombs
        tracker.count("rehash")
        old = [y for y in table if y is not None and y != DELETED]
        m = next_prime(max(1009, 4 * (len(old) + 1)))
        table = [None] * m
        tombs = 0
        for y in old:
            i = 0
            while table[probe(y, i)] is not None:
                i += 1
            table[probe(y, i)] = y

    def find(x):
        return slot(x) >= 0

    def insert(x):
        nonlocal size, tombs
        if slot(x) >= 0:
            return
        if 2 * (size + tombs + 1) > m:
            rehash()
        i = 0
        while True:
            j = probe(x, i)
            tracker.count("probe")
            if table[j] is None or table[j] == DELETED:
                if table[j] == DELETED:
                    tombs -= 1
                table[j] = x
                size += 1
                return
            i += 1

    def delete(x):
        nonlocal size, tombs
        j = slot(x)
        if j >= 0:
            table[j] = DELETED
            size -= 1
            tombs += 1
''' + RUN_OPS + '''
    items = sorted(y for y in table if y is not None and y != DELETED)
    return {"found": found, "items": items}
''',
        },
    ],
    "experiments": [
        {
            "id": "exp_set_trees", "name": "Zoznam a stromy pri náhodných a vzostupných kľúčoch",
            "algorithms": ["alg_set_list", "alg_set_bst", "alg_set_avl", "alg_set_23"],
            "generator": "gen_set_ops", "sizes": [250, 500, 1000, 2000, 4000], "repeats": 3,
            "variants": [
                {"label": "náhodné kľúče", "params": {"mode": "random"}},
                {"label": "vzostupné kľúče", "params": {"mode": "sorted"}},
            ],
        },
        {
            "id": "exp_set_hash", "name": "Hašovacie tabuľky pri kolíziách",
            "algorithms": ["alg_set_avl", "alg_set_chain", "alg_set_linear", "alg_set_quadratic"],
            "generator": "gen_set_ops", "sizes": [250, 500, 1000, 2000, 4000], "repeats": 3,
            "variants": [
                {"label": "náhodné kľúče", "params": {"mode": "random"}},
                {"label": "násobky 1009", "params": {"mode": "collisions"}},
            ],
        },
    ],
}

PROBLEMS = [SET_OPS]
