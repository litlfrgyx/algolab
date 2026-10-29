import { cx } from './ui'

/**
 * Logo AlgoLab z pôvodného návrhu (banka s grafom a nápis). Obrázky s priehľadným
 * pozadím sú v public/brand v dvoch farebných verziách: tmavé logo pre svetlú tému
 * a svetlé logo pre tmavú tému. Prepína ich CSS podľa témy (triedy theme-light a theme-dark).
 */

function Themed({ name, alt, className, height }: { name: string; alt: string; className?: string; height: number }) {
  return (
    <>
      <img src={`/brand/${name}-light.png`} alt={alt} height={height} style={{ height }} className={cx('theme-light w-auto', className)} draggable={false} />
      <img src={`/brand/${name}-dark.png`} alt={alt} height={height} style={{ height }} className={cx('theme-dark w-auto', className)} draggable={false} />
    </>
  )
}

/** Len banka s grafom. */
export function LogoMark({ size = 36, className }: { size?: number; className?: string }) {
  return <Themed name="mark" alt="" height={size} className={className} />
}

/** Banka a nápis AlgoLab vedľa seba, do horných a bočných panelov. */
export function Logo({ size = 32, className }: { size?: number; className?: string }) {
  return (
    <span className={cx('inline-flex items-center gap-2', className)} role="img" aria-label="AlgoLab">
      <LogoMark size={size} />
      <Themed name="word" alt="" height={Math.round(size * 0.62)} />
    </span>
  )
}

/** Celé logo pod sebou, na väčšie plochy. */
export function LogoFull({ size = 160, className }: { size?: number; className?: string }) {
  return <Themed name="logo" alt="AlgoLab" height={size} className={className} />
}
