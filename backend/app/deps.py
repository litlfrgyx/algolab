"""Spoločné pomocné funkcie routerov: ochrana úprav a rozbor kódu."""

from __future__ import annotations

import ast
import hmac

from fastapi import Header, HTTPException

from .config import settings


def require_edit(x_edit_password: str | None = Header(default=None)) -> None:
    """Ak je nastavené EDIT_PASSWORD, úpravy vyžadujú hlavičku X-Edit-Password."""
    if not settings.edit_password:
        return
    if not x_edit_password or not hmac.compare_digest(x_edit_password, settings.edit_password):
        raise HTTPException(401, "Na úpravy je potrebné heslo")


def forbid_builtin(obj, what: str) -> None:
    if getattr(obj, "is_builtin", False):
        raise HTTPException(403, f"Vstavaná položka ({what}) sa nedá meniť. Použi tlačidlo Duplikovať a uprav kópiu.")


def ensure_valid_code(code: str | None, entry: str) -> None:
    """Pred uložením: syntax, zakázané konštrukcie a prítomnosť vstupnej funkcie. Inak 400."""
    if code is None:
        return
    from .sandbox.runner import UnsafeCode, check_code

    try:
        check_code(code)
    except SyntaxError as exc:
        raise HTTPException(400, f"Syntaktická chyba na riadku {exc.lineno}: {exc.msg}") from exc
    except UnsafeCode as exc:
        raise HTTPException(400, str(exc)) from exc
    try:
        names = {n.name for n in ast.walk(ast.parse(code)) if isinstance(n, ast.FunctionDef)}
    except SyntaxError as exc:  # pragma: no cover, check_code ju už odhalí
        raise HTTPException(400, str(exc)) from exc
    if entry not in names:
        raise HTTPException(400, f"Kód musí obsahovať funkciu {entry}")


def uses_tracker(code: str) -> bool:
    """Má funkcia solve druhý parameter (tracker)? Bez spustenia kódu."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "solve":
            return len(node.args.args) >= 2
    return False
