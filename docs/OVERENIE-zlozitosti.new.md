# Overenie odhadu zložitosti na vstavaných experimentoch

| Experiment | Variant | Algoritmus | Deklarovaná (prípad) | Odhad z operácií | Istota | Exponent | Zhoda | Správnosť |
|---|---|---|---|---|---|---|---|---|
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Naive string matching | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Knuth-Morris-Pratt | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Boyer-Moore-Horspool | O(n) (avg) | O(n) | medium | 0.97 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | náhodný text | Rabin-Karp | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Naive string matching | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Knuth-Morris-Pratt | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Boyer-Moore-Horspool | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka aa…ab | Rabin-Karp | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Naive string matching | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Knuth-Morris-Pratt | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Boyer-Moore-Horspool | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vyhľadávanie vzorky na rôznych textoch | aaa…a, vzorka baa…a | Rabin-Karp | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Naive recursion | other (avg) | O(3^n) | low | 6.1 | unknown | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Memoized recursion | O(n^2) (avg) | O(n^2) | medium | 1.94 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Bottom-up table | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Memoized recursion | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Bottom-up table | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Binárne a interpolačné vyhľadávanie | rovnomerné hodnoty | Linear search | O(n) (avg) | O(n) | high | 0.98 | match | áno |
| Binárne a interpolačné vyhľadávanie | rovnomerné hodnoty | Binary search | O(log n) (avg) | O(log n) | medium | 0.12 | match | áno |
| Binárne a interpolačné vyhľadávanie | rovnomerné hodnoty | Interpolation search | O(1) (best) | O(1) | low | -0.02 | match | áno |
| Binárne a interpolačné vyhľadávanie | jedna obrovská hodnota | Linear search | O(n) (avg) | O(n) | high | 0.99 | match | áno |
| Binárne a interpolačné vyhľadávanie | jedna obrovská hodnota | Binary search | O(log n) (avg) | O(log n) | medium | 0.12 | match | áno |
| Binárne a interpolačné vyhľadávanie | jedna obrovská hodnota | Interpolation search | O(n) (worst) | O(n) | medium | 0.97 | match | áno |
| Dijkstra (array, binary heap) a Bellman-Ford | riedky graf | Dijkstra (array) | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Dijkstra (array, binary heap) a Bellman-Ford | riedky graf | Dijkstra (binary heap) | O(n log n) (avg) | O(n) | high | 1.0 | mismatch | áno |
| Dijkstra (array, binary heap) a Bellman-Ford | riedky graf | Bellman-Ford | O(n) (best) | O(n) | low | 1.15 | match | áno |
| Dijkstra (array, binary heap) a Bellman-Ford | hustý graf | Dijkstra (array) | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Dijkstra (array, binary heap) a Bellman-Ford | hustý graf | Dijkstra (binary heap) | O(n log n) (avg) | O(n) | medium | 1.1 | unknown | áno |
| Dijkstra (array, binary heap) a Bellman-Ford | hustý graf | Bellman-Ford | O(n^2) (avg) | O(n^2) | high | 1.88 | match | áno |
| Kruskal a Prim na riedkych a hustých grafoch | riedky graf | Kruskal | O(n log n) (avg) | O(n) | high | 1.08 | mismatch | áno |
| Kruskal a Prim na riedkych a hustých grafoch | riedky graf | Prim (binary heap) | O(n log n) (avg) | O(n) | high | 1.0 | mismatch | áno |
| Kruskal a Prim na riedkych a hustých grafoch | riedky graf | Prim (adjacency matrix) | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Kruskal a Prim na riedkych a hustých grafoch | hustý graf | Kruskal | O(n log n) (avg) | O(n) | low | 1.27 | unknown | áno |
| Kruskal a Prim na riedkych a hustých grafoch | hustý graf | Prim (binary heap) | O(n log n) (avg) | O(n^2) | high | 1.91 | mismatch | áno |
| Kruskal a Prim na riedkych a hustých grafoch | hustý graf | Prim (adjacency matrix) | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | Unsorted list | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | Binary search tree | O(n log n) (avg) | O(n log n) | high | 1.23 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | AVL tree | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | 2-3 tree | O(n log n) (avg) | O(n log n) | high | 1.19 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | Unsorted list | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | Binary search tree | O(n^2) (worst) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | AVL tree | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | 2-3 tree | O(n log n) (avg) | O(n log n) | high | 1.18 | match | áno |
