"""Abstraktné údajové typy z cvičení 3, 4 a 5 ÚSaA: zoznam, zásobník, front a halda."""

from __future__ import annotations

from .common import ARRAY_MODES, GEN_ARRAY, enum

GEN_LIST_OPS = '''
import random

def generate(n, mix="cat_heavy", seed=42):
    """Postupnosť n operácií nad zoznamami L1 a L2.

    ["push", 1, x]  pridá x na koniec L1      ["push", 2, x]  pridá x na koniec L2
    ["cat"]         Cat(L1, L2): pripojí L2 za L1, L2 zostane prázdny
    ["cut", p]      Cut(L1, p): odstráni prvok L1 na pozícii p a vráti ho
    """
    rnd = random.Random(seed)
    ops = []
    size1 = size2 = 0
    for _ in range(n):
        r = rnd.random()
        if mix == "cat_heavy":
            if r < 0.15 and size2 > 0:
                ops.append(["cat"]); size1 += size2; size2 = 0
            elif r < 0.25 and size1 > 0:
                ops.append(["cut", rnd.randrange(size1)]); size1 -= 1
            elif r < 0.6:
                ops.append(["push", 1, rnd.randint(1, 99)]); size1 += 1
            else:
                ops.append(["push", 2, rnd.randint(1, 99)]); size2 += 1
        else:
            if r < 0.4 and size1 > 0:
                p = 0 if mix == "cut_front" else size1 - 1
                ops.append(["cut", p]); size1 -= 1
            else:
                ops.append(["push", 1, rnd.randint(1, 99)]); size1 += 1
    return ops
'''

LIST_OPS = {
    "id": "prob_list_ops",
    "name": "Zoznam: operácie Cat a Cut",
    "summary": "Spájaj zoznamy a odstraňuj prvky. Pole alebo spájaný zoznam?",
    "description": (
        "Úloha z cvičenia 3. Cat(L1, L2) pripojí L2 za L1, Cut(L, p) odstráni prvok na pozícii p. "
        "V poli treba pri Cat kopírovať prvky a pri Cut posúvať zvyšok poľa. Spájaný zoznam "
        "s ukazovateľom na koniec zvládne Cat v konštantnom čase, pri Cut však musí prejsť "
        "k pozícii p. Výhodnejšia implementácia závisí od toho, ktoré operácie prevládajú."
    ),
    "category": "data_structures",
    "input_type": "operations",
    "renderer": "none",
    "input_description": "Postupnosť operácií push, cat a cut (pozri popis generátora).",
    "output_description": "Objekt s hodnotami odstránenými operáciou Cut a s výsledným obsahom L1.",
    "tags": ["usaa", "cv3"],
    "reference": "alg_list_array",
    "generators": [{
        "id": "gen_list_ops", "name": "Postupnosť operácií", "code": GEN_LIST_OPS,
        "description": "Náhodná postupnosť operácií s rôznym zastúpením Cat a Cut.",
        "sizes": [1000, 2000, 4000, 8000, 16000], "viz_size": 10,
        "params": [enum("mix", "Prevládajúce operácie", {
            "cat_heavy": "veľa spájaní (Cat)", "cut_front": "Cut zo začiatku", "cut_back": "Cut z konca"}, "cat_heavy")],
    }],
    "algorithms": [
        {
            "id": "alg_list_array", "name": "Zoznam v poli", "viz": False,
            "description": "Prvky sú v súvislom poli. Cat kopíruje prvky L2, Cut posúva prvky za pozíciou p.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(n)",
            "note": "Cat O(|L2|), Cut O(n − p) na operáciu", "param": "počet operácií",
            "code": '''
def solve(ops, tracker):
    l1, l2 = [], []
    removed = []
    for op in ops:
        if op[0] == "push":
            (l1 if op[1] == 1 else l2).append(op[2])
            tracker.count("write")
        elif op[0] == "cat":
            for x in l2:              # kopírovanie prvkov L2 na koniec L1
                l1.append(x)
                tracker.count("write")
            l2 = []
        else:
            p = op[1]
            removed.append(l1[p])
            for i in range(p, len(l1) - 1):   # posun zvyšku poľa doľava
                l1[i] = l1[i + 1]
                tracker.count("write")
            l1.pop()
    return {"removed": removed, "list": l1}
''',
        },
        {
            "id": "alg_list_linked", "name": "Spájaný zoznam s ukazovateľom na koniec", "viz": False,
            "description": "Každý prvok je uzol s odkazom na nasledujúci. Cat len prepojí koniec L1 so začiatkom L2.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(n)",
            "note": "Cat O(1), Cut O(p) na operáciu", "param": "počet operácií",
            "code": '''
class Node:
    __slots__ = ("value", "next")

    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = self.tail = None
        self.size = 0

    def push(self, value, tracker):
        node = Node(value)
        tracker.count("write")
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1


def solve(ops, tracker):
    l1, l2 = LinkedList(), LinkedList()
    removed = []
    for op in ops:
        if op[0] == "push":
            (l1 if op[1] == 1 else l2).push(op[2], tracker)
        elif op[0] == "cat":
            tracker.count("write")
            if l2.head is not None:
                if l1.tail is None:
                    l1.head = l2.head
                else:
                    l1.tail.next = l2.head
                l1.tail = l2.tail
                l1.size += l2.size
            l2 = LinkedList()
        else:
            p = op[1]
            prev, cur = None, l1.head
            for _ in range(p):          # prechod k pozícii p
                prev, cur = cur, cur.next
                tracker.count("step")
            removed.append(cur.value)
            if prev is None:
                l1.head = cur.next
            else:
                prev.next = cur.next
            if cur is l1.tail:
                l1.tail = prev
            l1.size -= 1
            tracker.count("write")
    out, node = [], l1.head
    while node is not None:
        out.append(node.value)
        node = node.next
    return {"removed": removed, "list": out}
''',
        },
    ],
    "experiments": [{
        "id": "exp_list_ops", "name": "Pole oproti spájanému zoznamu",
        "algorithms": ["alg_list_array", "alg_list_linked"], "generator": "gen_list_ops",
        "sizes": [1000, 2000, 4000, 8000], "repeats": 3,
        "variants": [
            {"label": "veľa spájaní", "params": {"mix": "cat_heavy"}},
            {"label": "Cut zo začiatku", "params": {"mix": "cut_front"}},
            {"label": "Cut z konca", "params": {"mix": "cut_back"}},
        ],
    }],
}

GEN_STACK_OPS = '''
import random

def generate(n, seed=42):
    """Postupnosť n operácií: ["push", x], ["pop"], ["top"]."""
    rnd = random.Random(seed)
    ops, size = [], 0
    for _ in range(n):
        r = rnd.random()
        if r < 0.5 or size == 0:
            ops.append(["push", rnd.randint(1, 99)]); size += 1
        elif r < 0.8:
            ops.append(["pop"]); size -= 1
        else:
            ops.append(["top"])
    return ops
'''

STACK = {
    "id": "prob_stack",
    "name": "Zásobník",
    "summary": "Push, Pop a Top v poli a v spájanom zozname.",
    "description": (
        "Úloha z cvičenia 4. Zásobník pridáva aj odoberá prvky na tom istom konci. "
        "Obe implementácie majú každú operáciu v konštantnom čase, celá postupnosť n operácií "
        "je teda lineárna. Experiment ukazuje rozdiel v konštante a v pamäti."
    ),
    "category": "data_structures",
    "input_type": "operations",
    "renderer": "none",
    "input_description": "Postupnosť operácií push, pop a top.",
    "output_description": "Hodnoty vrátené operáciami pop a top v poradí, v akom boli zavolané.",
    "tags": ["usaa", "cv4"],
    "reference": "alg_stack_array",
    "generators": [{
        "id": "gen_stack_ops", "name": "Postupnosť operácií", "code": GEN_STACK_OPS,
        "description": "Náhodná postupnosť operácií, pop sa nevolá na prázdny zásobník.",
        "sizes": [10000, 20000, 50000, 100000, 200000], "viz_size": 10, "params": [],
    }],
    "algorithms": [
        {
            "id": "alg_stack_array", "name": "Zásobník v poli", "viz": False,
            "description": "Vrchol zásobníka je koniec poľa.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "každá operácia O(1)", "param": "počet operácií",
            "code": '''
def solve(ops, tracker):
    stack, out = [], []
    for op in ops:
        tracker.count("operation")
        if op[0] == "push":
            stack.append(op[1])
        elif op[0] == "pop":
            out.append(stack.pop())
        else:
            out.append(stack[-1])
    return out
''',
        },
        {
            "id": "alg_stack_linked", "name": "Zásobník v spájanom zozname", "viz": False,
            "description": "Vrchol zásobníka je prvý uzol zoznamu.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "každá operácia O(1)", "param": "počet operácií",
            "code": '''
class Node:
    __slots__ = ("value", "next")

    def __init__(self, value, next):
        self.value = value
        self.next = next


def solve(ops, tracker):
    top, out = None, []
    for op in ops:
        tracker.count("operation")
        if op[0] == "push":
            top = Node(op[1], top)
        elif op[0] == "pop":
            out.append(top.value)
            top = top.next
        else:
            out.append(top.value)
    return out
''',
        },
    ],
    "experiments": [{
        "id": "exp_stack", "name": "Zásobník v poli a v zozname",
        "algorithms": ["alg_stack_array", "alg_stack_linked"], "generator": "gen_stack_ops",
        "sizes": [10000, 20000, 50000, 100000], "repeats": 3,
    }],
}

GEN_QUEUE_OPS = '''
import random

def generate(n, seed=42):
    """Postupnosť n operácií: ["enqueue", x], ["dequeue"], ["front"]."""
    rnd = random.Random(seed)
    ops, size = [], 0
    for _ in range(n):
        r = rnd.random()
        if r < 0.55 or size == 0:
            ops.append(["enqueue", rnd.randint(1, 99)]); size += 1
        elif r < 0.85:
            ops.append(["dequeue"]); size -= 1
        else:
            ops.append(["front"])
    return ops
'''

QUEUE = {
    "id": "prob_queue",
    "name": "Front",
    "summary": "Enqueue a Dequeue: posúvanie poľa, kruhové pole alebo spájaný zoznam.",
    "description": (
        "Úloha z cvičenia 4. Front pridáva prvky na koniec a odoberá zo začiatku. Ak pole po "
        "každom odobratí posunie všetky prvky, stojí Dequeue lineárny čas a celá postupnosť je "
        "kvadratická. Kruhové pole a spájaný zoznam zvládnu každú operáciu v konštantnom čase."
    ),
    "category": "data_structures",
    "input_type": "operations",
    "renderer": "none",
    "input_description": "Postupnosť operácií enqueue, dequeue a front.",
    "output_description": "Hodnoty vrátené operáciami dequeue a front.",
    "tags": ["usaa", "cv4"],
    "reference": "alg_queue_linked",
    "generators": [{
        "id": "gen_queue_ops", "name": "Postupnosť operácií", "code": GEN_QUEUE_OPS,
        "description": "Náhodná postupnosť operácií, dequeue sa nevolá na prázdny front.",
        "sizes": [1000, 2000, 4000, 8000, 16000], "viz_size": 10, "params": [],
    }],
    "algorithms": [
        {
            "id": "alg_queue_shift", "name": "Pole s posúvaním prvkov", "viz": False,
            "description": "Začiatok frontu je vždy na indexe 0, preto Dequeue posunie všetky prvky.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n^2)", "worst": "O(n^2)", "space": "O(n)",
            "note": "Dequeue O(n)", "param": "počet operácií",
            "code": '''
def solve(ops, tracker):
    queue, out = [], []
    for op in ops:
        if op[0] == "enqueue":
            queue.append(op[1])
            tracker.count("write")
        elif op[0] == "dequeue":
            out.append(queue[0])
            for i in range(len(queue) - 1):    # posun všetkých prvkov dopredu
                queue[i] = queue[i + 1]
                tracker.count("write")
            queue.pop()
        else:
            out.append(queue[0])
    return out
''',
        },
        {
            "id": "alg_queue_circular", "name": "Kruhové pole", "viz": False,
            "description": "Indexy začiatku a konca sa posúvajú dokola. Pri zaplnení sa pole zdvojnásobí.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "každá operácia amortizovane O(1)", "param": "počet operácií",
            "code": '''
def solve(ops, tracker):
    cap = 4
    buf = [None] * cap
    head = size = 0
    out = []
    for op in ops:
        if op[0] == "enqueue":
            if size == cap:                     # zdvojnásobenie kapacity
                new = [None] * (2 * cap)
                for i in range(size):
                    new[i] = buf[(head + i) % cap]
                    tracker.count("write")
                buf, cap, head = new, 2 * cap, 0
            buf[(head + size) % cap] = op[1]
            size += 1
            tracker.count("write")
        elif op[0] == "dequeue":
            out.append(buf[head])
            head = (head + 1) % cap
            size -= 1
            tracker.count("write")
        else:
            out.append(buf[head])
    return out
''',
        },
        {
            "id": "alg_queue_linked", "name": "Spájaný zoznam", "viz": False,
            "description": "Uzly so začiatkom a koncom. Enqueue pridá uzol na koniec, Dequeue odoberie prvý.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(n)",
            "note": "každá operácia O(1)", "param": "počet operácií",
            "code": '''
class Node:
    __slots__ = ("value", "next")

    def __init__(self, value):
        self.value = value
        self.next = None


def solve(ops, tracker):
    head = tail = None
    out = []
    for op in ops:
        if op[0] == "enqueue":
            node = Node(op[1])
            if tail is None:
                head = tail = node
            else:
                tail.next = node
                tail = node
            tracker.count("write")
        elif op[0] == "dequeue":
            out.append(head.value)
            head = head.next
            if head is None:
                tail = None
            tracker.count("write")
        else:
            out.append(head.value)
    return out
''',
        },
    ],
    "experiments": [{
        "id": "exp_queue", "name": "Tri implementácie frontu",
        "algorithms": ["alg_queue_shift", "alg_queue_circular", "alg_queue_linked"], "generator": "gen_queue_ops",
        "sizes": [1000, 2000, 4000, 8000, 16000], "repeats": 3,
    }],
}

BUILD_HEAP = {
    "id": "prob_build_heap",
    "name": "Vytvorenie maximálnej haldy",
    "summary": "Preusporiadaj pole tak, aby každý rodič bol väčší ako jeho potomkovia.",
    "description": (
        "Úloha z cvičenia 5 (BuildHeap). Halda je binárny strom uložený v poli: potomkovia prvku "
        "na indexe i sú na indexoch 2i + 1 a 2i + 2. Postupné vkladanie prvkov stojí O(n log n), "
        "postup zdola (BuildHeap) len O(n). Platných háld z rovnakých čísel je viac, preto sa "
        "výsledok kontroluje podľa vlastnosti haldy, nie porovnaním s jednou odpoveďou."
    ),
    "category": "data_structures",
    "input_type": "array",
    "renderer": "array",
    "input_description": "Pole celých čísel.",
    "output_description": "Pole s rovnakými prvkami, ktoré spĺňa vlastnosť maximálnej haldy.",
    "tags": ["usaa", "cv5"],
    "checker": '''
def check(input, output, expected=None):
    if sorted(output) != sorted(input):
        return False, "Výstup neobsahuje tie isté prvky ako vstup"
    for i in range(len(output)):
        for c in (2 * i + 1, 2 * i + 2):
            if c < len(output) and output[c] > output[i]:
                return False, f"Prvok {output[c]} na indexe {c} je väčší ako jeho rodič {output[i]}"
    return True
''',
    "generators": [{
        "id": "gen_heap_array", "name": "Pole celých čísel", "code": GEN_ARRAY,
        "description": "Na zoradenom poli musí postupné vkladanie presúvať každý prvok až do koreňa.",
        "sizes": [1000, 5000, 20000, 50000, 100000], "viz_size": 12,
        "params": [enum("mode", "Rozloženie hodnôt", {k: ARRAY_MODES[k] for k in ("random", "sorted", "reverse")}, "random")],
    }],
    "algorithms": [
        {
            "id": "alg_heap_insert", "name": "Postupné vkladanie",
            "description": "Prvky sa vkladajú jeden po druhom na koniec haldy a vybublajú nahor, kým sú väčšie ako rodič.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n log n)", "space": "O(n)",
            "note": "na zoradenom vstupe O(n log n)", "param": "počet prvkov",
            "code": '''
def solve(data, tracker):
    heap = []
    tracker.array(heap)
    for x in data:
        heap.append(x)
        i = len(heap) - 1
        tracker.set(i, x, label=f"vlož {x} na koniec haldy")
        while i > 0:
            parent = (i - 1) // 2
            tracker.compare(i, parent)
            if heap[i] <= heap[parent]:
                break
            heap[i], heap[parent] = heap[parent], heap[i]
            tracker.swap(i, parent)
            i = parent
    return heap
''',
        },
        {
            "id": "alg_heap_bottomup", "name": "BuildHeap zdola",
            "description": "Od posledného rodiča po koreň sa každý prvok nechá klesnúť na správne miesto vo svojom podstrome.",
            "paradigm": "data_structure", "best": "O(n)", "avg": "O(n)", "worst": "O(n)", "space": "O(1)",
            "param": "počet prvkov", "properties": ["in_place"],
            "code": '''
def solve(data, tracker):
    n = len(data)

    def sift_down(i):
        while True:
            largest = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < n:
                    tracker.compare(c, largest)
                    if data[c] > data[largest]:
                        largest = c
            if largest == i:
                return
            data[i], data[largest] = data[largest], data[i]
            tracker.swap(i, largest)
            i = largest

    for i in range(n // 2 - 1, -1, -1):
        tracker.pointer("i", i)
        sift_down(i)
    tracker.pointer("i", None)
    return data
''',
        },
    ],
    "experiments": [{
        "id": "exp_build_heap", "name": "Vkladanie oproti BuildHeap",
        "algorithms": ["alg_heap_insert", "alg_heap_bottomup"], "generator": "gen_heap_array",
        "sizes": [1000, 5000, 20000, 50000, 100000], "repeats": 3,
        "variants": [
            {"label": "náhodné pole", "params": {"mode": "random"}},
            {"label": "zoradené pole", "params": {"mode": "sorted"}},
        ],
    }],
}

PROBLEMS = [LIST_OPS, STACK, QUEUE, BUILD_HEAP]
