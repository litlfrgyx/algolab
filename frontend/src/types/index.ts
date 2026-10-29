// Barrel: jediný import bod pre celý zdieľaný kontrakt.
//   import type { Problem, Step, VisualizationTrace, ApiClient } from '../types'
// (Voliteľne sa v Fáze 0 dá pridať alias '@/types' cez tsconfig `paths` +
//  vite `resolve.alias`; zatiaľ projekt alias nemá, preto relatívna cesta.)
export * from './domain'
export * from './steps'
export * from './api'
