import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Problems from './pages/Problems'
import Algorithms from './pages/Algorithms'
import Generator from './pages/Generator'
import Experiments from './pages/Experiments'
import Results from './pages/Results'
import Visualizer from './pages/Visualizer'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/problems" replace />} />
          <Route path="problems" element={<Problems />} />
          <Route path="algorithms" element={<Algorithms />} />
          <Route path="generator" element={<Generator />} />
          <Route path="experiments" element={<Experiments />} />
          <Route path="results" element={<Results />} />
          <Route path="visualizer" element={<Visualizer />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
