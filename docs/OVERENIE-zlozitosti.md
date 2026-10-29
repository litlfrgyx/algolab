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
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | AVL tree | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | Hashing with chaining (m = 1009) | O(n) (avg) | O(n log n) | medium | 1.14 | unknown | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | Open addressing, linear probing | O(n) (avg) | O(n) | low | 1.13 | match | áno |
| Hašovacie tabuľky pri kolíziách | náhodné kľúče | Open addressing, quadratic probing | O(n) (avg) | O(n log n) | medium | 1.12 | unknown | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | AVL tree | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | Hashing with chaining (m = 1009) | O(n^2) (worst) | O(n^2) | high | 1.99 | match | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | Open addressing, linear probing | O(n) (avg) | O(log n) | low | 1.28 | unknown | áno |
| Hašovacie tabuľky pri kolíziách | násobky 1009 | Open addressing, quadratic probing | O(n) (avg) | O(log n) | low | 1.28 | unknown | áno |
| Zoznam susedov oproti matici | riedky graf | DFS (recursive) | O(n) (avg) | O(n) | high | 1.01 | match | áno |
| Zoznam susedov oproti matici | riedky graf | DFS (stack) | O(n) (avg) | O(n) | high | 1.01 | match | áno |
| Zoznam susedov oproti matici | riedky graf | BFS (adjacency list) | O(n) (avg) | O(n) | high | 1.01 | match | áno |
| Zoznam susedov oproti matici | riedky graf | BFS (adjacency matrix) | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam susedov oproti matici | hustý graf | DFS (recursive) | O(n^2) (worst) | O(n^2) | high | 1.96 | match | áno |
| Zoznam susedov oproti matici | hustý graf | DFS (stack) | O(n^2) (worst) | O(n^2) | high | 1.94 | match | áno |
| Zoznam susedov oproti matici | hustý graf | BFS (adjacency list) | O(n^2) (worst) | O(n^2) | high | 1.96 | match | áno |
| Zoznam susedov oproti matici | hustý graf | BFS (adjacency matrix) | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Kostrový les cez DFS a BFS | predvolený vstup | DFS spanning forest | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Kostrový les cez DFS a BFS | predvolený vstup | BFS spanning forest | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| BFS oproti DFS pri vzdialenostiach | predvolený vstup | BFS (layers) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| BFS oproti DFS pri vzdialenostiach | predvolený vstup | DFS depth (incorrect) | O(n) (avg) | O(n) | high | 1.0 | match | nie |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Bubble sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Bubble sort (early exit) | O(n^2) (avg) | O(n^2) | high | 2.01 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Insertion sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Selection sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Bubble sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Bubble sort (early exit) | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Insertion sort | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Selection sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.15 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Bubble sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Bubble sort (early exit) | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Insertion sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Selection sort | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.15 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Quicksort (last element pivot) | O(n log n) (avg) | O(n log n) | high | 1.18 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Quicksort (random pivot) | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Heapsort | O(n log n) (avg) | O(n log n) | high | 1.18 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Quicksort (last element pivot) | O(n^2) (worst) | O(n^2) | high | 2.0 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Quicksort (random pivot) | O(n log n) (avg) | O(n log n) | high | 1.16 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.15 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Heapsort | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.11 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Heapsort | O(n log n) (avg) | O(n log n) | high | 1.12 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Quicksort (random pivot) | O(n log n) (avg) | O(n log n) | high | 1.13 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Radix sort (LSD, counting) | O(n) (avg) | O(n) | low | 1.11 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Radix sort (LSD, ten queues) | O(n) (avg) | O(n) | low | 1.11 | match | áno |
| Radix sorty oproti merge sortu | premenlivá dĺžka | LSD radix sort | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Radix sorty oproti merge sortu | premenlivá dĺžka | MSD radix sort | O(n) (avg) | O(n log n) | low | 1.07 | unknown | áno |
| Radix sorty oproti merge sortu | premenlivá dĺžka | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.14 | match | áno |
| Radix sorty oproti merge sortu | pevná dĺžka 8 | LSD radix sort | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Radix sorty oproti merge sortu | pevná dĺžka 8 | MSD radix sort | O(n) (avg) | O(n log n) | high | 1.1 | mismatch | áno |
| Radix sorty oproti merge sortu | pevná dĺžka 8 | Merge sort | O(n log n) (avg) | O(n log n) | high | 1.14 | match | áno |
| Recursive a iterative inorder | predvolený vstup | Recursive inorder | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Recursive a iterative inorder | predvolený vstup | Iterative inorder (stack) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Recursive a iterative postorder | predvolený vstup | Recursive postorder | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Recursive a iterative postorder | predvolený vstup | Iterative postorder (two stacks) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Front oproti prechodu po úrovniach | vyvážený strom | Level-order (queue) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Front oproti prechodu po úrovniach | vyvážený strom | Level-order without queue | O(n) (best) | O(n) | high | 1.01 | match | áno |
| Front oproti prechodu po úrovniach | zdegenerovaný strom | Level-order (queue) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Front oproti prechodu po úrovniach | zdegenerovaný strom | Level-order without queue | O(n^2) (worst) | O(n^2) | high | 2.0 | match | áno |
| Tri implementácie frontu | predvolený vstup | Array with shifting | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Tri implementácie frontu | predvolený vstup | Circular buffer | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tri implementácie frontu | predvolený vstup | Linked list queue | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vkladanie oproti BuildHeap | náhodné pole | Repeated insertion | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vkladanie oproti BuildHeap | náhodné pole | Bottom-up BuildHeap | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vkladanie oproti BuildHeap | zoradené pole | Repeated insertion | O(n log n) (worst) | O(n log n) | high | 1.13 | match | áno |
| Vkladanie oproti BuildHeap | zoradené pole | Bottom-up BuildHeap | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | náhodný strom | Recursive preorder | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | náhodný strom | Iterative preorder (stack) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | zdegenerovaný strom | Recursive preorder | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | zdegenerovaný strom | Iterative preorder (stack) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Greedy oproti dynamic programming | mince 100, 25, 20, 5, 1 | Greedy | O(n) (avg) | O(n) | high | 0.9 | match | nie |
| Greedy oproti dynamic programming | mince 100, 25, 20, 5, 1 | Dynamic programming | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Greedy oproti dynamic programming | eurové mince | Greedy | O(n) (avg) | O(n) | high | 0.97 | match | áno |
| Greedy oproti dynamic programming | eurové mince | Dynamic programming | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Pole oproti spájanému zoznamu | veľa spájaní | Array list | O(n^2) (avg) | O(n^2) | high | 2.04 | match | áno |
| Pole oproti spájanému zoznamu | veľa spájaní | Linked list with tail pointer | O(n^2) (avg) | O(n^2) | high | 2.09 | match | áno |
| Pole oproti spájanému zoznamu | Cut zo začiatku | Array list | O(n^2) (avg) | O(n^2) | high | 1.98 | match | áno |
| Pole oproti spájanému zoznamu | Cut zo začiatku | Linked list with tail pointer | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Pole oproti spájanému zoznamu | Cut z konca | Array list | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Pole oproti spájanému zoznamu | Cut z konca | Linked list with tail pointer | O(n^2) (avg) | O(n^2) | high | 1.98 | match | áno |
| Zásobník v poli a v zozname | predvolený vstup | Array stack | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Zásobník v poli a v zozname | predvolený vstup | Linked list stack | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Naive recursion (Pascal's rule) | O(2^n) (avg) | O(2^n) | high | 7.55 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Memoized recursion | O(n^2) (avg) | O(n^2) | high | 1.87 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Pascal's triangle | O(n^2) (avg) | O(n^2) | high | 1.73 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Multiplicative formula | O(n) (avg) | O(n) | high | 0.84 | match | áno |
| Tabuľka oproti vzorcu pre veľké n | predvolený vstup | Pascal's triangle | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Tabuľka oproti vzorcu pre veľké n | predvolený vstup | Multiplicative formula | O(n) (avg) | O(n) | high | 0.99 | match | áno |
| Exponenciálna rekurzia oproti tabuľke | predvolený vstup | Naive recursion | O(3^n) (avg) | O(3^n) | high | 7.91 | match | áno |
| Exponenciálna rekurzia oproti tabuľke | predvolený vstup | Memoized recursion | O(n^3) (avg) | O(n^3) | high | 2.77 | match | áno |
| Exponenciálna rekurzia oproti tabuľke | predvolený vstup | Bottom-up dynamic programming | O(n^3) (avg) | O(n^3) | high | 2.64 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Memoized recursion | O(n^3) (avg) | O(n^3) | high | 2.96 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Bottom-up dynamic programming | O(n^3) (avg) | O(n^3) | high | 2.93 | match | áno |
| Tri spôsoby výpočtu 2^n | predvolený vstup | Repeated multiplication | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tri spôsoby výpočtu 2^n | predvolený vstup | Fast exponentiation | O(log n) (avg) | O(log n) | high | 0.08 | match | áno |
| Tri spôsoby výpočtu 2^n | predvolený vstup | Bit shift | O(1) (avg) | O(1) | low | 0.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Naive recursion | O(phi^n) (avg) | O(phi^n) | high | 5.87 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Memoized recursion | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Bottom-up table | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Two variables | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Fast doubling | O(log n) (avg) | O(log n) | low | 0.3 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Memoized recursion | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Bottom-up table | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Two variables | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Fast doubling | O(log n) (avg) | O(log n) | high | 0.13 | match | áno |
| Cyklus oproti vzorcu | predvolený vstup | Loop | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Cyklus oproti vzorcu | predvolený vstup | Gauss formula | O(1) (avg) | O(1) | low | 0.0 | match | áno |
| Faktoriál cyklom a rekurziou | predvolený vstup | Iterative | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Faktoriál cyklom a rekurziou | predvolený vstup | Recursive | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Počet porovnaní pri hľadaní minima a maxima | náhodné pole | Naive linear scan | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Počet porovnaní pri hľadaní minima a maxima | náhodné pole | MAXMIN (divide and conquer) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Počet porovnaní pri hľadaní minima a maxima | náhodné pole | Pairwise scan | O(n) (avg) | O(n) | high | 1.0 | match | áno |

Spolu 158 sérií: zhoda 145, nezhoda 5, neurčené 8.

## Vysvetlenie nezhôd

- Kruskal, Prim s haldou, Dijkstra s haldou: operácia s haldou a zabudované zoradenie hrán sa
  počítajú ako jedna operácia, preto počet operácií rastie ako n + m a odhad ukáže O(n),
  v hustom grafe O(n²). Logaritmický faktor meranie operácií nevidí.
- MSD radix sort pri pevnej dĺžke slov: na rozlíšenie n slov treba asi log n znakov,
  meranie ukáže n log n. Deklarované O(n) platí pre ohraničenú dĺžku porovnávanej časti.

Tabuľku vytvára `backend/experiments_report.py` nad dočasnou databázou.
