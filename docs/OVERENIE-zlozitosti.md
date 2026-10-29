# Overenie odhadu zložitosti na vstavaných experimentoch

| Experiment | Variant | Algoritmus | Deklarovaná (prípad) | Odhad z operácií | Istota | Exponent | Zhoda | Správnosť |
|---|---|---|---|---|---|---|---|---|
| Rekurzia oproti tabuľke | predvolený vstup | Rekurzia bez pamäte | other (avg) | O(3^n) | low | 6.1 | unknown | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Rekurzia s memoizáciou | O(n^2) (avg) | O(n^2) | medium | 1.94 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Tabuľka po riadkoch | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Rekurzia s memoizáciou | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Tabuľka po riadkoch | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Kruskal a Prim na riedkych a hustých grafoch | riedky graf | Kruskal | O(n log n) (avg) | O(n) | high | 1.08 | mismatch | áno |
| Kruskal a Prim na riedkych a hustých grafoch | riedky graf | Prim s haldou | O(n log n) (avg) | O(n) | high | 1.0 | mismatch | áno |
| Kruskal a Prim na riedkych a hustých grafoch | riedky graf | Prim s maticou | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Kruskal a Prim na riedkych a hustých grafoch | hustý graf | Kruskal | O(n log n) (avg) | O(n) | low | 1.27 | unknown | áno |
| Kruskal a Prim na riedkych a hustých grafoch | hustý graf | Prim s haldou | O(n log n) (avg) | O(n^2) | high | 1.91 | mismatch | áno |
| Kruskal a Prim na riedkych a hustých grafoch | hustý graf | Prim s maticou | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Naivné vyhľadávanie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Knuth-Morris-Pratt | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Boyer-Moore-Horspool | O(n) (avg) | O(n) | medium | 0.97 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Rabin-Karp | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Naivné vyhľadávanie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Knuth-Morris-Pratt | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Boyer-Moore-Horspool | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Rabin-Karp | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Naivné vyhľadávanie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Knuth-Morris-Pratt | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Boyer-Moore-Horspool | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Rabin-Karp | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Binárne a interpolačné vyhľadávanie | rovnomerné hodnoty | Lineárne vyhľadávanie | O(n) (avg) | O(n) | high | 0.98 | match | áno |
| Binárne a interpolačné vyhľadávanie | rovnomerné hodnoty | Binárne vyhľadávanie | O(log n) (avg) | O(log n) | medium | 0.12 | match | áno |
| Binárne a interpolačné vyhľadávanie | rovnomerné hodnoty | Interpolačné vyhľadávanie | O(1) (best) | O(1) | low | -0.02 | match | áno |
| Binárne a interpolačné vyhľadávanie | jedna obrovská hodnota | Lineárne vyhľadávanie | O(n) (avg) | O(n) | high | 0.99 | match | áno |
| Binárne a interpolačné vyhľadávanie | jedna obrovská hodnota | Binárne vyhľadávanie | O(log n) (avg) | O(log n) | medium | 0.12 | match | áno |
| Binárne a interpolačné vyhľadávanie | jedna obrovská hodnota | Interpolačné vyhľadávanie | O(n) (worst) | O(n) | medium | 0.97 | match | áno |
| Dijkstra s poľom a haldou, Bellman-Ford | riedky graf | Dijkstra s poľom | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Dijkstra s poľom a haldou, Bellman-Ford | riedky graf | Dijkstra s binárnou haldou | O(n log n) (avg) | O(n) | high | 1.0 | mismatch | áno |
| Dijkstra s poľom a haldou, Bellman-Ford | riedky graf | Bellman-Ford | O(n) (best) | O(n) | low | 1.15 | match | áno |
| Dijkstra s poľom a haldou, Bellman-Ford | hustý graf | Dijkstra s poľom | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Dijkstra s poľom a haldou, Bellman-Ford | hustý graf | Dijkstra s binárnou haldou | O(n log n) (avg) | O(n) | medium | 1.1 | unknown | áno |
| Dijkstra s poľom a haldou, Bellman-Ford | hustý graf | Bellman-Ford | O(n^2) (avg) | O(n^2) | high | 1.88 | match | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | AVL strom | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | Hašovanie so zreťazením (m = 1009) | O(n) (avg) | O(n log n) | medium | 1.14 | unknown | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | Otvorené adresovanie, lineárne skúšanie | O(n) (avg) | O(n) | low | 1.13 | match | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | Otvorené adresovanie, kvadratické skúšanie | O(n) (avg) | O(n log n) | medium | 1.12 | unknown | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | AVL strom | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | Hašovanie so zreťazením (m = 1009) | O(n^2) (worst) | O(n^2) | high | 1.99 | match | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | Otvorené adresovanie, lineárne skúšanie | O(n) (avg) | O(log n) | low | 1.28 | unknown | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | Otvorené adresovanie, kvadratické skúšanie | O(n) (avg) | O(log n) | low | 1.28 | unknown | áno |
| BFS oproti DFS pri vzdialenostiach | predvolený vstup | BFS (vzdialenosti po vrstvách) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| BFS oproti DFS pri vzdialenostiach | predvolený vstup | DFS (zámerne nesprávne) | O(n) (avg) | O(n) | high | 1.0 | match | nie |
