import type { GeneratorParamSpec, Scalar } from '../types'
import { Field, Input, Select } from './ui'

export function defaultParams(spec: GeneratorParamSpec[]): Record<string, Scalar> {
  return Object.fromEntries(spec.map((p) => [p.name, p.default]))
}

export function optionLabel(spec: GeneratorParamSpec, value: Scalar): string {
  return spec.option_labels?.[String(value)] ?? String(value)
}

export function ParamsForm({ spec, value, onChange, exclude = [] }: {
  spec: GeneratorParamSpec[]
  value: Record<string, Scalar>
  onChange: (v: Record<string, Scalar>) => void
  exclude?: string[]
}) {
  return (
    <>
      {spec.filter((p) => !exclude.includes(p.name)).map((p) => (
        <Field key={p.name} label={p.label}>
          {p.type === 'enum' ? (
            <Select value={String(value[p.name] ?? p.default)} onChange={(e) => onChange({ ...value, [p.name]: e.target.value })}>
              {(p.options ?? []).map((o) => <option key={o} value={o}>{optionLabel(p, o)}</option>)}
            </Select>
          ) : p.type === 'boolean' ? (
            <Select value={String(value[p.name] ?? p.default)} onChange={(e) => onChange({ ...value, [p.name]: e.target.value === 'true' })}>
              <option value="true">áno</option>
              <option value="false">nie</option>
            </Select>
          ) : (
            <Input
              type="number"
              className="num"
              value={String(value[p.name] ?? p.default ?? '')}
              onChange={(e) => onChange({ ...value, [p.name]: e.target.value === '' ? null : Number(e.target.value) })}
            />
          )}
        </Field>
      ))}
    </>
  )
}
