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

Algoritmy z predmetu Údajové štruktúry a algoritmy (KPI FEI TUKE) a päť úloh nad jeho
rámec.

| Úloha | Cvičenie | Zobrazenie | Kontrola | Algoritmy |
|---|---|---|---|---|
| Maximum a minimum poľa | 1, 8 | pole | check | Naivný prechod, MAXMIN (rozdeľuj a panuj), Prechod po dvojiciach |
| Súčet 1 + 2 + … + n | 2 | bez | check | Cyklus, Gaussov vzorec |
| Faktoriál | 1, 2 | bez | check | Cyklus, Rekurzia |
| Mocnina 2ⁿ | 1 | bez | check | Opakované násobenie, Rýchle umocňovanie, Bitový posun |
| Fibonacciho čísla | 3 | pole | referencia | Rekurzia podľa definície, Rekurzia s memoizáciou, Tabuľka zdola nahor, Dve premenné, Rýchle zdvojovanie |
| Kombinačné číslo | 3 | tabuľka | referencia | Rekurzia podľa Pascalovho vzťahu, Rekurzia s memoizáciou, Pascalov trojuholník v tabuľke, Multiplikatívny vzorec |
| Násobenie reťazca matíc | 4 | tabuľka | referencia | Rekurzia cez všetky delenia, Rekurzia s memoizáciou, Tabuľka podľa dĺžky úseku |
| Rozmieňanie mincí | 4 | pole | check | Pažravý algoritmus (zámerne nesprávny pre sadu z cvičenia), Dynamické programovanie |
| Zoznam: operácie Cat a Cut | 3 | bez | referencia | Zoznam v poli, Spájaný zoznam s ukazovateľom na koniec |
| Zásobník | 4 | bez | referencia | Zásobník v poli, Zásobník v spájanom zozname |
| Front | 4 | bez | referencia | Pole s posúvaním prvkov, Kruhové pole, Spájaný zoznam |
| Vytvorenie maximálnej haldy | 5 | pole | check | Postupné vkladanie, BuildHeap zdola |
| Preorder prehľadávanie | 6 | strom | referencia | rekurzívne, so zásobníkom |
| Inorder prehľadávanie | 6 | strom | referencia | rekurzívne, so zásobníkom |
| Postorder prehľadávanie | 6 | strom | referencia | rekurzívne, s dvoma zásobníkmi |
| Level-order prehľadávanie | 6 | strom | referencia | s frontom, bez frontu (levelorderNQ) |
| Triedenie poľa čísel | 7, 8, 9 | pole | check | Bublinkové, bublinkové s ukončením, vkladaním, výberom, merge sort, heapsort, quicksort s posledným a s náhodným pivotom, radix sort s počítaním cifier a s desiatimi frontmi |
| Triedenie reťazcov | 9 | bez | check | LSD radix sort, MSD radix sort, merge sort |
| Prehľadanie grafu | 10 | graf | check | DFS rekurzívne, DFS so zásobníkom, BFS so zoznamom susedov, BFS s maticou susednosti |
| Kostrový les grafu | 11 | graf | check | pomocou DFS, pomocou BFS |
| Najkratšie cesty v neváženom grafe | 11 | graf | check | BFS, DFS (zámerne nesprávne) |
| Operácie nad množinou | 5, 12 | strom | check | Neusporiadaný zoznam, BVS, AVL strom, 2-3 strom, hašovanie so zreťazením, otvorené adresovanie s lineárnym a kvadratickým skúšaním |
| Vyhľadávanie v zoradenom poli | mimo | pole | check | Lineárne, binárne, interpolačné |
| Najkratšie cesty vo váženom grafe | mimo | graf | referencia | Dijkstra s poľom, Dijkstra s haldou, Bellman-Ford |
| Minimálna kostra grafu | mimo | graf | check | Kruskal, Prim s haldou, Prim s maticou |
| Vyhľadávanie vzorky v texte | mimo | text | referencia | Naivné, KMP, Boyer-Moore-Horspool, Rabin-Karp |
| Najdlhšia spoločná podpostupnosť | mimo | tabuľka | referencia | Rekurzia bez pamäte, s memoizáciou, tabuľka |

Overenie katalógu: `backend/catalog_test.py` spustí každý algoritmus na každom druhu
vstupu s tromi seedmi, skontroluje správnosť (zámerne nesprávne algoritmy musia aspoň raz
zlyhať), nenulový počet operácií a druh krokov vizualizácie. Výsledok: 3 517 kontrol,
0 zlyhaní.

## 8. Rozhranie (kapitola 3.6)

Rozhranie je navrhnuté pre študenta druhého ročníka. Zásady:

- Svetlá a tmavá téma podľa systému, jedna rodina písma (IBM Plex Sans, kód v IBM Plex Mono).
- Farba patrí dátam a stavom. Rovnaké farby rolí vo všetkých zobrazeniach: porovnanie
  (jantárová), výmena alebo zápis (oranžovočervená), pivot (purpurová), práve spracúvaný
  prvok (modrá), hotové (zelená).
- Domovská stránka je katalóg úloh zoradený podľa tém predmetu a trojkrokový návod:
  vyber úlohu, spusti vizualizáciu, porovnaj v experimente.
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
