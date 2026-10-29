import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, getPassword, setPassword } from '../api'
import type { CatalogInfo } from '../types'

interface EditAuth {
  info: CatalogInfo | null
  /** Smie používateľ vytvárať a upravovať vlastný kód? */
  canEdit: boolean
  /** Je úprava chránená heslom (nasadená verzia)? */
  protectedMode: boolean
  unlock: (password: string) => void
  lock: () => void
}

const Ctx = createContext<EditAuth>({
  info: null, canEdit: true, protectedMode: false, unlock: () => {}, lock: () => {},
})

export function EditAuthProvider({ children }: { children: ReactNode }) {
  const [info, setInfo] = useState<CatalogInfo | null>(null)
  const [hasPassword, setHasPassword] = useState(() => !!getPassword())

  useEffect(() => {
    api.info().then(setInfo).catch(() => setInfo(null))
  }, [])

  const unlock = useCallback((password: string) => {
    setPassword(password)
    setHasPassword(!!password)
  }, [])
  const lock = useCallback(() => {
    setPassword('')
    setHasPassword(false)
  }, [])

  const protectedMode = !!info?.edit_protected
  return (
    <Ctx.Provider value={{ info, canEdit: !protectedMode || hasPassword, protectedMode, unlock, lock }}>
      {children}
    </Ctx.Provider>
  )
}

 
export const useEditAuth = () => useContext(Ctx)
