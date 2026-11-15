import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { getEvaluation } from '../lib/api'
import ScoreRing from '../components/ScoreRing'
import {
  Clock, Cpu, DollarSign, CheckCircle, XCircle,
  AlertTriangle, HelpCircle, FileText, ArrowRight,
  Info, Shield, Zap,
} from 'lucide-react'

const MODEL_COLORS = ['var(--blue-400)', 'var(--purple-400)', 'var(--teal-400)', 'var(--amber-400)', 'var(--rose-400)']

const MetricCell = ({ value, format = 'default', unavailableLabel = 'Unavailable' }) => {
  if (value === null || value === undefined) {
    return <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{unavailableLabel}</span>
  }
  if (format === 'ms') return <span>{value.toFixed(0)}ms</span>
  if (format === 'tokens') return <span>{value.toLocaleString()}</span>
  if (format === 'cost') return <span style={{ color: 'var(--teal-400)' }}>${value.toFixed(5)} <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>(est.)</span></span>
  if (format === 'score') {
    const color = value >= 70 ? 'var(--emerald-400)' : value >= 40 ? 'var(--amber-400)' : 'var(--rose-400)'
    return <span style={{ fontWeight: 700, color }}>{value.toFixed(1)}</span>
  }
  return <span>{value}</span>
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', fontSize: 13 }}>
      <div style={{ fontWeight: 700, marginBottom: 6 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ color: p.color, display: 'flex', gap: 8 }}>
          <span>{p.name}:</span>
          <span style={{ fontWeight: 700 }}>{p.value.toFixed(1)}</span>
        </div>
      ))}
    </div>
  )
}

export default function ComparisonDashboard() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedResponse, setExpandedResponse] = useState(null)

  const isDemo = id === 'demo'

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getEvaluation(id)
        setEvaluation(res.data)
      } catch (e) {
        setError(e.response?.data?.detail || 'Failed to load evaluation.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: 16 }}>
      <div className="spinner spinner-lg" />
      <div style={{ color: 'var(--text-muted)' }}>Loading comparison dashboard…</div>
    </div>
  )

  if (error) return (
    <div className="container" style={{ paddingTop: 40 }}>
      <div className="error-box">{error}</div>
    </div>
  )

  const models = evaluation?.models || []
  const successModels = models.filter(m => m.response_text || (m.trust_score !== null && m.trust_score !== undefined))

  // Build chart data
  const trustChartData = successModels.map((m, i) => ({
    name: m.display_name || m.model_id,
    'Trust Score': m.trust_score ?? 0,
    'Efficiency Score': m.efficiency_score ?? 0,
    color: MODEL_COLORS[i],
  }))

  const claimChartData = successModels.map((m, i) => ({
    name: m.display_name || m.model_id,
    Supported: m.verified_claims || 0,
    Contradicted: m.contradicted_claims || 0,
    Outdated: m.outdated_claims || 0,
    Unverifiable: m.unverifiable_claims || 0,
    color: MODEL_COLORS[i],
  }))

  // Find best models
  const bestTrust = successModels.reduce((best, m) => (!best || (m.trust_score ?? 0) > (best.trust_score ?? 0)) ? m : best, null)
  const bestEfficiency = successModels.reduce((best, m) => (!best || (m.efficiency_score ?? 0) > (best.efficiency_score ?? 0)) ? m : best, null)

  return (
    <div style={{ minHeight: '100vh', paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)', padding: '24px' }}>
        <div className="container">
          {isDemo || evaluation?.demo_mode ? (
            <div className="demo-banner">
              <AlertTriangle size={16} />
              <strong>DEMO MODE</strong> — All data below is pre-prepared sample data. No real API calls were made.
            </div>
          ) : null}

          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <h1 className="page-title">Comparison Dashboard</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
                {evaluation?.task?.slice(0, 100)}{evaluation?.task?.length > 100 ? '…' : ''}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Link to={`/evaluate/${id}/claims`} className="btn btn-secondary btn-sm">
                <FileText size={14} />
                Claim Report
              </Link>
              <Link to={`/evaluate/${id}/report`} className="btn btn-primary btn-sm">
                <Shield size={14} />
                Trust Report
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container" style={{ paddingTop: 32 }}>
        {/* Model score cards */}
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(successModels.length, 3)}, 1fr)`, gap: 16, marginBottom: 32 }}>
          {successModels.map((model, i) => (
            <div key={model.model_id} className="card animate-fade-in" style={{ animationDelay: `${i * 0.1}s`, position: 'relative' }}>
              {/* Best badge */}
              {bestTrust?.model_id === model.model_id && (
                <div style={{
                  position: 'absolute', top: -10, right: 16,
                  background: 'var(--gradient-primary)', borderRadius: 100,
                  padding: '3px 10px', fontSize: 11, fontWeight: 700, color: 'white',
                }}>
                  🏆 Best Trust
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <div className="status-dot completed" />
                    <span style={{ fontWeight: 700, fontSize: 15 }}>{model.display_name}</span>
                  </div>
                  <span className="badge badge-gray" style={{ fontSize: 11 }}>{model.provider}</span>
                </div>
              </div>

              {/* Score rings */}
              <div style={{ display: 'flex', justifyContent: 'center', gap: 24, marginBottom: 20 }}>
                <ScoreRing score={model.trust_score} size={80} label="Trust" />
                <ScoreRing score={model.efficiency_score} size={80} label="Efficiency" color="var(--blue-400)" />
              </div>

              {/* Claim stats */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, marginBottom: 16 }}>
                {[
                  { label: 'Supported', value: model.verified_claims || 0, color: 'var(--emerald-400)' },
                  { label: 'Contradicted', value: model.contradicted_claims || 0, color: 'var(--rose-400)' },
                  { label: 'Outdated', value: model.outdated_claims || 0, color: 'var(--amber-400)' },
                  { label: 'Unverifiable', value: model.unverifiable_claims || 0, color: 'var(--text-muted)' },
                ].map(stat => (
                  <div key={stat.label} style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: '10px 12px', textAlign: 'center' }}>
                    <div style={{ fontSize: 20, fontWeight: 800, color: stat.color }}>{stat.value}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>{stat.label}</div>
                  </div>
                ))}
              </div>

              {/* Performance metrics */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                  <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 5 }}><Clock size={12} /> Latency</span>
                  <MetricCell value={model.latency_ms} format="ms" />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                  <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 5 }}><Cpu size={12} /> Tokens</span>
                  <MetricCell value={model.total_tokens} format="tokens" />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                  <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 5 }}><DollarSign size={12} /> Est. Cost</span>
                  <MetricCell value={model.estimated_cost_usd} format="cost" />
                </div>
              </div>

              {/* Full response toggle */}
              {model.response_text && (
                <div style={{ marginTop: 16 }}>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}
                    onClick={() => setExpandedResponse(expandedResponse === model.model_id ? null : model.model_id)}
                  >
                    {expandedResponse === model.model_id ? 'Hide Response ▲' : 'View Full Response ▼'}
                  </button>
                  {expandedResponse === model.model_id && (
                    <div style={{
                      marginTop: 10, padding: 14, background: 'var(--bg-secondary)',
                      borderRadius: 8, fontSize: 13, color: 'var(--text-secondary)',
                      lineHeight: 1.7, maxHeight: 300, overflowY: 'auto',
                    }}>
                      {model.response_text}
                    </div>
                  )}
                </div>
              )}

              {model.error && (
                <div className="error-box" style={{ marginTop: 12, fontSize: 12 }}>
                  Error: {model.error}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid-2" style={{ marginBottom: 32 }}>
          {/* Trust + Efficiency bar chart */}
          <div className="chart-container">
            <h3 style={{ fontSize: 15, marginBottom: 20 }}>Trust & Efficiency Scores</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={trustChartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="Trust Score" fill="var(--blue-400)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Efficiency Score" fill="var(--purple-400)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Claim breakdown chart */}
          <div className="chart-container">
            <h3 style={{ fontSize: 15, marginBottom: 20 }}>Claim Verification Breakdown</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={claimChartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="Supported" fill="var(--emerald-400)" stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Contradicted" fill="var(--rose-400)" stackId="a" />
                <Bar dataKey="Outdated" fill="var(--amber-400)" stackId="a" />
                <Bar dataKey="Unverifiable" fill="var(--text-muted)" stackId="a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Comparison table */}
        <div className="card" style={{ marginBottom: 32 }}>
          <h3 style={{ fontSize: 16, marginBottom: 20 }}>Full Comparison Table</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Trust Score</th>
                  <th>Efficiency Score</th>
                  <th>Task Completion</th>
                  <th>Supported Claims</th>
                  <th>Contradicted</th>
                  <th>Latency</th>
                  <th>Tokens</th>
                  <th>Est. Cost</th>
                </tr>
              </thead>
              <tbody>
                {models.map(model => (
                  <tr key={model.model_id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{model.display_name}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{model.provider}</div>
                    </td>
                    <td><MetricCell value={model.trust_score} format="score" /></td>
                    <td><MetricCell value={model.efficiency_score} format="score" /></td>
                    <td>{model.task_completion_score ? `${(model.task_completion_score * 100).toFixed(0)}%` : '—'}</td>
                    <td style={{ color: 'var(--emerald-400)', fontWeight: 600 }}>{model.verified_claims ?? '—'}</td>
                    <td style={{ color: 'var(--rose-400)', fontWeight: 600 }}>{model.contradicted_claims ?? '—'}</td>
                    <td><MetricCell value={model.latency_ms} format="ms" /></td>
                    <td><MetricCell value={model.total_tokens} format="tokens" /></td>
                    <td><MetricCell value={model.estimated_cost_usd} format="cost" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Score methodology note */}
        <div style={{
          padding: '16px 20px', background: 'rgba(59,130,246,0.04)',
          border: '1px solid rgba(59,130,246,0.1)', borderRadius: 'var(--radius-md)',
          display: 'flex', gap: 12, fontSize: 13, color: 'var(--text-secondary)',
        }}>
          <Info size={16} style={{ flexShrink: 0, marginTop: 1, color: 'var(--blue-400)' }} />
          <div>
            <strong style={{ color: 'var(--text-primary)' }}>Scoring methodology:</strong>{' '}
            Trust Score = verified claim ratio × 100 − contradicted × 15 − outdated × 8 − unverifiable × 3 + task completion × 20.
            Efficiency Score = weighted average of latency (50%), tokens (30%), cost (20%). Scores are not guarantees of truth.
            {' '}<Link to={`/evaluate/${id}/report`} style={{ color: 'var(--blue-400)' }}>See full report →</Link>
          </div>
        </div>

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
          <Link to={`/evaluate/${id}/claims`} className="btn btn-secondary">
            <FileText size={16} />
            View Claim Verification
          </Link>
          <Link to={`/evaluate/${id}/report`} className="btn btn-primary">
            <Shield size={16} />
            View Trust Report
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  )
}
