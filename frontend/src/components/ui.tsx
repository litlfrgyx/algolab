import { forwardRef, type ButtonHTMLAttributes, type ReactNode, type SelectHTMLAttributes, type InputHTMLAttributes } from 'react'
import { AlertTriangle, CircleCheck, Info, Loader2, XCircle } from 'lucide-react'

export function cx(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(' ')
}

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: 'sm' | 'md'
  icon?: ReactNode
  iconRight?: ReactNode
  loading?: boolean
}

const VARIANT: Record<Variant, string> = {
  primary: 'bg-accent text-accent-ink hover:bg-accent-hover border border-transparent',
  secondary: 'bg-surface text-ink border border-line-strong hover:bg-surface-2',
  ghost: 'bg-transparent text-ink-2 border border-transparent hover:bg-surface-2 hover:text-ink',
  danger: 'bg-surface text-bad border border-line-strong hover:bg-bad-soft',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = 'secondary', size = 'md', icon, iconRight, loading, className, children, disabled, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cx(
        'inline-flex items-center justify-center gap-2 rounded-[var(--radius)] font-medium whitespace-nowrap',
        'transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer',
        size === 'sm' ? 'h-8 px-2.5 text-[13px]' : 'h-9 px-3.5 text-sm',
        VARIANT[variant],
        className,
      )}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? <Loader2 className="size-4 animate-spin" aria-hidden /> : icon}
      {children}
      {iconRight}
    </button>
  )
})

export function Field({ label, hint, children, className }: { label: string; hint?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <label className={cx('flex flex-col gap-1.5 min-w-0', className)}>
      <span className="text-[13px] font-medium text-ink-2">{label}</span>
      {children}
      {hint && <span className="text-xs text-ink-3">{hint}</span>}
    </label>
  )
}

const control =
  'h-9 rounded-[var(--radius)] border border-line-strong bg-surface-2 px-2.5 text-sm text-ink ' +
  'hover:border-ink-3 focus:outline-none focus-visible:border-accent focus-visible:ring-2 focus-visible:ring-accent-soft'

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(function Select(
  { className, ...rest }, ref,
) {
  return <select ref={ref} className={cx(control, 'pr-7 cursor-pointer', className)} {...rest} />
})

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(function Input(
  { className, ...rest }, ref,
) {
  return <input ref={ref} className={cx(control, 'placeholder:text-ink-3', className)} {...rest} />
})

export function Tag({ children, tone = 'neutral', title }: { children: ReactNode; tone?: 'neutral' | 'accent' | 'ok' | 'warn' | 'bad'; title?: string }) {
  const tones = {
    neutral: 'bg-surface-2 text-ink-2',
    accent: 'bg-accent-soft text-accent',
    ok: 'bg-ok-soft text-ok',
    warn: 'bg-warn-soft text-warn',
    bad: 'bg-bad-soft text-bad',
  }
  return (
    <span title={title} className={cx('inline-flex items-center gap-1 rounded px-1.5 h-[22px] text-xs font-medium whitespace-nowrap', tones[tone])}>
      {children}
    </span>
  )
}

export function Notice({ tone = 'info', title, children, action }: { tone?: 'info' | 'warn' | 'bad' | 'ok'; title?: string; children?: ReactNode; action?: ReactNode }) {
  const Icon = { info: Info, warn: AlertTriangle, bad: XCircle, ok: CircleCheck }[tone]
  const tones = {
    info: 'bg-accent-soft text-ink [&_svg]:text-accent',
    warn: 'bg-warn-soft text-ink [&_svg]:text-warn',
    bad: 'bg-bad-soft text-ink [&_svg]:text-bad',
    ok: 'bg-ok-soft text-ink [&_svg]:text-ok',
  }
  return (
    <div role={tone === 'bad' ? 'alert' : 'status'} className={cx('flex gap-3 rounded-[var(--radius)] px-3.5 py-3 text-sm', tones[tone])}>
      <Icon className="size-4 mt-0.5 shrink-0" aria-hidden />
      <div className="min-w-0 flex-1 space-y-1">
        {title && <p className="font-medium">{title}</p>}
        {children && <div className="text-ink-2">{children}</div>}
      </div>
      {action}
    </div>
  )
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx('animate-pulse rounded bg-surface-2', className)} aria-hidden />
}

export function Panel({ children, className, title, actions, id }: { children: ReactNode; className?: string; title?: ReactNode; actions?: ReactNode; id?: string }) {
  return (
    <section id={id} className={cx('rounded-[var(--radius-lg)] border border-line bg-surface', className)}>
      {(title || actions) && (
        <header className="flex items-center justify-between gap-3 px-4 pt-3.5 pb-1">
          {typeof title === 'string' ? <h2 className="text-[15px] font-semibold">{title}</h2> : title}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>
      )}
      {children}
    </section>
  )
}

export function PageHeader({ title, lead, actions, back }: { title: ReactNode; lead?: ReactNode; actions?: ReactNode; back?: ReactNode }) {
  return (
    <header className="mb-6 flex flex-wrap items-end justify-between gap-x-6 gap-y-3">
      <div className="min-w-0 space-y-1.5">
        {back}
        <h1 className="text-2xl font-semibold tracking-[-0.01em]">{title}</h1>
        {lead && <p className="max-w-[72ch] text-[15px] text-ink-2">{lead}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </header>
  )
}

export function Segmented<T extends string>({ value, onChange, options, label }: {
  value: T
  onChange: (v: T) => void
  options: { value: T; label: string }[]
  label: string
}) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-[var(--radius)] bg-surface-2 p-0.5">
      {options.map((o) => (
        <button
          key={o.value}
          role="radio"
          aria-checked={value === o.value}
          onClick={() => onChange(o.value)}
          className={cx(
            'h-7 rounded-[5px] px-2.5 text-[13px] font-medium transition-colors cursor-pointer',
            value === o.value ? 'bg-surface text-ink shadow-[0_1px_2px_rgba(0,0,0,0.08)]' : 'text-ink-2 hover:text-ink',
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

export function Empty({ title, children, action }: { title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-start gap-2 px-4 py-8">
      <p className="font-medium">{title}</p>
      {children && <div className="text-sm text-ink-2 max-w-[60ch]">{children}</div>}
      {action && <div className="pt-1">{action}</div>}
    </div>
  )
}

export function LoadError({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <Notice tone="bad" title="Dáta sa nepodarilo načítať" action={onRetry && <Button size="sm" onClick={onRetry}>Skúsiť znova</Button>}>
      {error}
    </Notice>
  )
}
