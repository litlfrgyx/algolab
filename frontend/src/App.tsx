import { lazy } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { EditAuthProvider } from './lib/auth'
import Landing from './pages/Landing'
const Problems = lazy(() => import('./pages/Problems'))
const ProblemDetail = lazy(() => import('./pages/ProblemDetail'))
const Algorithms = lazy(() => import('./pages/Algorithms'))
const AlgorithmDetail = lazy(() => import('./pages/AlgorithmDetail'))
const NewAlgorithm = lazy(() => import('./pages/AlgorithmDetail').then((m) => ({ default: m.NewAlgorithm })))
const GeneratorDetail = lazy(() => import('./pages/GeneratorDetail'))
const Visualizer = lazy(() => import('./pages/Visualizer'))
const Experiments = lazy(() => import('./pages/Experiments'))
const ExperimentNew = lazy(() => import('./pages/ExperimentNew'))
const ExperimentDetail = lazy(() => import('./pages/ExperimentDetail'))
const Guide = lazy(() => import('./pages/Guide'))

export default function App() {
  return (
    <EditAuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route element={<Layout />}>
            <Route path="problems" element={<Problems />} />
            <Route path="problems/:id" element={<ProblemDetail />} />
            <Route path="problems/:id/new" element={<NewAlgorithm />} />
            <Route path="algorithms" element={<Algorithms />} />
            <Route path="algorithms/:id" element={<AlgorithmDetail />} />
            <Route path="generators/:id" element={<GeneratorDetail />} />
            <Route path="visualizer" element={<Visualizer />} />
            <Route path="experiments" element={<Experiments />} />
            <Route path="experiments/new" element={<ExperimentNew />} />
            <Route path="experiments/:id" element={<ExperimentDetail />} />
            <Route path="guide" element={<Guide />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </EditAuthProvider>
  )
}
