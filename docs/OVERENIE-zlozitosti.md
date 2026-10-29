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
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | Neusporiadaný zoznam | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | Binárny vyhľadávací strom | O(n log n) (avg) | O(n log n) | high | 1.23 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | AVL strom | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | náhodné kľúče | 2-3 strom | O(n log n) (avg) | O(n log n) | high | 1.19 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | Neusporiadaný zoznam | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | Binárny vyhľadávací strom | O(n^2) (worst) | O(n^2) | high | 2.0 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | AVL strom | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Zoznam a stromy pri náhodných a vzostupných kľúčoch | vzostupné kľúče | 2-3 strom | O(n log n) (avg) | O(n log n) | high | 1.18 | match | áno |
| Zoznam susedov oproti matici | riedky graf | DFS rekurzívne | O(n) (avg) | O(n) | high | 1.01 | match | áno |
| Zoznam susedov oproti matici | riedky graf | DFS so zásobníkom | O(n) (avg) | O(n) | high | 1.01 | match | áno |
| Zoznam susedov oproti matici | riedky graf | BFS so zoznamom susedov | O(n) (avg) | O(n) | high | 1.01 | match | áno |
| Zoznam susedov oproti matici | riedky graf | BFS s maticou susednosti | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Zoznam susedov oproti matici | hustý graf | DFS rekurzívne | O(n^2) (worst) | O(n^2) | high | 1.96 | match | áno |
| Zoznam susedov oproti matici | hustý graf | DFS so zásobníkom | O(n^2) (worst) | O(n^2) | high | 1.94 | match | áno |
| Zoznam susedov oproti matici | hustý graf | BFS so zoznamom susedov | O(n^2) (worst) | O(n^2) | high | 1.96 | match | áno |
| Zoznam susedov oproti matici | hustý graf | BFS s maticou susednosti | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Kostrový les cez DFS a BFS | predvolený vstup | Kostrový les pomocou DFS | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Kostrový les cez DFS a BFS | predvolený vstup | Kostrový les pomocou BFS | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Triedenie zlučovaním (merge sort) | O(n log n) (avg) | O(n log n) | high | 1.11 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Triedenie haldou (heapsort) | O(n log n) (avg) | O(n log n) | high | 1.12 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Quicksort, náhodný pivot | O(n log n) (avg) | O(n log n) | high | 1.13 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Radix sort (LSD, počítanie cifier) | O(n) (avg) | O(n) | low | 1.11 | match | áno |
| Rýchle triedenia na väčších poliach | predvolený vstup | Radix sort (LSD, desať frontov) | O(n) (avg) | O(n) | low | 1.11 | match | áno |
| Radix sorty oproti merge sortu | premenlivá dĺžka | LSD radix sort | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Radix sorty oproti merge sortu | premenlivá dĺžka | MSD radix sort | O(n) (avg) | O(n log n) | low | 1.07 | unknown | áno |
| Radix sorty oproti merge sortu | premenlivá dĺžka | Merge sort reťazcov | O(n log n) (avg) | O(n log n) | high | 1.14 | match | áno |
| Radix sorty oproti merge sortu | pevná dĺžka 8 | LSD radix sort | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Radix sorty oproti merge sortu | pevná dĺžka 8 | MSD radix sort | O(n) (avg) | O(n log n) | high | 1.1 | mismatch | áno |
| Radix sorty oproti merge sortu | pevná dĺžka 8 | Merge sort reťazcov | O(n log n) (avg) | O(n log n) | high | 1.14 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Bublinkové triedenie | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Bublinkové triedenie s ukončením | O(n^2) (avg) | O(n^2) | high | 2.01 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Triedenie vkladaním | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Triedenie výberom | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | náhodné pole | Triedenie zlučovaním (merge sort) | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Bublinkové triedenie | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Bublinkové triedenie s ukončením | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Triedenie vkladaním | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Triedenie výberom | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | zoradené pole | Triedenie zlučovaním (merge sort) | O(n log n) (avg) | O(n log n) | high | 1.15 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Bublinkové triedenie | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Bublinkové triedenie s ukončením | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Triedenie vkladaním | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Triedenie výberom | O(n^2) (avg) | O(n^2) | high | 2.0 | match | áno |
| Jednoduché triedenia oproti merge sortu | opačne zoradené pole | Triedenie zlučovaním (merge sort) | O(n log n) (avg) | O(n log n) | high | 1.15 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Quicksort, pivot je posledný prvok | O(n log n) (avg) | O(n log n) | high | 1.18 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Quicksort, náhodný pivot | O(n log n) (avg) | O(n log n) | high | 1.2 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Triedenie zlučovaním (merge sort) | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Voľba pivota v quicksorte | náhodné pole | Triedenie haldou (heapsort) | O(n log n) (avg) | O(n log n) | high | 1.18 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Quicksort, pivot je posledný prvok | O(n^2) (worst) | O(n^2) | high | 2.0 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Quicksort, náhodný pivot | O(n log n) (avg) | O(n log n) | high | 1.16 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Triedenie zlučovaním (merge sort) | O(n log n) (avg) | O(n log n) | high | 1.15 | match | áno |
| Voľba pivota v quicksorte | zoradené pole | Triedenie haldou (heapsort) | O(n log n) (avg) | O(n log n) | high | 1.17 | match | áno |
| Postorder rekurzívne a s dvoma zásobníkmi | predvolený vstup | Postorder rekurzívne | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Postorder rekurzívne a s dvoma zásobníkmi | predvolený vstup | Postorder s dvoma zásobníkmi | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Front oproti prechodu po úrovniach | vyvážený strom | Level-order s frontom | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Front oproti prechodu po úrovniach | vyvážený strom | Level-order bez frontu (levelorderNQ) | O(n) (best) | O(n) | high | 1.01 | match | áno |
| Front oproti prechodu po úrovniach | zdegenerovaný strom | Level-order s frontom | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Front oproti prechodu po úrovniach | zdegenerovaný strom | Level-order bez frontu (levelorderNQ) | O(n^2) (worst) | O(n^2) | high | 2.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | náhodný strom | Preorder rekurzívne | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | náhodný strom | Preorder so zásobníkom | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | zdegenerovaný strom | Preorder rekurzívne | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Rekurzia oproti vlastnému zásobníku | zdegenerovaný strom | Preorder so zásobníkom | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Inorder rekurzívne a so zásobníkom | predvolený vstup | Inorder rekurzívne | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Inorder rekurzívne a so zásobníkom | predvolený vstup | Inorder so zásobníkom | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tri implementácie frontu | predvolený vstup | Pole s posúvaním prvkov | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Tri implementácie frontu | predvolený vstup | Kruhové pole | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tri implementácie frontu | predvolený vstup | Spájaný zoznam | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vkladanie oproti BuildHeap | náhodné pole | Postupné vkladanie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vkladanie oproti BuildHeap | náhodné pole | BuildHeap zdola | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Vkladanie oproti BuildHeap | zoradené pole | Postupné vkladanie | O(n log n) (worst) | O(n log n) | high | 1.13 | match | áno |
| Vkladanie oproti BuildHeap | zoradené pole | BuildHeap zdola | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Pole oproti spájanému zoznamu | veľa spájaní | Zoznam v poli | O(n^2) (avg) | O(n^2) | high | 2.04 | match | áno |
| Pole oproti spájanému zoznamu | veľa spájaní | Spájaný zoznam s ukazovateľom na koniec | O(n^2) (avg) | O(n^2) | high | 2.09 | match | áno |
| Pole oproti spájanému zoznamu | Cut zo začiatku | Zoznam v poli | O(n^2) (avg) | O(n^2) | high | 1.98 | match | áno |
| Pole oproti spájanému zoznamu | Cut zo začiatku | Spájaný zoznam s ukazovateľom na koniec | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Pole oproti spájanému zoznamu | Cut z konca | Zoznam v poli | O(n) (best) | O(n) | high | 1.0 | match | áno |
| Pole oproti spájanému zoznamu | Cut z konca | Spájaný zoznam s ukazovateľom na koniec | O(n^2) (avg) | O(n^2) | high | 1.98 | match | áno |
| Zásobník v poli a v zozname | predvolený vstup | Zásobník v poli | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Zásobník v poli a v zozname | predvolený vstup | Zásobník v spájanom zozname | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Rekurzia s memoizáciou | O(n^3) (avg) | O(n^3) | high | 2.96 | match | áno |
| Memoizácia oproti tabuľke | predvolený vstup | Tabuľka podľa dĺžky úseku | O(n^3) (avg) | O(n^3) | high | 2.93 | match | áno |
| Pažravý algoritmus oproti dynamickému programovaniu | sada z cvičenia | Pažravý algoritmus | O(n) (avg) | O(n) | high | 0.9 | match | nie |
| Pažravý algoritmus oproti dynamickému programovaniu | sada z cvičenia | Dynamické programovanie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Pažravý algoritmus oproti dynamickému programovaniu | eurové mince | Pažravý algoritmus | O(n) (avg) | O(n) | high | 0.97 | match | áno |
| Pažravý algoritmus oproti dynamickému programovaniu | eurové mince | Dynamické programovanie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tabuľka oproti vzorcu pre veľké n | predvolený vstup | Pascalov trojuholník v tabuľke | O(n^2) (avg) | O(n^2) | high | 1.99 | match | áno |
| Tabuľka oproti vzorcu pre veľké n | predvolený vstup | Multiplikatívny vzorec | O(n) (avg) | O(n) | high | 0.99 | match | áno |
| Exponenciálna rekurzia oproti tabuľke | predvolený vstup | Rekurzia cez všetky delenia | O(3^n) (avg) | O(3^n) | high | 7.91 | match | áno |
| Exponenciálna rekurzia oproti tabuľke | predvolený vstup | Rekurzia s memoizáciou | O(n^3) (avg) | O(n^3) | high | 2.77 | match | áno |
| Exponenciálna rekurzia oproti tabuľke | predvolený vstup | Tabuľka podľa dĺžky úseku | O(n^3) (avg) | O(n^3) | high | 2.64 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Rekurzia podľa Pascalovho vzťahu | O(2^n) (avg) | O(2^n) | high | 7.55 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Rekurzia s memoizáciou | O(n^2) (avg) | O(n^2) | high | 1.87 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Pascalov trojuholník v tabuľke | O(n^2) (avg) | O(n^2) | high | 1.73 | match | áno |
| Rekurzia oproti tabuľke | predvolený vstup | Multiplikatívny vzorec | O(n) (avg) | O(n) | high | 0.84 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Rekurzia podľa definície | O(phi^n) (avg) | O(phi^n) | high | 5.87 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Rekurzia s memoizáciou | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Tabuľka zdola nahor | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Dve premenné | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Exponenciálna rekurzia oproti lineárnym riešeniam | predvolený vstup | Rýchle zdvojovanie | O(log n) (avg) | O(log n) | low | 0.3 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Rekurzia s memoizáciou | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Tabuľka zdola nahor | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Dve premenné | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Lineárne riešenia a rýchle zdvojovanie pre veľké n | predvolený vstup | Rýchle zdvojovanie | O(log n) (avg) | O(log n) | high | 0.13 | match | áno |
| Faktoriál cyklom a rekurziou | predvolený vstup | Cyklus | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Faktoriál cyklom a rekurziou | predvolený vstup | Rekurzia | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tri spôsoby výpočtu 2^n | predvolený vstup | Opakované násobenie | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Tri spôsoby výpočtu 2^n | predvolený vstup | Rýchle umocňovanie | O(log n) (avg) | O(log n) | high | 0.08 | match | áno |
| Tri spôsoby výpočtu 2^n | predvolený vstup | Bitový posun | O(1) (avg) | O(1) | low | 0.0 | match | áno |
| Cyklus oproti vzorcu | predvolený vstup | Cyklus | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Cyklus oproti vzorcu | predvolený vstup | Gaussov vzorec | O(1) (avg) | O(1) | low | 0.0 | match | áno |
| Počet porovnaní pri hľadaní minima a maxima | náhodné pole | Naivný prechod | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Počet porovnaní pri hľadaní minima a maxima | náhodné pole | MAXMIN (rozdeľuj a panuj) | O(n) (avg) | O(n) | high | 1.0 | match | áno |
| Počet porovnaní pri hľadaní minima a maxima | náhodné pole | Prechod po dvojiciach | O(n) (avg) | O(n) | high | 1.0 | match | áno |

Spolu 158 sérií: zhoda 145, nezhoda 5, neurčené 8.

## Vysvetlenie nezhôd

- Kruskal, Prim s haldou, Dijkstra s haldou: operácia s haldou a zabudované zoradenie hrán sa
  počítajú ako jedna operácia, preto počet operácií rastie ako n + m a odhad ukáže O(n),
  v hustom grafe O(n²). Logaritmický faktor meranie operácií nevidí.
- MSD radix sort pri pevnej dĺžke slov: na rozlíšenie n slov treba asi log n znakov,
  meranie ukáže n log n. Deklarované O(n) platí pre ohraničenú dĺžku porovnávanej časti.

Tabuľku vytvára `backend/experiments_report.py` nad dočasnou databázou.
