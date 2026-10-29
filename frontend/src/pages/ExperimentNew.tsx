import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { FlaskConical } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { useEditAuth } from '../lib/auth'
import { prettyO } from '../lib/labels'
import { ParamsForm, defaultParams, optionLabel } from '../components/ParamsForm'
import { Button, Field, Input, LoadError, Notice, PageHeader, Panel, Select, Skeleton } from '../components/ui'
import { BackLink } from './ProblemDetail'
import type { Scalar } from '../types'

export default function ExperimentNew() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { info } = useEditAuth()
  const maxAlgs = info?.max_algorithms ?? 8
  const problems = useAsync(() => api.problems(), [])
  const [problemId, setProblemId] = useState(params.get('problem') ?? '')
  useEffect(() => {
    if (!problemId && problems.data?.length) setProblemId(problems.data[0].id)
  }, [problems.data, problemId])

  const detail = useAsync(async () => {
    if (!problemId) return null
    const [algorithms, generators] = await Promise.all([api.problemAlgorithms(problemId), api.problemGenerators(problemId)])
    return { algorithms, generators }
  }, [problemId])

  const [selected, setSelected] = useState<string[]>([])
  const [generatorId, setGeneratorId] = useState('')
  const [sizes, setSizes] = useState('')
  const [repeats, setRepeats] = useState(3)
  const [seed, setSeed] = useState(42)
  const [genParams, setGenParams] = useState<Record<string, Scalar>>({})
  const [variantOptions, setVariantOptions] = useState<string[]>([])
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const generator = detail.data?.generators.find((g) => g.id === generatorId) ?? detail.data?.generators[0]
  const variantParam = generator?.param_spec.find((p) => p.type === 'enum')

  // nová úloha: predvolený výber
  useEffect(() => {
    if (!detail.data) return
    setSelected(detail.data.algorithms.slice(0, Math.min(3, maxAlgs)).map((a) => a.id))
    const g = detail.data.generators[0]
    setGeneratorId(g?.id ?? '')
  }, [detail.data, maxAlgs])

  useEffect(() => {
    if (!generator) return
    setSizes(generator.default_sizes.join(', '))
    setGenParams(defaultParams(generator.param_spec))
    setVariantOptions([])
  }, [generator])

  const algNames = useMemo(() => Object.fromEntries((detail.data?.algorithms ?? []).map((a) => [a.id, a.name])), [detail.data])
  const autoName = selected.length ? selected.map((id) => algNames[id]).filter(Boolean).join(', ') : 'Nový experiment'
  const parsedSizes = sizes.split(/[,\s;]+/).filter(Boolean).map(Number)
  const sizesOk = parsedSizes.length >= 1 && parsedSizes.every((x) => Number.isInteger(x) && x >= 0)
  const cases = Math.max(1, variantOptions.length) * parsedSizes.length * repeats

  const toggle = (id: string) =>
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : s.length >= maxAlgs ? s : [...s, id]))

  const submit = async () => {
    if (!generator) return
    setSaving(true)
    setError(null)
    try {
      const variants = variantParam && variantOptions.length
        ? variantOptions.map((o) => ({ label: optionLabel(variantParam, o), params: { [variantParam.name]: o } }))
        : []
      const exp = await api.createExperiment({
        name: name.trim() || autoName,
        problem_id: problemId,
        algorithm_ids: selected,
        generator_id: generator.id,
        sizes: parsedSizes,
        repeats,
        seed,
        generator_params: genParams,
        variants,
      })
      navigate(`/experiments/${exp.id}?start=1`)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setSaving(false)
    }
  }

  if (problems.error) return <LoadError error={problems.error} onRetry={problems.reload} />

  return (
    <>
      <PageHeader back={<BackLink to="/experiments">Experimenty</BackLink>} title="Nový experiment"
        lead="Všetky algoritmy dostanú v každom prípade ten istý vstup. Každá veľkosť sa zopakuje s iným seedom a výsledky sa spriemerujú." />
      {!problems.data ? <Skeleton className="h-96" /> : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="min-w-0 space-y-6">
            <Panel title="Úloha a algoritmy">
              <div className="space-y-4 px-4 pb-4 pt-2">
                <Field label="Úloha">
                  <Select value={problemId} onChange={(e) => setProblemId(e.target.value)}>
                    {problems.data.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </Select>
                </Field>
                <fieldset>
                  <legend className="mb-2 text-[13px] font-medium text-ink-2">Algoritmy, najviac {maxAlgs}</legend>
                  {!detail.data ? <Skeleton className="h-24" /> : (
                    <ul className="grid gap-1 sm:grid-cols-2">
                      {detail.data.algorithms.map((a) => (
                        <li key={a.id}>
                          <label className="flex cursor-pointer items-start gap-2.5 rounded-[var(--radius)] px-2 py-1.5 hover:bg-surface-2">
                            <input type="checkbox" className="mt-0.5 size-4 accent-[var(--accent)]" checked={selected.includes(a.id)}
                              onChange={() => toggle(a.id)} disabled={!selected.includes(a.id) && selected.length >= maxAlgs} />
                            <span>
                              <span className="block text-sm">{a.name}</span>
                              <span className="block text-xs text-ink-3 num">priemer {prettyO(a.complexity_time_avg)}, najhorší {prettyO(a.complexity_time_worst)}</span>
                            </span>
                          </label>
                        </li>
                      ))}
                    </ul>
                  )}
                </fieldset>
              </div>
            </Panel>

            {generator && (
              <Panel title="Vstupy">
                <div className="grid gap-4 px-4 pb-4 pt-2 sm:grid-cols-2">
                  {detail.data && detail.data.generators.length > 1 && (
                    <Field label="Generátor">
                      <Select value={generator.id} onChange={(e) => setGeneratorId(e.target.value)}>
                        {detail.data.generators.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                      </Select>
                    </Field>
                  )}
                  <Field label="Veľkosti vstupu n" hint="oddelené čiarkou, napríklad 250, 500, 1000, 2000">
                    <Input className="num" value={sizes} onChange={(e) => setSizes(e.target.value)} aria-invalid={!sizesOk} />
                  </Field>
                  <Field label="Opakovania pre každú veľkosť">
                    <Input type="number" min={1} max={10} className="num" value={repeats} onChange={(e) => setRepeats(Math.max(1, Math.min(10, Number(e.target.value) || 1)))} />
                  </Field>
                  <ParamsForm spec={generator.param_spec} value={genParams} onChange={setGenParams}
                    exclude={variantOptions.length && variantParam ? [variantParam.name] : []} />
                  <Field label="Seed" hint="rovnaký seed dá rovnaké vstupy">
                    <Input type="number" className="num" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
                  </Field>
                </div>
                {variantParam && (
                  <fieldset className="border-t border-line px-4 py-4">
                    <legend className="sr-only">Varianty vstupu</legend>
                    <p className="mb-2 text-[13px] font-medium text-ink-2">Porovnať aj podľa parametra {variantParam.label.toLowerCase()}</p>
                    <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm">
                      {(variantParam.options ?? []).map((o) => (
                        <label key={o} className="flex cursor-pointer items-center gap-2">
                          <input type="checkbox" className="size-4 accent-[var(--accent)]" checked={variantOptions.includes(o)}
                            onChange={(e) => setVariantOptions((v) => (e.target.checked ? [...v, o] : v.filter((x) => x !== o)))} />
                          {optionLabel(variantParam, o)}
                        </label>
                      ))}
                    </div>
                    <p className="mt-2 text-xs text-ink-3">Každá zaškrtnutá hodnota je samostatný variant s vlastným grafom a odhadom zložitosti.</p>
                  </fieldset>
                )}
              </Panel>
            )}
          </div>

          <aside className="space-y-4">
            <Panel title="Zhrnutie">
              <div className="space-y-3 px-4 pb-4 pt-2 text-sm">
                <Field label="Názov"><Input value={name} placeholder={autoName} onChange={(e) => setName(e.target.value)} /></Field>
                <p className="text-ink-2 num">
                  {selected.length} {selected.length === 1 ? 'algoritmus' : 'algoritmy'}, {cases} {cases === 1 ? 'prípad' : cases < 5 ? 'prípady' : 'prípadov'}
                  {parsedSizes.length < 4 && ' (na odhad zložitosti treba aspoň 4 veľkosti)'}
                </p>
                {error && <Notice tone="bad">{error}</Notice>}
                <Button variant="primary" className="w-full" icon={<FlaskConical className="size-4" aria-hidden />}
                  onClick={submit} loading={saving} disabled={!selected.length || !sizesOk || !generator}>
                  Vytvoriť a spustiť
                </Button>
              </div>
            </Panel>
          </aside>
        </div>
      )}
    </>
  )
}
