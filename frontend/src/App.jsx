import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import EvaluationWorkspace from './pages/EvaluationWorkspace'
import EvaluationProgress from './pages/EvaluationProgress'
import ComparisonDashboard from './pages/ComparisonDashboard'
import ClaimVerificationReport from './pages/ClaimVerificationReport'
import TrustReport from './pages/TrustReport'
import DemoPage from './pages/DemoPage'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/evaluate" element={<EvaluationWorkspace />} />
        <Route path="/evaluate/:id/progress" element={<EvaluationProgress />} />
        <Route path="/evaluate/:id/dashboard" element={<ComparisonDashboard />} />
        <Route path="/evaluate/:id/claims" element={<ClaimVerificationReport />} />
        <Route path="/evaluate/:id/report" element={<TrustReport />} />
        <Route path="/demo" element={<DemoPage />} />
        {/* Redirect /demo/* to the demo evaluation views */}
        <Route path="/evaluate/demo/dashboard" element={<ComparisonDashboard />} />
        <Route path="/evaluate/demo/claims" element={<ClaimVerificationReport />} />
        <Route path="/evaluate/demo/report" element={<TrustReport />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
