import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, FlaskConical, PlayCircle, Plus } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { useEditAuth } from '../lib/auth'
import { CATEGORY } from '../lib/labels'
import { AlgorithmTable } from '../components/AlgorithmTable'
import { CodeView } from '../components/CodeView'
import { Button, Empty, LoadError, PageHeader, Panel, Skeleton, Tag } from '../components/ui'

export function BackLink({ to, children }: { to: string; children: string }) {
  return (
    <Link to={to} className="inline-flex items-center gap-1 text-[13px] text-ink-3 hover:text-ink">
      <ArrowLeft className="size-3.5" aria-hidden />{children}
    </Link>
  )
}

export default function ProblemDetail() {
  const { id = '' } = useParams()
  const { canEdit } = useEditAuth()
  const state = useAsync(async () => {
    const [problem, algorithms, generators, experiments] = await Promise.all([
      api.problem(id), api.problemAlgorithms(id), api.problemGenerators(id), api.experiments(),
    ])
    return { problem, algorithms, generators, experiments: experiments.filter((e) => e.problem_id === id).sort((a, b) => Number(b.is_builtin) - Number(a.is_builtin) || a.created_at.localeCompare(b.created_at)) }
  }, [id])

  if (state.error) return <LoadError error={state.error} onRetry={state.reload} />
  if (!state.data) return <div className="space-y-4"><Skeleton className="h-10 w-80" /><Skeleton className="h-40" /><Skeleton className="h-64" /></div>

  const { problem, algorithms, generators, experiments } = state.data
  const canVisualize = problem.renderer !== 'none' && algorithms.some((a) => a.supports_visualization)
  const algNames = Object.fromEntries(algorithms.map((a) => [a.id, a.name]))

  return (
    <>
      <PageHeader
        back={<BackLink to="/problems">Všetky úlohy</BackLink>}
        title={problem.name}
        lead={problem.summary}
        actions={
          <>
            {canVisualize && (
              <Link to={`/visualizer?problem=${problem.id}`}>
                <Button variant="primary" icon={<PlayCircle className="size-4" aria-hidden />}>Vizualizovať</Button>
              </Link>
            )}
            <Link to={`/experiments/new?problem=${problem.id}`}>
              <Button icon={<FlaskConical className="size-4" aria-hidden />}>Nový experiment</Button>
            </Link>
          </>
        }
      />

      <div className="mb-6 flex flex-wrap gap-1.5">
        <Tag>{CATEGORY[problem.category]}</Tag>
        {!problem.is_builtin && <Tag>vlastná úloha</Tag>}
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-6 min-w-0">
          <section aria-labelledby="popis">
            <h2 id="popis" className="sr-only">Popis</h2>
            <p className="prose-text text-[15px]">{problem.description}</p>
          </section>

          <Panel
            title={`Algoritmy (${algorithms.length})`}
            actions={canEdit && (
              <Link to={`/problems/${problem.id}/new`}>
                <Button size="sm" variant="ghost" icon={<Plus className="size-4" aria-hidden />}>Vlastný algoritmus</Button>
              </Link>
            )}
          >
            {algorithms.length ? (
              <AlgorithmTable algorithms={algorithms} referenceId={problem.reference_algorithm_id} />
            ) : (
              <Empty title="Úloha zatiaľ nemá algoritmus">Napíš prvý algoritmus a skontroluj ho na vygenerovanom vstupe.</Empty>
            )}
          </Panel>

          <Panel title="Pripravené experimenty">
            {experiments.length ? (
              <ul className="divide-y divide-line px-1 pb-1">
                {experiments.map((e) => (
                  <li key={e.id}>
                    <Link to={`/experiments/${e.id}`} className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 rounded-[var(--radius)] px-3 py-2.5 hover:bg-surface-2">
                      <span className="font-medium hover:text-accent">{e.name}</span>
                      <span className="text-[13px] text-ink-3">
                        {e.algorithm_ids.map((a) => algNames[a] ?? a).join(', ')}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <Empty title="Žiadny experiment">Vytvor experiment a porovnaj algoritmy tejto úlohy.</Empty>
            )}
          </Panel>
        </div>

        <aside className="space-y-6">
          <Panel title="Vstup a výstup">
            <dl className="space-y-3 px-4 pb-4 pt-1 text-sm">
              <div>
                <dt className="font-medium">Vstup</dt>
                <dd className="text-ink-2">{problem.input_description || 'Nie je popísaný.'}</dd>
              </div>
              <div>
                <dt className="font-medium">Výstup</dt>
                <dd className="text-ink-2">{problem.output_description || 'Nie je popísaný.'}</dd>
              </div>
              <div>
                <dt className="font-medium">Kontrola správnosti</dt>
                <dd className="text-ink-2">
                  {problem.checker_code
                    ? 'Výstup overí funkcia check, kód je nižšie.'
                    : problem.reference_algorithm_id
                      ? `Výstup sa porovná s výsledkom algoritmu ${algNames[problem.reference_algorithm_id] ?? 'referenčného'}.`
                      : 'Úloha nemá kontrolu správnosti.'}
                </dd>
              </div>
            </dl>
          </Panel>

          <Panel title="Generátory vstupov">
            <ul className="divide-y divide-line px-1 pb-1">
              {generators.map((g) => (
                <li key={g.id}>
                  <Link to={`/generators/${g.id}`} className="block rounded-[var(--radius)] px-3 py-2.5 hover:bg-surface-2">
                    <p className="font-medium">{g.name}</p>
                    <p className="text-[13px] text-ink-2">{g.description}</p>
                  </Link>
                </li>
              ))}
            </ul>
          </Panel>

          {problem.checker_code && (
            <details className="rounded-[var(--radius-lg)] border border-line bg-surface">
              <summary className="cursor-pointer px-4 py-3 text-[15px] font-semibold">Kód kontroly správnosti</summary>
              <div className="px-1 pb-1"><CodeView code={problem.checker_code.trim()} /></div>
            </details>
          )}
        </aside>
      </div>
    </>
  )
}
