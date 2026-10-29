"""Spustí všetky vstavané experimenty a vypíše odhad zložitosti oproti deklarovanej.

Spustenie:  python experiments_report.py [id_experimentu ...] > report.md
Výstup je tabuľka v Markdowne, ktorá sa dá použiť pri overení systému.
Beží nad dočasnou SQLite databázou, nemení vývojovú databázu.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'report.db'}"
os.environ.pop("EDIT_PASSWORD", None)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def main(only: list[str]) -> None:
    rows = []
    with TestClient(app) as c:
        exps = [e for e in c.get("/api/experiments").json() if e["is_builtin"]]
        algs = {a["id"]: a for a in c.get("/api/algorithms").json()}
        print(f"# Overenie odhadu zložitosti na vstavaných experimentoch\n")
        print("| Experiment | Variant | Algoritmus | Deklarovaná (prípad) | Odhad z operácií | Istota | Exponent | Zhoda | Správnosť |")
        print("|---|---|---|---|---|---|---|---|---|")
        for e in exps:
            if only and e["id"] not in only:
                continue
            t0 = time.perf_counter()
            c.post(f"/api/experiments/{e['id']}/run")
            elapsed = time.perf_counter() - t0
            res = c.get(f"/api/experiments/{e['id']}/results").json()
            for s in res["series"]:
                cx = s["complexity"]
                op = cx["operations"]
                a = algs[s["algorithm_id"]]
                declared = f"{cx['declared'] or a.get('complexity_time_avg') or '-'} ({cx['declared_case']})"
                correct = {True: "áno", False: "nie", None: "-"}[s["is_correct"]]
                rows.append((e["id"], cx["agreement"]))
                print(f"| {e['name']} | {s['variant_label']} | {s['algorithm_name']} | {declared} | "
                      f"{op['best'] or op['reason']} | {op['confidence']} | {op['exponent']} | "
                      f"{cx['agreement']} | {correct} |")
            print(f"<!-- {e['id']}: {elapsed:.1f} s -->", file=sys.stderr)
    agree = sum(1 for _, a in rows if a == "match")
    mism = sum(1 for _, a in rows if a == "mismatch")
    unk = len(rows) - agree - mism
    print(f"\nSpolu {len(rows)} sérií: zhoda {agree}, nezhoda {mism}, neurčené {unk}.")


if __name__ == "__main__":
    main(sys.argv[1:])
