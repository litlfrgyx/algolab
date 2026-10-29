import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Copy, Eye, Save, Trash2 } from 'lucide-react'
import { ApiError, api } from '../api'
import { useAsync } from '../lib/hooks'
import { useEditAuth } from '../lib/auth'
import { formatNumber } from '../lib/labels'
import { CodeEditor } from '../components/CodeEditor'
import { ParamsForm, defaultParams } from '../components/ParamsForm'
import { Button, Field, Input, LoadError, Notice, PageHeader, Panel, Skeleton } from '../components/ui'
import { BackLink } from './ProblemDetail'
import type { GeneratorPreview, InputGenerator, Problem, Scalar } from '../types'

function Body({ generator, problem }: { generator: InputGenerator; problem: Problem }) {
  const navigate = useNavigate()
  const { canEdit, lock } = useEditAuth()
  const editable = !generator.is_builtin && canEdit
  const [code, setCode] = useState(generator.code)
  const [name, setName] = useState(generator.name)
  const [sizes, setSizes] = useState(generator.default_sizes.join(', '))
  const [n, setN] = useState(generator.viz_size)
  const [seed, setSeed] = useState(42)
  const [params, setParams] = useState<Record<string, Scalar>>(() => defaultParams(generator.param_spec))
  const [preview, setPreview] = useState<GeneratorPreview | null>(null)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  const run = async (what: string, fn: () => Promise<void>) => {
    setBusy(what)
    setError(null)
    try {
      await fn()
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) lock()
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(null)
    }
  }

  const doPreview = () => run('preview', async () => {
    const changed = code !== generator.code
    setPreview(changed ? await api.previewCode(code, n, params, seed) : await api.preview(generator.id, n, params, seed))
  })
  const save = () => run('save', async () => {
    const parsed = sizes.split(/[,\s]+/).filter(Boolean).map(Number).filter((x) => Number.isFinite(x) && x >= 0)
    await api.updateGenerator(generator.id, { name, code, default_sizes: parsed })
    setSaved(true)
  })
  const duplicate = () => run('dup', async () => {
    const copy = await api.duplicateGenerator(generator.id)
    navigate(`/generators/${copy.id}`)
  })
  const remove = () => run('del', async () => {
    if (!window.confirm(`Naozaj zmazať generátor ${generator.name}?`)) return
    await api.deleteGenerator(generator.id)
    navigate(`/problems/${problem.id}`)
  })

  return (
    <>
      <PageHeader
        back={<BackLink to={`/problems/${problem.id}`}>{problem.name}</BackLink>}
        title={generator.name}
        lead={generator.description}
        actions={generator.is_builtin && canEdit && (
          <Button icon={<Copy className="size-4" aria-hidden />} onClick={duplicate} loading={busy === 'dup'}>Duplikovať</Button>
        )}
      />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-4">
          {editable && (
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Názov"><Input value={name} onChange={(e) => { setName(e.target.value); setSaved(false) }} /></Field>
              <Field label="Predvolené veľkosti n" hint="oddelené čiarkou"><Input className="num" value={sizes} onChange={(e) => { setSizes(e.target.value); setSaved(false) }} /></Field>
            </div>
          )}
          <CodeEditor value={code} onChange={(v) => { setCode(v); setSaved(false) }} readOnly={!editable} height={Math.min(560, 19 * (code.split("\n").length + 1) + 24)} />
          {generator.is_builtin && <p className="text-[13px] text-ink-3">Vstavaný generátor sa nedá meniť. Kópiu po duplikovaní možno upraviť.</p>}
          {editable && (
            <div className="flex flex-wrap gap-2">
              <Button variant="primary" icon={<Save className="size-4" aria-hidden />} onClick={save} loading={busy === 'save'}>Uložiť</Button>
              <Button variant="danger" icon={<Trash2 className="size-4" aria-hidden />} onClick={remove} loading={busy === 'del'}>Zmazať</Button>
              {saved && <span className="self-center text-[13px] text-ok">Uložené</span>}
            </div>
          )}
        </div>
        <aside className="space-y-4">
          <Panel title="Náhľad vstupu">
            <div className="space-y-3 px-4 pb-4 pt-2">
              <div className="grid grid-cols-2 gap-3">
                <Field label="Veľkosť n"><Input type="number" min={0} className="num" value={n} onChange={(e) => setN(Number(e.target.value))} /></Field>
                <Field label="Seed" hint="rovnaký seed, rovnaký vstup"><Input type="number" className="num" value={seed} onChange={(e) => setSeed(Number(e.target.value))} /></Field>
              </div>
              <ParamsForm spec={generator.param_spec} value={params} onChange={setParams} />
              <Button icon={<Eye className="size-4" aria-hidden />} onClick={doPreview} loading={busy === 'preview'} className="w-full">Vygenerovať</Button>
              {error && <Notice tone="bad">{error}</Notice>}
              {preview && (preview.error ? (
                <Notice tone="bad" title="Generátor zlyhal">{preview.error}</Notice>
              ) : (
                <div className="space-y-2">
                  <p className="text-[13px] text-ink-3 num">
                    {preview.type}, dĺžka {formatNumber(preview.length)}, {formatNumber(preview.elapsed_ms, 2)} ms
                  </p>
                  <pre className="max-h-72 overflow-auto whitespace-pre-wrap break-all rounded-[var(--radius)] bg-surface-2 p-3 text-[12px] leading-relaxed">{preview.preview}</pre>
                </div>
              ))}
            </div>
          </Panel>
        </aside>
      </div>
    </>
  )
}

export default function GeneratorDetail() {
  const { id = '' } = useParams()
  const state = useAsync(async () => {
    const generator = await api.generator(id)
    const problem = await api.problem(generator.problem_id)
    return { generator, problem }
  }, [id])
  if (state.error) return <LoadError error={state.error} onRetry={state.reload} />
  if (!state.data) return <Skeleton className="h-96" />
  return <Body key={state.data.generator.id} {...state.data} />
}
