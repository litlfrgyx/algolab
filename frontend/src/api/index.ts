// Jediný prístupový bod k dátovej vrstve.
//   import { api } from '../api'
//
// Predvolene reálny backend (HttpApiClient). Pre offline/demo bez backendu
// nastav VITE_USE_MOCK=true (napr. v .env.local) → použije sa MockApiClient.

import { MockApiClient } from './client'
import { HttpApiClient } from './http'
import type { ApiClient } from '../types'

const useMock = import.meta.env.VITE_USE_MOCK === 'true'

export const api: ApiClient = useMock ? new MockApiClient() : new HttpApiClient()
