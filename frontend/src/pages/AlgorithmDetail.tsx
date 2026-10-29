import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { CheckCircle2, Copy, PlayCircle, Save, Trash2 } from 'lucide-react'
import { ApiError, api, type AlgorithmInput } from '../api'
import { useAsync } from '../lib/hooks'
import { useEditAuth } from '../lib/auth'
import { CASE_LABEL, LADDER, PARADIGM, PROPERTY, prettyO, propertyLabel } from '../lib/labels'
import { CodeEditor } from '../components/CodeEditor'
import { ComplexityLadder } from '../components/ComplexityLadder'
import { Button, Field, Input, LoadError, Notice, PageHeader, Panel, Select, Skeleton, Tag } from '../components/ui'
import { BackLink } from './ProblemDetail'
import type { Algorithm, ComplexityClass, Paradigm, Problem, ValidateResult } from '../types'

const TEMPLATES: Record<string, string> = {
  array: `def solve(data, tracker):
    """data je pole čísel. tracker zaznamenáva kroky pre vizualizáciu."""
    a = data
    for i in range(len(a) - 1):
        tracker.compare(i, i + 1)        # porovnanie dvoch prvkov
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
            tracker.swap(i, i + 1)       # výmena, pole je už zmenené
    return a
`,
  default: `def solve(data, tracker):
    """data je vstup úlohy podľa jej popisu.

    tracker.count("nazov") započíta operáciu, ktorú chceš merať.
    Metódy na vizualizáciu sú v Príručke.
    """
    tracker.count("krok")
    return data
`,
}

const COMPLEXITY_OPTIONS: ComplexityClass[] = [...LADDER, 'other']

type Draft = Required<Pick<AlgorithmInput, 'name' | 'code' | 'description' | 'paradigm' | 'complexity_note' | 'complexity_param' | 'properties'>> & {
  complexity_time_best: ComplexityClass | null
  complexity_time_avg: ComplexityClass | null
  complexity_time_worst: ComplexityClass | null
  complexity_space: ComplexityClass | null
}

function toDraft(a: Algorithm): Draft {
  return {
    name: a.name, code: a.code, description: a.description, paradigm: a.paradigm,
    complexity_time_best: a.complexity_time_best, complexity_time_avg: a.complexity_time_avg,
    complexity_time_worst: a.complexity_time_worst, complexity_space: a.complexity_space,
    complexity_note: a.complexity_note, complexity_param: a.complexity_param, properties: a.properties,
  }
}

function ComplexitySelect({ label, value, onChange }: { label: string; value: ComplexityClass | null; onChange: (v: ComplexityClass | null) => void }) {
  return (
    <Field label={label}>
      <Select value={value ?? ''} onChange={(e) => onChange((e.target.value || null) as ComplexityClass | null)}>
        <option value="">neuvedená</option>
        {COMPLEXITY_OPTIONS.map((c) => <option key={c} value={c}>{prettyO(c)}</option>)}
      </Select>
    </Field>
  )
}

function ReadOnlyMeta({ a }: { a: Algorithm }) {
  return (
    <Panel title="Zložitosť a vlastnosti">
      <div className="space-y-4 px-4 pb-4 pt-2 text-sm">
        <ComplexityLadder best={a.complexity_time_best} avg={a.complexity_time_avg} worst={a.complexity_time_worst} />
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
          {(['best', 'avg', 'worst'] as const).map((k) => (
            <div key={k} className="contents">
              <dt className="text-ink-2">{CASE_LABEL[k]}</dt>
              <dd className="font-medium num">{prettyO(a[`complexity_time_${k}`])}</dd>
            </div>
          ))}
          <dt className="text-ink-2">pamäť</dt>
          <dd className="font-medium num">{prettyO(a.complexity_space)}</dd>
          {a.complexity_param && (<><dt className="text-ink-2">n je</dt><dd>{a.complexity_param}</dd></>)}
        </dl>
        {a.complexity_note && <p className="text-ink-2">{a.complexity_note}</p>}
        <div className="flex flex-wrap gap-1.5">
          <Tag>{PARADIGM[a.paradigm]}</Tag>
          {a.properties.map((p) => <Tag key={p} tone={p === 'intentionally_incorrect' ? 'warn' : 'neutral'}>{propertyLabel(p)}</Tag>)}
        </div>
      </div>
    </Panel>
  )
}

function Editor({ problem, initial, algorithm }: { problem: Problem; initial: Draft; algorithm?: Algorithm }) {
  const navigate = useNavigate()
  const { lock } = useEditAuth()
  const [draft, setDraft] = useState<Draft>(initial)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [check, setCheck] = useState<ValidateResult | null>(null)
  const up = <K extends keyof Draft>(k: K, v: Draft[K]) => {
    setDraft((d) => ({ ...d, [k]: v }))
    setSaved(false)
  }


  const save = async () => {
    setSaving(true)
    setError(null)
    try {
      if (algorithm) {
        await api.updateAlgorithm(algorithm.id, draft)
        setSaved(true)
      } else {
        const created = await api.createAlgorithm(problem.id, draft)
        navigate(`/algorithms/${created.id}`, { replace: true })
      }
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) lock()
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setSaving(false)
    }
  }

  const validate = async () => {
    try {
      setCheck(await api.validate(draft.code, 'algorithm'))
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  const remove = async () => {
    if (!algorithm) return
    if (!window.confirm(`Naozaj zmazať algoritmus ${algorithm.name}?`)) return
    try {
      await api.deleteAlgorithm(algorithm.id)
      navigate(`/problems/${problem.id}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div className="min-w-0 space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Názov"><Input value={draft.name} onChange={(e) => up('name', e.target.value)} /></Field>
          <Field label="Prístup">
            <Select value={draft.paradigm} onChange={(e) => up('paradigm', e.target.value as Paradigm)}>
              {(Object.keys(PARADIGM) as Paradigm[]).map((p) => <option key={p} value={p}>{PARADIGM[p]}</option>)}
            </Select>
          </Field>
        </div>
        <Field label="Popis myšlienky">
          <Input value={draft.description} onChange={(e) => up('description', e.target.value)} placeholder="Jedna veta o tom, ako algoritmus postupuje" />
        </Field>
        <CodeEditor value={draft.code} onChange={(v) => { up('code', v); setCheck(null) }} height={460} />
        {check && (
          check.valid && !check.errors.length ? (
            <Notice tone="ok" title="Kód je v poriadku">Funkcia solve prijíma tracker, algoritmus sa dá merať aj vizualizovať.</Notice>
          ) : (
            <Notice tone={check.valid ? 'warn' : 'bad'} title={check.valid ? 'Kód sa dá spustiť, ale pozri upozornenie' : 'Kód treba opraviť'}>
              <ul className="list-disc pl-4">
                {check.errors.map((e, i) => <li key={i}>{e.line ? `Riadok ${e.line}: ` : ''}{e.message}</li>)}
              </ul>
            </Notice>
          )
        )}
        {error && <Notice tone="bad" title="Uloženie zlyhalo">{error}</Notice>}
        <div className="flex flex-wrap gap-2">
          <Button variant="primary" icon={<Save className="size-4" aria-hidden />} onClick={save} loading={saving} disabled={!draft.name.trim()}>
            {algorithm ? 'Uložiť zmeny' : 'Vytvoriť algoritmus'}
          </Button>
          <Button icon={<CheckCircle2 className="size-4" aria-hidden />} onClick={validate}>Overiť kód</Button>
          {algorithm && (
            <Link to={`/visualizer?problem=${problem.id}&a=${algorithm.id}`}>
              <Button icon={<PlayCircle className="size-4" aria-hidden />}>Vizualizovať</Button>
            </Link>
          )}
          {algorithm && <Button variant="danger" icon={<Trash2 className="size-4" aria-hidden />} onClick={remove}>Zmazať</Button>}
          {saved && <span className="self-center text-[13px] text-ok">Uložené</span>}
        </div>
      </div>
      <aside className="space-y-4">
        <Panel title="Deklarovaná zložitosť">
          <div className="space-y-3 px-4 pb-4 pt-2">
            <p className="text-[13px] text-ink-2">Experiment porovná odhad z merania s týmito triedami.</p>
            <ComplexitySelect label="Najlepší prípad" value={draft.complexity_time_best} onChange={(v) => up('complexity_time_best', v)} />
            <ComplexitySelect label="Priemerný prípad" value={draft.complexity_time_avg} onChange={(v) => up('complexity_time_avg', v)} />
            <ComplexitySelect label="Najhorší prípad" value={draft.complexity_time_worst} onChange={(v) => up('complexity_time_worst', v)} />
            <ComplexitySelect label="Pamäť" value={draft.complexity_space} onChange={(v) => up('complexity_space', v)} />
            <Field label="Poznámka"><Input value={draft.complexity_note} onChange={(e) => up('complexity_note', e.target.value)} placeholder="napríklad O(n + m)" /></Field>
          </div>
        </Panel>
        <Panel title="Vlastnosti">
          <div className="flex flex-wrap gap-x-4 gap-y-2 px-4 pb-4 pt-2 text-sm">
            {Object.entries(PROPERTY).map(([k, label]) => (
              <label key={k} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="size-4 accent-[var(--accent)]"
                  checked={draft.properties.includes(k)}
                  onChange={(e) => up('properties', e.target.checked ? [...draft.properties, k] : draft.properties.filter((p) => p !== k))}
                />
                {label}
              </label>
            ))}
          </div>
        </Panel>
      </aside>
    </div>
  )
}

export function NewAlgorithm() {
  const { id = '' } = useParams()
  const { canEdit } = useEditAuth()
  const state = useAsync(() => api.problem(id), [id])
  if (state.error) return <LoadError error={state.error} />
  if (!state.data) return <Skeleton className="h-96" />
  const problem = state.data
  const initial: Draft = {
    name: 'Môj algoritmus', description: '', paradigm: 'iterative', code: TEMPLATES[problem.renderer] ?? TEMPLATES.default,
    complexity_time_best: null, complexity_time_avg: null, complexity_time_worst: null, complexity_space: null,
    complexity_note: '', complexity_param: '', properties: [],
  }
  return (
    <>
      <PageHeader back={<BackLink to={`/problems/${problem.id}`}>{problem.name}</BackLink>} title="Nový algoritmus"
        lead={`Vstup: ${problem.input_description} Výstup: ${problem.output_description}`} />
      {!canEdit ? <Notice tone="warn" title="Úpravy sú zamknuté">Vlastný kód sa dá písať po odomknutí úprav v ľavom paneli.</Notice>
        : <Editor problem={problem} initial={initial} />}
    </>
  )
}

export default function AlgorithmDetail() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const { canEdit, lock } = useEditAuth()
  const [dupError, setDupError] = useState<string | null>(null)
  const [duplicating, setDuplicating] = useState(false)
  const state = useAsync(async () => {
    const algorithm = await api.algorithm(id)
    const problem = await api.problem(algorithm.problem_id)
    return { algorithm, problem, draft: toDraft(algorithm) }
  }, [id])

  if (state.error) return <LoadError error={state.error} onRetry={state.reload} />
  if (!state.data) return <div className="space-y-4"><Skeleton className="h-10 w-80" /><Skeleton className="h-96" /></div>
  const { algorithm: a, problem, draft } = state.data

  const duplicate = async () => {
    setDuplicating(true)
    setDupError(null)
    try {
      const copy = await api.duplicateAlgorithm(a.id)
      navigate(`/algorithms/${copy.id}`)
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) lock()
      setDupError(e instanceof Error ? e.message : String(e))
    } finally {
      setDuplicating(false)
    }
  }

  const dupButton = canEdit && (
    <Button icon={<Copy className="size-4" aria-hidden />} onClick={duplicate} loading={duplicating}>Duplikovať</Button>
  )

  return (
    <>
      <PageHeader
        back={<BackLink to={`/problems/${problem.id}`}>{problem.name}</BackLink>}
        title={a.name}
        lead={a.description}
        actions={
          <>
            {a.supports_visualization && problem.renderer !== 'none' && (
              <Link to={`/visualizer?problem=${problem.id}&a=${a.id}`}>
                <Button variant="primary" icon={<PlayCircle className="size-4" aria-hidden />}>Vizualizovať</Button>
              </Link>
            )}
            {dupButton}
          </>
        }
      />
      {dupError && <div className="mb-4"><Notice tone="bad" title="Kópia sa nevytvorila">{dupError}</Notice></div>}
      {a.is_builtin || !canEdit ? (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="min-w-0 space-y-3">
            {a.is_builtin && (
              <p className="text-[13px] text-ink-3">
                Vstavaný algoritmus sa nedá meniť. {canEdit ? 'Duplikuj ho a uprav kópiu.' : 'Na úpravy kópie treba odomknúť úpravy.'}
              </p>
            )}
            <CodeEditor value={a.code.trim() + '\n'} readOnly height={Math.min(640, 19 * (a.code.trim().split("\n").length + 1) + 24)} />
          </div>
          <aside><ReadOnlyMeta a={a} /></aside>
        </div>
      ) : (
        <Editor key={a.id + a.updated_at} problem={problem} initial={draft} algorithm={a} />
      )}
    </>
  )
}
