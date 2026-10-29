import { useCallback, useEffect, useRef, useState } from 'react'

export interface AsyncState<T> {
  data: T | undefined
  error: string | null
  loading: boolean
  reload: () => void
  setData: (value: T) => void
}

/** Načíta dáta pri zmene závislostí. Starší výsledok neprepíše novší. */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [data, setData] = useState<T | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [tick, setTick] = useState(0)
  const seq = useRef(0)

  useEffect(() => {
    const id = ++seq.current
    setLoading(true)
    setError(null)
    fn()
      .then((value) => {
        if (id === seq.current) setData(value)
      })
      .catch((e: unknown) => {
        if (id === seq.current) setError(e instanceof Error ? e.message : String(e))
      })
      .finally(() => {
        if (id === seq.current) setLoading(false)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick])

  const reload = useCallback(() => setTick((t) => t + 1), [])
  return { data, error, loading, reload, setData }
}

/** Hodnota uložená v localStorage, ak je dostupné. Len pre pohodlie jedného používateľa. */
export function useStoredState<T>(key: string, initial: T): [T, (v: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = localStorage.getItem(key)
      return raw === null ? initial : (JSON.parse(raw) as T)
    } catch {
      return initial
    }
  })
  const set = useCallback(
    (v: T) => {
      setValue(v)
      try {
        localStorage.setItem(key, JSON.stringify(v))
      } catch {
        /* nič */
      }
    },
    [key],
  )
  return [value, set]
}
