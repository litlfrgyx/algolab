import { cx } from './ui'

/**
 * Logo AlgoLab: laboratórna banka, v nej rastúci graf meraní a malý graf vrcholov.
 * Prekreslené do SVG z návrhu loga, farby idú z tokenov --logo-ink a --logo-accent,
 * takže logo funguje vo svetlej aj tmavej téme.
 */
export function LogoMark({ className, detailed = false }: { className?: string; detailed?: boolean }) {
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden fill="none" strokeLinecap="round" strokeLinejoin="round">
      {/* para z hrdla banky, len vo väčšej verzii */}
      {detailed && <path d="M31.5 20 C30 13 33.5 7.5 40.5 4.5" stroke="var(--logo-ink)" strokeWidth="2.2" />}
      {/* banka */}
      <path d="M20.5 8.5 H43.5" stroke="var(--logo-ink)" strokeWidth="3.6" />
      <path
        d="M24.5 9 V23.5 L9.6 49.6 Q6.6 56.4 13.6 57 H50.4 Q57.4 56.4 54.4 49.6 L39.5 23.5 V9"
        stroke="var(--logo-ink)"
        strokeWidth="3.4"
      />
      {/* rastúci graf meraní so šípkou */}
      <path d="M14.5 50 L23 41.5 L31 45.5 L40 36.5 L48.5 28" stroke="var(--logo-accent)" strokeWidth="2.6" />
      <path d="M51.5 25 L44.6 26.4 L50.1 31.9 Z" fill="var(--logo-accent)" stroke="var(--logo-accent)" strokeWidth="1.4" />
      <circle cx="14.5" cy="50" r="2.7" fill="var(--logo-bg)" stroke="var(--logo-ink)" strokeWidth="2" />
      <circle cx="23" cy="41.5" r="2.7" fill="var(--logo-bg)" stroke="var(--logo-accent)" strokeWidth="2" />
      <circle cx="31" cy="45.5" r="2.7" fill="var(--logo-bg)" stroke="var(--logo-accent)" strokeWidth="2" />
      <circle cx="40" cy="36.5" r="2.7" fill="var(--logo-bg)" stroke="var(--logo-accent)" strokeWidth="2" />
      {detailed && (
        <g strokeWidth="1.8">
          <path d="M37 52.5 H45.5 M45.5 46.5 V52.5 M37 52.5 V47 H42" stroke="var(--logo-ink)" />
          <circle cx="37" cy="52.5" r="2.3" fill="var(--logo-accent)" stroke="none" />
          <circle cx="45.5" cy="52.5" r="2" fill="var(--logo-ink)" stroke="none" />
          <circle cx="45.5" cy="46.5" r="2" fill="var(--logo-ink)" stroke="none" />
          <circle cx="42" cy="47" r="2" fill="var(--logo-accent)" stroke="none" />
        </g>
      )}
    </svg>
  )
}

export function Logo({ className, size = 28, detailed = false }: { className?: string; size?: number; detailed?: boolean }) {
  return (
    <span className={cx('inline-flex items-center gap-2', className)}>
      <span className="shrink-0" style={{ width: size, height: size }}>
        <LogoMark detailed={detailed} className="size-full" />
      </span>
      <span className="sr-only">AlgoLab</span>
      <span aria-hidden className="font-semibold tracking-[-0.01em] text-[var(--logo-ink)]" style={{ fontSize: size * 0.62 }}>
        Algo<span className="font-medium">Lab</span>
      </span>
    </span>
  )
}
