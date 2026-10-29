"""Smoke test backendu cez HTTP API (FastAPI TestClient, dočasná SQLite databáza).

Spustenie:  python smoke_test.py
Overí: inicializáciu katalógu, ochranu vstavaných záznamov, duplikovanie, heslo na úpravy,
experiment po dávkach s variantmi, odhad zložitosti, export, vizualizáciu a kontrolu kódu.
Úplné overenie všetkých algoritmov katalógu robí catalog_test.py.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp()) / "smoke.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}")
os.environ["EDIT_PASSWORD"] = "tajne"
os.environ["STEP_BUDGET_S"] = "0.5"

from fastapi.testclient import TestClient  # noqa: E402

from app.analysis.complexity import fit_complexity  # noqa: E402
from app.catalog import CATALOG  # noqa: E402
from app.main import app  # noqa: E402

passed = 0
failed = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  XX  {name}  {extra}")


PW = {"X-Edit-Password": "tajne"}


def main() -> None:
    with TestClient(app) as c:
        print("— katalóg —")
        info = c.get("/api/info").json()
        n_alg = sum(len(p["algorithms"]) for p in CATALOG)
        check("info: počet úloh", info["problems"] == len(CATALOG), str(info))
        check("info: počet algoritmov", info["algorithms"] == n_alg, str(info))
        check("info: úpravy chránené heslom", info["edit_protected"] is True)
        problems = c.get("/api/problems").json()
        check("zoznam úloh", len(problems) == len(CATALOG))
        check("úlohy sú vstavané", all(p["is_builtin"] for p in problems))
        sorting = next(p for p in problems if p["id"] == "prob_sorting")
        check("triedenie má 10 algoritmov", sorting["algorithm_count"] == 10, str(sorting["algorithm_count"]))
        algs = c.get("/api/algorithms").json()
        check("všetky algoritmy", len(algs) == n_alg)
        bubble = next(a for a in algs if a["id"] == "alg_bubble")
        check("metadáta algoritmu", bubble["complexity_time_avg"] == "O(n^2)" and bubble["paradigm"] == "iterative")
        check("bubble podporuje vizualizáciu", bubble["supports_visualization"] is True)

        print("— ochrana a duplikovanie —")
        r = c.put("/api/algorithms/alg_bubble", json={"name": "x"}, headers=PW)
        check("vstavaný algoritmus sa nedá upraviť (403)", r.status_code == 403, str(r.status_code))
        r = c.post("/api/algorithms/alg_bubble/duplicate")
        check("bez hesla sa nedá duplikovať (401)", r.status_code == 401, str(r.status_code))
        r = c.post("/api/algorithms/alg_bubble/duplicate", headers=PW)
        check("duplikát vytvorený", r.status_code == 201, r.text[:200])
        dup = r.json()
        check("duplikát nie je vstavaný", dup["is_builtin"] is False)
        r = c.put(f"/api/algorithms/{dup['id']}", headers=PW,
                  json={"name": "Moja bublina", "complexity_time_avg": "O(n^2)", "properties": ["stable"]})
        check("duplikát sa dá upraviť", r.status_code == 200 and r.json()["name"] == "Moja bublina", r.text[:200])
        r = c.put(f"/api/algorithms/{dup['id']}", headers=PW, json={"code": "import os\ndef solve(d): return d"})
        check("nebezpečný kód sa neuloží (400)", r.status_code == 400, str(r.status_code))
        r = c.post("/api/code/validate", json={"kind": "algorithm", "code": "def solve(data):\n    return sorted(data)\n"})
        body = r.json()
        check("validácia: platný kód bez trackera", body["valid"] is True and body["uses_tracker"] is False)
        check("validácia: upozornenie na chýbajúci tracker", any(e["severity"] == "warning" for e in body["errors"]))
        r = c.post("/api/code/validate", json={"kind": "algorithm", "code": "def solve(data:\n    return 1\n"})
        check("validácia: syntaktická chyba s riadkom", r.json()["valid"] is False and r.json()["errors"][0]["line"] == 1)

        print("— generátor —")
        r = c.post("/api/generators/gen_sort/preview", json={"n": 8, "params": {"mode": "sorted"}, "seed": 1})
        prev = r.json()
        check("náhľad generátora", r.status_code == 200 and prev["input"] == sorted(prev["input"]), r.text[:200])

        print("— experiment po dávkach s variantmi —")
        r = c.post("/api/experiments", json={
            "name": "smoke", "problem_id": "prob_sorting", "generator_id": "gen_sort",
            "algorithm_ids": ["alg_bubble", "alg_merge", "alg_quick_last", dup["id"]],
            "sizes": [50, 100, 200, 400], "repeats": 2, "seed": 7,
            "variants": [{"label": "náhodné", "params": {"mode": "random"}},
                         {"label": "zoradené", "params": {"mode": "sorted"}}],
        })
        check("experiment vytvorený", r.status_code == 201, r.text[:300])
        exp = r.json()
        prog = c.post(f"/api/experiments/{exp['id']}/start").json()
        check("počet prípadov = 2 varianty × 4 veľkosti × 2 opakovania", prog["total_cases"] == 16, str(prog["total_cases"]))
        steps = 0
        while not prog["finished"] and steps < 200:
            prog = c.post(f"/api/experiments/{exp['id']}/step").json()
            steps += 1
        check("experiment dobehol v dávkach", prog["finished"] and prog["experiment"]["status"] == "done",
              f"steps={steps} {prog['experiment']['status']}")
        check("viac ako jedna dávka", steps > 1, str(steps))
        runs = c.get(f"/api/experiments/{exp['id']}/runs").json()
        check("počet behov = 16 × 4", len(runs) == 64, str(len(runs)))
        bad = [x for x in runs if not (x["status"] == "ok" and x["is_correct"])]
        check("všetky behy ok a správne", not bad, str(bad[:2]))
        res = c.get(f"/api/experiments/{exp['id']}/results").json()
        series = res["series"]
        check("séria pre každý algoritmus a variant", len(series) == 8, str(len(series)))

        def est(aid: str, variant: int) -> dict:
            s = next(x for x in series if x["algorithm_id"] == aid and x["variant_index"] == variant)
            return s["complexity"]

        bub = est("alg_bubble", 0)
        check("odhad: bubble O(n^2) podľa operácií", bub["operations"]["best"] == "O(n^2)", str(bub["operations"]))
        check("odhad: bubble súhlasí s deklarovanou", bub["agreement"] == "match", str(bub))
        mer = est("alg_merge", 0)
        check("odhad: merge O(n log n)", mer["operations"]["best"] == "O(n log n)", str(mer["operations"]))
        ql = est("alg_quick_last", 1)
        check("odhad: quicksort na zoradenom vstupe O(n^2)", ql["operations"]["best"] == "O(n^2)", str(ql["operations"]))
        check("quicksort na zoradenom vstupe porovnáva s najhorším prípadom", ql["declared_case"] == "worst", str(ql))
        csv = c.get(f"/api/experiments/{exp['id']}/export?format=csv")
        check("export CSV", csv.status_code == 200 and "variant" in csv.text.splitlines()[0], csv.text[:120])
        js = c.get(f"/api/experiments/{exp['id']}/export?format=json")
        check("export JSON", js.status_code == 200 and "runs" in js.json())

        print("— zámerne nesprávny algoritmus —")
        r = c.post("/api/experiments", json={
            "name": "dfs", "problem_id": "prob_unweighted_sp", "generator_id": "gen_graph_sp",
            "algorithm_ids": ["alg_sp_bfs", "alg_sp_dfs_wrong"], "sizes": [30, 60], "repeats": 1,
        })
        e2 = r.json()
        c.post(f"/api/experiments/{e2['id']}/run")
        runs2 = c.get(f"/api/experiments/{e2['id']}/runs").json()
        check("BFS správne", all(x["is_correct"] for x in runs2 if x["algorithm_id"] == "alg_sp_bfs"))
        wrong = [x for x in runs2 if x["algorithm_id"] == "alg_sp_dfs_wrong"]
        check("DFS ako najkratšie cesty zlyhá kontrolu", any(x["is_correct"] is False for x in wrong))
        check("chybová správa kontroly", any(x["check_message"] for x in wrong))

        print("— vizualizácia —")
        for aid, renderer, inp in (
            ("alg_bubble", "array", [5, 3, 1, 4, 2]),
            ("alg_binom_table", "grid", {"n": 5, "k": 2}),
            ("alg_bfs", "graph", {"n": 4, "edges": [[0, 1], [1, 2], [0, 3]], "start": 0}),
            ("alg_set_avl", "tree", [["insert", 3], ["insert", 1], ["insert", 2], ["find", 2]]),
            ("alg_kmp", "string", {"text": "abababc", "pattern": "abc"}),
        ):
            r = c.post("/api/visualize", json={"algorithm_id": aid, "input": inp})
            tr = r.json()
            ok = r.status_code == 200 and tr["renderer"] == renderer and tr["steps"] and tr["is_correct"] is True
            check(f"vizualizácia {aid} ({renderer})", ok, r.text[:300])
        r = c.post("/api/visualize", json={"code": "def solve(data, tracker):\n    print('ahoj')\n    return sorted(data)\n",
                                           "problem_id": "prob_sorting", "input": [3, 1, 2]}, headers=PW)
        tr = r.json()
        check("vlastný kód: výstup print sa zachytí", "ahoj" in (tr.get("stdout") or ""), r.text[:200])
        check("vlastný kód: kontrola správnosti", tr.get("is_correct") is True)
        r = c.post("/api/visualize", json={"code": "def solve(data):\n    while True:\n        pass\n",
                                           "problem_id": "prob_sorting", "input": [3, 1, 2]}, headers=PW)
        check("nekonečný cyklus skončí časovým limitom", r.status_code in (400, 408, 422), f"{r.status_code} {r.text[:200]}")

        print("— zmazanie —")
        r = c.delete(f"/api/algorithms/{dup['id']}", headers=PW)
        check("vlastný algoritmus sa dá zmazať", r.status_code == 204, str(r.status_code))
        r = c.delete("/api/problems/prob_sorting", headers=PW)
        check("vstavanú úlohu nemožno zmazať", r.status_code == 403, str(r.status_code))

    print("— odhad zložitosti na syntetických dátach —")
    ns = [100, 200, 400, 800, 1600]
    for name, f in (("O(n)", lambda n: 3 * n + 5), ("O(n^2)", lambda n: n * n / 2),
                    ("O(n log n)", lambda n: n * __import__("math").log2(n)), ("O(2^n)", None)):
        if f is None:
            pts = [(n, 2.0 ** n) for n in (8, 12, 16, 20, 24)]
        else:
            pts = [(n, f(n)) for n in ns]
        fit = fit_complexity(pts, "operations")
        check(f"syntetické {name}", fit["best"] == name, str(fit))

    print(f"\nVÝSLEDOK: {passed} prešlo, {failed} zlyhalo")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
