/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL backendu. Predvolene http://localhost:8000. */
  readonly VITE_API_BASE?: string
  /** "true" → použi MockApiClient namiesto reálneho backendu (offline/demo). */
  readonly VITE_USE_MOCK?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
