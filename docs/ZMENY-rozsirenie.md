# Rozšírenie AlgoLab: čo sa zmenilo a prečo

Podklad pre kapitoly 3.3 až 3.6 a 4 diplomovej práce. Opisuje stav po rozšírení
z októbra 2026.

## 1. Prehľad

| Oblasť | Predtým | Teraz |
|---|---|---|
| Úlohy | 1 (triedenie) | 27 úloh, 85 algoritmov, 34 pripravených experimentov |
| Kontrola správnosti | porovnanie s referenčným algoritmom | aj vlastná funkcia `check(input, output, expected)` so správou pre študenta |
| Vizualizácia | len pole | pole, tabuľka, graf, strom, text |
| Metadáta algoritmu | názov a kód | prístup, zložitosť v najlepšom, priemernom a najhoršom prípade, pamäť, vlastnosti |
| Filtrovanie | žiadne | katalóg algoritmov podľa témy, prístupu, hornej hranice zložitosti, vlastností a pôvodu |
| Experiment | jedna sada vstupov | varianty vstupu (napríklad náhodné, zoradené a opačne zoradené pole) |
| Vyhodnotenie | graf času | graf operácií aj času v lineárnej a logaritmickej mierke a odhad triedy zložitosti z merania |
| Priebeh experimentu | WebSocket | dávky: `POST start` a opakovane `POST step` |
| Sandbox | proces v backende | samostatný balík `runner/algolab_sandbox`, pri nasadení samostatný server bez hesiel |
| Úpravy | ktokoľvek | vstavané záznamy len na čítanie, duplikovanie, voliteľné heslo na vlastný kód |
| Databáza | SQLite | SQLite lokálne, PostgreSQL (Supabase) pri nasadení v schéme `algolab` |

## 2. Zmeny dátového modelu (kapitola 3.3)

Verzia schémy je uložená v tabuľke `meta`. Ak sa zmení `SCHEMA_VERSION` v `models.py`,
vývojová databáza sa pri štarte vytvorí znova. Vstavaný katalóg má vlastný odtlačok
(SHA-256 obsahu katalógu). Pri jeho zmene sa vstavané záznamy aktualizujú podľa ID
a vlastné záznamy používateľa ostanú nedotknuté.

| Entita | Nové polia |
|---|---|
| Problem | `summary`, `input_type`, `renderer`, `checker_code`, `tags`, `is_builtin`, `sort_order` |
| Algorithm | `description`, `paradigm`, `complexity_time_best`, `complexity_time_avg`, `complexity_time_worst`, `complexity_space`, `complexity_note`, `complexity_param`, `properties`, `is_builtin`, `sort_order` |
| InputGenerator | `description`, `viz_size`, `is_builtin` |
| Experiment | `variants`, `total_cases`, `done_cases`, `is_builtin` |
| ExperimentRun | `variant_index`, `variant_label`, `check_message` |
| Meta | nová tabuľka: `schema_version`, `catalog_version` |

Triedy zložitosti sú číselník: O(1), O(log log n), O(log n), O(√n), O(n), O(n log n),
O(n²), O(n³), O(φⁿ), O(2ⁿ), O(3ⁿ), O(n!) a „iná“. Triedy sa vzťahujú k veľkosti vstupu n,
ktorú určuje generátor. Presnejší zápis, napríklad O(n + m) pri grafe, je v poznámke.

## 3. Priebeh experimentu po dávkach (oprava textu v 3.1.6 a 3.2)

Pôvodný návrh počítal s WebSocketom na priebeh experimentu. Serverless prostredie
(Vercel) nedrží dlhé spojenia a funkcia smie bežať najviac 60 sekúnd. Experiment sa
preto rozdelí na prípady (variant × veľkosť × opakovanie):

1. `POST /api/experiments/{id}/start` zmaže staré behy a nastaví počet prípadov.
2. `POST /api/experiments/{id}/step` spracuje toľko prípadov, koľko sa zmestí do
   rozpočtu 15 sekúnd, a vráti priebeh.
3. Frontend volá `step`, kým experiment neskončí, a medzitým prekresľuje výsledky.

Experiment sa dá prerušiť a neskôr pokračovať. Rovnaký postup funguje lokálne.

V jednom prípade sa vstup vygeneruje raz, potom beží referenčný algoritmus a nakoniec
každý porovnávaný algoritmus na tom istom vstupe. Seed prípadu je seed experimentu plus
index opakovania.

## 4. Sandbox a bezpečnosť (oprava odseku o Dockeri v 3.1.6)

- Statická kontrola AST odmietne zakázané moduly, funkcie a dunder atribúty.
- Každý beh je samostatný proces s prázdnym prostredím, časovým limitom a na Linuxe
  limitmi `setrlimit` (CPU, pamäť).
- Pri nasadení beží sandbox ako samostatný Vercel projekt. Ten nemá prístup k databáze
  ani k heslám, prijíma len požiadavky s tajným tokenom `RUNNER_TOKEN`.
- Lokálne sa dá API spustiť v Docker kontajneri (`backend/docker-compose.yml`).
- Vstavané záznamy sú len na čítanie. Ak je nastavené `EDIT_PASSWORD`, vlastný kód sa dá
  uložiť a spustiť len s heslom.

## 5. Meranie

- Počet operácií zaznamenáva tracker. Pri meraní sa kroky neukladajú, snímky stromu ani
  obsah frontu sa nekopírujú, aby meranie nespomaľovalo samotné volanie trackera.
- Čas sa meria `time.perf_counter()` okolo volania `solve`.
- Pamäť sa odhaduje z nárastu maximálnej rezidentnej pamäte procesu (`ru_maxrss`).
  Pôvodne použitý `tracemalloc` spomaľoval každú alokáciu: quicksort na zoradenom poli
  dĺžky 1000 trval s ním celý beh asi 2,3 s, bez neho asi 0,2 s. Meranie času by bolo skreslené, preto bol
  odstránený. Toto zistenie stojí za zmienku v práci ako príklad vplyvu nástroja merania
  na meranú veličinu.

## 6. Odhad triedy zložitosti z merania

Implementácia: `backend/app/analysis/complexity.py`.

1. Pre každú veľkosť n sa spriemerujú výsledky opakovaní.
2. Pre každú kandidátnu triedu g(n) sa metódou najmenších štvorcov nájde
   y ≈ a·g(n) + b s podmienkou a ≥ 0.
3. Chyba je RMSE delená priemerom y. Vyhrá trieda s najmenšou chybou.
4. Istota je vysoká, ak druhá najlepšia trieda má aspoň dvojnásobnú chybu, stredná pri
   1,3-násobku, inak nízka.
5. Doplnkovo sa počíta exponent k zo sklonu priamky v log-log súradniciach (y ≈ c·nᵏ).
6. Odhad z operácií má prednosť pred odhadom z času, lebo nezávisí od hardvéru.
7. Odhad sa porovná s deklarovanou triedou pre najlepší, priemerný a najhorší prípad.
   Zhoda s ktorýmkoľvek z nich je „zhoda“.

Podmienky: aspoň 4 rôzne veľkosti, ktoré sa líšia aspoň 2,5-násobne. Exponenciálne
triedy sa skúšajú len pre n do 60.

Zdroj metódy: Goldsmith, Aiken, Wilkerson: Measuring Empirical Computational
Complexity, ESEC/FSE 2007, doi:10.1145/1287624.1287681. Podobný princíp používa
knižnica big_O (P. Berkes).

Výsledok na všetkých vstavaných experimentoch je v `docs/OVERENIE-zlozitosti.md`.
Nezhody sú vysvetliteľné a sú didakticky užitočné:

- Radix sort: generátor dáva hodnoty do 10n, počet cifier rastie ako log n, meranie ukáže
  n log n. Deklarované O(n) platí pre ohraničený počet cifier.
- MSD radix sort reťazcov: na rozlíšenie n slov treba asi log n znakov.
- Dijkstra s haldou, Kruskal, Prim s haldou: operácia s haldou alebo zabudované
  zoradenie sa počíta ako jedna operácia, preto počet operácií ukáže O(n + m).
  Meranie vidí len to, čo algoritmus započíta.
- Hašovanie pri kolíziách: všetky kľúče v jednom zozname, čas rastie kvadraticky.

## 7. Katalóg úloh

Klasické úlohy z údajových štruktúr a algoritmov a z literatúry (Cormen a kol., Sedgewick a Wayne).
Názvy algoritmov sú anglické odborné názvy, popisy sú po slovensky.

| Úloha | Zobrazenie | Kontrola | Algoritmy |
|---|---|---|---|
| Maximum a minimum poľa | pole | check | Naive linear scan, MAXMIN (divide and conquer), Pairwise scan |
| Súčet 1 + 2 + … + n | bez | check | Loop, Gauss formula |
| Faktoriál | bez | check | Iterative, Recursive |
| Mocnina 2ⁿ | bez | check | Repeated multiplication, Fast exponentiation, Bit shift |
| Fibonacciho čísla | pole | referencia | Naive recursion, Memoized recursion, Bottom-up table, Two variables, Fast doubling |
| Kombinačné číslo | tabuľka | referencia | Naive recursion (Pascal's rule), Memoized recursion, Pascal's triangle, Multiplicative formula |
| Násobenie reťazca matíc | tabuľka | referencia | Naive recursion, Memoized recursion, Bottom-up dynamic programming |
| Rozmieňanie mincí | pole | check | Greedy, Dynamic programming |
| Zoznam: operácie Cat a Cut | bez | referencia | Array list, Linked list with tail pointer |
| Zásobník | bez | referencia | Array stack, Linked list stack |
| Front | bez | referencia | Array with shifting, Circular buffer, Linked list queue |
| Vytvorenie maximálnej haldy | pole | check | Repeated insertion, Bottom-up BuildHeap |
| Preorder prehľadávanie | strom | referencia | Recursive preorder, Iterative preorder (stack) |
| Inorder prehľadávanie | strom | referencia | Recursive inorder, Iterative inorder (stack) |
| Postorder prehľadávanie | strom | referencia | Recursive postorder, Iterative postorder (two stacks) |
| Level-order prehľadávanie | strom | referencia | Level-order (queue), Level-order without queue |
| Triedenie poľa čísel | pole | check | Bubble sort, Bubble sort (early exit), Insertion sort, Selection sort, Merge sort, Heapsort, Quicksort (last element pivot), Quicksort (random pivot), Radix sort (LSD, counting), Radix sort (LSD, ten queues) |
| Triedenie reťazcov | bez | check | LSD radix sort, MSD radix sort, Merge sort |
| Prehľadanie grafu | graf | check | DFS (recursive), DFS (stack), BFS (adjacency list), BFS (adjacency matrix) |
| Kostrový les grafu | graf | check | DFS spanning forest, BFS spanning forest |
| Najkratšie cesty v neváženom grafe | graf | check | BFS (layers), DFS depth (incorrect) |
| Operácie nad množinou | strom | check | Unsorted list, Binary search tree, AVL tree, 2-3 tree, Hashing with chaining (m = 1009), Open addressing, linear probing, Open addressing, quadratic probing |
| Vyhľadávanie v zoradenom poli | pole | check | Linear search, Binary search, Interpolation search |
| Najkratšie cesty vo váženom grafe | graf | referencia | Dijkstra (array), Dijkstra (binary heap), Bellman-Ford |
| Minimálna kostra grafu | graf | check | Kruskal, Prim (binary heap), Prim (adjacency matrix) |
| Vyhľadávanie vzorky v texte | text | referencia | Naive string matching, Knuth-Morris-Pratt, Boyer-Moore-Horspool, Rabin-Karp |
| Najdlhšia spoločná podpostupnosť | tabuľka | referencia | Naive recursion, Memoized recursion, Bottom-up table |

Overenie katalógu: `backend/catalog_test.py` spustí každý algoritmus na každom druhu
vstupu s tromi seedmi, skontroluje správnosť (zámerne nesprávne algoritmy musia aspoň raz
zlyhať), nenulový počet operácií a druh krokov vizualizácie. Výsledok: všetky kontroly prešli.


## 8. Rozhranie (kapitola 3.6)

Rozhranie je navrhnuté pre študenta druhého ročníka. Zásady:

- Svetlá a tmavá téma podľa systému, jedna rodina písma (IBM Plex Sans, kód v IBM Plex Mono).
- Farba patrí dátam a stavom. Rovnaké farby rolí vo všetkých zobrazeniach: porovnanie
  (jantárová), výmena alebo zápis (oranžovočervená), pivot (purpurová), práve spracúvaný
  prvok (modrá), hotové (zelená).
- Úvodná stránka predstaví funkcie na skutočných ukážkach (živá vizualizácia, graf z experimentu,
  odhad zložitosti, ukážka kódu). Katalóg úloh je zoradený podľa tém a má trojkrokový návod.
- Katalóg algoritmov je mriežka dlaždíc zoskupená podľa tém s filtrami.
- Rebrík zložitosti: triedy od O(1) po exponenciálne ako schody rastúcej výšky. Rozsah
  najlepší až najhorší prípad je podfarbený, deklarovaná trieda má rámik, odhad z merania
  je plný schod. Zhodu je vidieť bez čítania textu.
- Graf výsledkov má logaritmickú mierku na oboch osiach, kde je nᵏ priamka so sklonom k.
- Kategorická paleta grafov má pevné poradie a overenú rozlíšiteľnosť pre ľudí s poruchou
  farebného videnia. Farba patrí algoritmu, nie poradiu v grafe.
- Príručka v aplikácii opisuje kontrakt `solve`, `generate`, `check` a metódy trackera.

## 9. Nasadenie

| Časť | Kde |
|---|---|
| Frontend (statické súbory) a API (Python funkcia `api/index.py`) | hlavný Vercel projekt |
| Sandbox (`runner/api/index.py`) | samostatný Vercel projekt, bez hesiel |
| Databáza | Supabase PostgreSQL, schéma `algolab`, rola `algolab_app` len s prístupom k nej |

Premenné prostredia hlavného projektu: `DATABASE_URL`, `DB_SCHEMA`, `RUNNER_URL`,
`RUNNER_TOKEN`, `EDIT_PASSWORD`. Runner: `RUNNER_TOKEN`.
