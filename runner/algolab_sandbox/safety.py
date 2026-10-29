"""Statická kontrola používateľského kódu (prvá, najslabšia vrstva ochrany).

Odmietne importy modulov s prístupom k súborom, sieti a procesom a prístup
k interným atribútom interpretera. Kontrolu sa dá obísť, preto nie je jedinou
ochranou: kód beží v samostatnom procese bez premenných prostredia, s časovým
a pamäťovým limitom, a pri nasadení na samostatnom serveri bez prístupu
k databáze.
"""

from __future__ import annotations

import ast

BANNED_MODULES = frozenset(
    {
        "os", "sys", "subprocess", "socket", "shutil", "pathlib", "ctypes",
        "threading", "multiprocessing", "importlib", "pickle", "marshal",
        "builtins", "io", "requests", "urllib", "http", "asyncio", "signal",
        "resource", "gc", "inspect", "code", "codeop", "pty", "tempfile",
        "glob", "fcntl", "mmap", "select", "selectors", "ssl", "ftplib",
        "smtplib", "telnetlib", "webbrowser", "platform", "sysconfig", "site",
        "zipimport", "runpy", "traceback", "linecache", "tracemalloc",
    }
)
BANNED_CALLS = frozenset(
    {"__import__", "eval", "exec", "compile", "open", "input", "breakpoint",
     "globals", "locals", "vars", "getattr", "setattr", "delattr", "memoryview"}
)
ALLOWED_DUNDERS = frozenset(
    {"__init__", "__repr__", "__str__", "__eq__", "__lt__", "__le__", "__gt__",
     "__ge__", "__ne__", "__hash__", "__len__", "__iter__", "__next__",
     "__getitem__", "__setitem__", "__contains__", "__bool__", "__name__",
     "__slots__", "__add__", "__sub__", "__mul__"}
)


class UnsafeCode(ValueError):
    """Kód porušil pravidlá statickej kontroly."""


def check_code(code: str) -> None:
    """Vyhodí SyntaxError alebo UnsafeCode s číslom riadku."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        line = getattr(node, "lineno", None)
        where = f" (riadok {line})" if line else ""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BANNED_MODULES:
                    raise UnsafeCode(f"Import modulu {alias.name} nie je povolený{where}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BANNED_MODULES:
                raise UnsafeCode(f"Import modulu {node.module} nie je povolený{where}")
        elif isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None)
            if name in BANNED_CALLS:
                raise UnsafeCode(f"Volanie {name}() nie je povolené{where}")
        elif isinstance(node, ast.Attribute):
            attr = node.attr
            if attr.startswith("__") and attr.endswith("__") and attr not in ALLOWED_DUNDERS:
                raise UnsafeCode(f"Prístup k atribútu {attr} nie je povolený{where}")
        elif isinstance(node, ast.Name):
            if node.id in ("__builtins__", "__loader__", "__spec__"):
                raise UnsafeCode(f"Prístup k {node.id} nie je povolený{where}")
