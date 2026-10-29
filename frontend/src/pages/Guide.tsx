import { Link } from 'react-router-dom'
import { CodeView } from '../components/CodeView'
import { PageHeader, Panel } from '../components/ui'

const SOLVE = `def solve(data, tracker):
    a = data
    for i in range(len(a) - 1):
        tracker.compare(i, i + 1)
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
            tracker.swap(i, i + 1)
    return a`

const GENERATE = `import random

def generate(n, mode="random", seed=42):
    rnd = random.Random(seed)
    data = [rnd.randint(0, 10 * n) for _ in range(n)]
    if mode == "sorted":
        data.sort()
    return data`

const CHECK = `def check(input, output, expected=None):
    if output == sorted(input):
        return True
    return False, "Výstup nie je zoradený"`

const TRACKER: [string, string, string][] = [
  ['Meranie', 'tracker.count("nazov")', 'Započíta operáciu bez záznamu kroku. Hodí sa tam, kde vizualizácia nie je potrebná.'],
  ['Pole', 'tracker.compare(i, j), tracker.swap(i, j), tracker.set(i, hodnota)', 'Porovnanie, výmena a zápis. Pole najprv zmeň v kóde, tracker zmenu len zaznamená.'],
  ['Pole', 'tracker.pivot(i), tracker.mark_sorted([i]), tracker.pointer("mid", i)', 'Pivot, prvky na správnom mieste a pomenované ukazovatele pod poľom.'],
  ['Pole', 'tracker.array(iné_pole, labels=[...])', 'Zobrazí iné pole ako vstup, napríklad haldu alebo tabuľku memoizácie.'],
  ['Tabuľka', 'tracker.grid(riadky, stĺpce), tracker.read_cell(i, j), tracker.set_cell(i, j, hodnota)', 'Dynamické programovanie: odkiaľ sa hodnota počíta a kam sa zapíše.'],
  ['Graf', 'tracker.graph(n, hrany), tracker.visit(v), tracker.edge(u, v, "tree")', 'Návšteva vrchola a preskúmanie hrany. Rola "tree" hranu označí natrvalo.'],
  ['Graf', 'tracker.relax(u, v, nová_vzdialenosť), tracker.frontier(front, "front")', 'Uvoľnenie hrany a obsah frontu alebo zásobníka pod grafom.'],
  ['Strom', 'tracker.tree(koreň, label="..."), tracker.focus(kľúč), tracker.mark_node(kľúč)', 'Snímok stromu z uzlov s atribútmi key, left, right alebo keys, children.'],
  ['Strom', 'tracker.tree_arrays(values, left, right, root)', 'Strom uložený v troch poliach, kde 0 znamená prázdny podstrom.'],
  ['Text', 'tracker.string(text, vzorka), tracker.shift(posun), tracker.match(i, j), tracker.mismatch(i, j), tracker.found(i)', 'Vyhľadávanie vzorky v texte.'],
]

export default function Guide() {
  return (
    <>
      <PageHeader title="Príručka" lead="Ako napísať vlastný algoritmus, generátor vstupov a kontrolu správnosti. Kód beží v Pythone v izolovanom procese s časovým limitom." />
      <div className="space-y-6">
        <Panel title="Algoritmus">
          <div className="grid gap-4 px-4 pb-4 pt-1 lg:grid-cols-2 [&>*]:min-w-0">
            <div className="prose-text space-y-3 text-sm">
              <p>Algoritmus je funkcia <code>solve(data)</code> alebo <code>solve(data, tracker)</code>. Dostane vstup úlohy a vráti výsledok.</p>
              <p>Druhý parameter <code>tracker</code> zaznamenáva kroky. Algoritmus bez neho sa dá merať, ale nie vizualizovať.</p>
              <p>Pri meraní sa kroky nezaznamenávajú, tracker len počíta operácie. Volania trackera preto nespomaľujú experiment viac, ako je nutné.</p>
              <p>Moduly ako <code>os</code>, <code>sys</code> alebo <code>subprocess</code> a funkcie <code>open</code>, <code>eval</code>, <code>exec</code> sú zakázané. Funkcia <code>print</code> funguje, výpis sa zobrazí vo vizualizácii.</p>
            </div>
            <CodeView code={SOLVE} />
          </div>
        </Panel>
        <Panel title="Metódy trackera">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b border-line text-left text-[13px] text-ink-3">
                  <th className="px-4 py-2 font-medium">Zobrazenie</th>
                  <th className="px-3 py-2 font-medium">Volanie</th>
                  <th className="px-4 py-2 font-medium">Význam</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {TRACKER.map(([kind, call, desc], i) => (
                  <tr key={i} className="align-top">
                    <td className="px-4 py-2.5 text-ink-2">{kind}</td>
                    <td className="px-3 py-2.5"><code className="text-[12.5px]">{call}</code></td>
                    <td className="px-4 py-2.5 text-ink-2">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="px-4 py-3 text-[13px] text-ink-3">Každá metóda má voliteľný parameter <code>label</code> s textom, ktorý sa zobrazí pri kroku.</p>
        </Panel>
        <div className="grid gap-6 lg:grid-cols-2 [&>*]:min-w-0">
          <Panel title="Generátor vstupov">
            <div className="space-y-3 px-4 pb-4 pt-1">
              <p className="prose-text text-sm">Funkcia <code>generate(n, **params)</code> vráti vstup veľkosti n. Parameter <code>seed</code> zaručí, že rovnaký seed dá rovnaký vstup, takže experiment sa dá zopakovať.</p>
              <CodeView code={GENERATE} />
            </div>
          </Panel>
          <Panel title="Kontrola správnosti">
            <div className="space-y-3 px-4 pb-4 pt-1">
              <p className="prose-text text-sm">Funkcia <code>check(input, output, expected)</code> vráti <code>True</code> alebo dvojicu <code>(False, správa)</code>. Ak úloha nemá kontrolu, výstup sa porovná s referenčným algoritmom.</p>
              <CodeView code={CHECK} />
            </div>
          </Panel>
        </div>
        <Panel title="Ako sa odhaduje zložitosť">
          <div className="prose-text space-y-3 px-4 pb-4 pt-1 text-sm">
            <p>Experiment zmeria priemerný počet operácií a čas pre každú veľkosť n. Pre každú triedu g(n), napríklad n, n log n alebo n², sa metódou najmenších štvorcov nájde krivka a·g(n) + b a vypočíta sa jej chyba. Vyhrá trieda s najmenšou chybou.</p>
            <p>Druhým ukazovateľom je exponent k, sklon priamky v grafe s logaritmickými osami. Pri n² vyjde približne 2, pri n log n o niečo viac ako 1.</p>
            <p>Odhad je len približný. Na spoľahlivý výsledok treba aspoň štyri veľkosti, ktoré sa líšia aspoň dva a pol násobne. Postup vychádza z merania empirickej zložitosti podľa Goldsmitha, Aikena a Wilkersona (2007).</p>
            <p>Hotové experimenty sú v časti <Link to="/experiments" className="text-accent underline">Experimenty</Link>.</p>
          </div>
        </Panel>
      </div>
    </>
  )
}
