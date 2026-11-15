import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEvaluationReport, getEvaluation } from '../lib/api'
import ScoreRing from '../components/ScoreRing'
import { ClaimBadge } from '../components/ClaimBadge'
import SourceCard from '../components/SourceCard'
import {
  Shield, Zap, Trophy, AlertTriangle, CheckCircle, XCircle,
  Info, Download, Copy, ArrowLeft, FileText, ExternalLink,
} from 'lucide-react'

function MarkdownText({ text }) {
  // Simple markdown renderer for bold and bullet lists
  if (!text) return null
  const lines = text.split('\n')
  return (
    <div style={{ lineHeight: 1.75 }}>
      {lines.map((line, i) => {
        // Bold
        const rendered = line.replace(/\*\*(.*?)\*\*/g, (_, m) =>
          `<strong style="color:var(--text-primary)">${m}</strong>`
        )
        if (line.startsWith('• ') || line.startsWith('* ')) {
          return <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
            <span style={{ color: 'var(--blue-400)', flexShrink: 0 }}>•</span>
            <span dangerouslySetInnerHTML={{ __html: rendered.replace(/^[•*] /, '') }} />
          </div>
        }
        if (!line.trim()) return <div key={i} style={{ height: 8 }} />
        return <p key={i} style={{ margin: '0 0 6px' }} dangerouslySetInnerHTML={{ __html: rendered }} />
      })}
    </div>
  )
}

function ModelReportCard({ model, isBestTrust, isBestEfficiency }) {
  const [showClaims, setShowClaims] = useState(false)
  const trustColor = model.trust_score >= 70 ? 'var(--emerald-400)' : model.trust_score >= 40 ? 'var(--amber-400)' : 'var(--rose-400)'

  const strengths = []
  const weaknesses = []

  if (model.verified_claims > 0) strengths.push(`${model.verified_claims} claim(s) supported by web evidence`)
  if (model.efficiency_score >= 70) strengths.push(`High efficiency score (${model.efficiency_score?.toFixed(1)})`)
  if (model.latency_ms && model.latency_ms < 2000) strengths.push(`Fast response time (${model.latency_ms.toFixed(0)}ms)`)
  if (model.total_claims > 3) strengths.push(`Detailed response with ${model.total_claims} verifiable claims`)

  if (model.contradicted_claims > 0) weaknesses.push(`${model.contradicted_claims} claim(s) contradicted by evidence`)
  if (model.outdated_claims > 0) weaknesses.push(`${model.outdated_claims} claim(s) may be outdated`)
  if (model.unverifiable_claims > model.verified_claims) weaknesses.push(`More unverifiable than verified claims`)
  if (model.efficiency_score < 40) weaknesses.push(`Lower efficiency (latency, tokens, or cost)`)

  return (
    <div className="card" style={{ marginBottom: 20, position: 'relative' }}>
      {isBestTrust && (
        <div style={{
          position: 'absolute', top: -12, left: 20,
          background: 'var(--gradient-primary)', borderRadius: 100,
          padding: '4px 14px', fontSize: 12, fontWeight: 700, color: 'white',
          display: 'flex', alignItems: 'center', gap: 6,
        }}>
          <Trophy size={12} />
          Best Trust Score
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ display: 'flex', gap: 16 }}>
            <ScoreRing score={model.trust_score} size={72} label="Trust" />
            <ScoreRing score={model.efficiency_score} size={72} label="Efficiency" color="var(--blue-400)" />
          </div>
          <div>
            <h3 style={{ fontSize: 18, marginBottom: 4 }}>{model.display_name || model.model_id}</h3>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              <span className="badge badge-gray">{model.provider}</span>
              {isBestEfficiency && <span className="badge badge-blue">⚡ Fastest</span>}
            </div>
          </div>
        </div>

        {/* Claim summary pills */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {model.verified_claims > 0 && <span className="badge badge-emerald">✅ {model.verified_claims} supported</span>}
          {model.contradicted_claims > 0 && <span className="badge badge-rose">❌ {model.contradicted_claims} contradicted</span>}
          {model.outdated_claims > 0 && <span className="badge badge-amber">⚠️ {model.outdated_claims} outdated</span>}
          {model.unverifiable_claims > 0 && <span className="badge badge-gray">❓ {model.unverifiable_claims} unverifiable</span>}
        </div>
      </div>

      {/* Score explanations */}
      {model.trust_score_explanation && (
        <div style={{
          padding: '10px 14px', background: 'var(--bg-secondary)',
          borderRadius: 8, marginBottom: 12, fontSize: 12,
          color: 'var(--text-muted)', lineHeight: 1.6,
        }}>
          <strong style={{ color: 'var(--text-secondary)' }}>How Trust Score was calculated:</strong>{' '}
          {model.trust_score_explanation}
        </div>
      )}

      <div className="grid-2" style={{ marginBottom: 16 }}>
        {strengths.length > 0 && (
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--emerald-400)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
              Key Strengths
            </div>
            {strengths.map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6, fontSize: 13 }}>
                <CheckCircle size={14} style={{ flexShrink: 0, color: 'var(--emerald-400)', marginTop: 1 }} />
                <span style={{ color: 'var(--text-secondary)' }}>{s}</span>
              </div>
            ))}
          </div>
        )}
        {weaknesses.length > 0 && (
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--rose-400)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
              Key Weaknesses
            </div>
            {weaknesses.map((w, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6, fontSize: 13 }}>
                <XCircle size={14} style={{ flexShrink: 0, color: 'var(--rose-400)', marginTop: 1 }} />
                <span style={{ color: 'var(--text-secondary)' }}>{w}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Problematic claims */}
      {model.claims && (
        (() => {
          const badClaims = (model.claims || []).filter(c =>
            ['CONTRADICTED', 'POTENTIALLY_OUTDATED'].includes(c.verification?.status)
          )
          if (!badClaims.length) return null
          return (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--amber-400)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
                Important Unsupported / Outdated Claims
              </div>
              {badClaims.map((c, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 10, padding: '8px 12px', marginBottom: 6,
                  background: 'rgba(244,63,94,0.05)', border: '1px solid rgba(244,63,94,0.15)',
                  borderRadius: 6, fontSize: 13,
                }}>
                  <ClaimBadge status={c.verification?.status} />
                  <span style={{ color: 'var(--text-secondary)', flex: 1 }}>{c.claim_text || c.text}</span>
                </div>
              ))}
            </div>
          )
        })()
      )}

      <button
        className="btn btn-ghost btn-sm"
        style={{ fontSize: 12, color: 'var(--blue-400)' }}
        onClick={() => setShowClaims(!showClaims)}
      >
        {showClaims ? '▲ Hide' : '▼ Show'} all {model.total_claims || 0} claims with sources
      </button>

      {showClaims && model.claims && (
        <div style={{ marginTop: 12 }}>
          {model.claims.map((claim, i) => {
            const v = claim.verification || {}
            return (
              <div key={i} style={{ marginBottom: 10, padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: 8, fontSize: 13 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: v.sources?.length ? 8 : 0 }}>
                  <ClaimBadge status={v.status} />
                  <span style={{ color: 'var(--text-secondary)', flex: 1 }}>{claim.claim_text || claim.text}</span>
                </div>
                {v.sources?.slice(0, 2).map((src, si) => (
                  <SourceCard key={si} source={src} index={si} />
                ))}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default function TrustReport() {
  const { id } = useParams()
  const [report, setReport] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const [reportRes, evalRes] = await Promise.all([
          getEvaluationReport(id).catch(() => null),
          getEvaluation(id),
        ])
        setEvaluation(evalRes.data)
        if (reportRes) setReport(reportRes.data)
        else {
          // Build report from evaluation data if report endpoint fails
          const evalData = evalRes.data
          setReport({
            evaluation_id: id,
            task: evalData.task,
            task_category: evalData.task_category,
            models: evalData.models || [],
            recommendation: 'Report generation in progress. Please refresh in a moment.',
          })
        }
      } catch (e) {
        setError(e.response?.data?.detail || 'Failed to load trust report.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const exportJSON = useCallback(() => {
    const data = { report, evaluation }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `agentproof-report-${id}.json`
    a.click()
    URL.revokeObjectURL(url)
  }, [report, evaluation, id])

  const copyReport = useCallback(() => {
    if (!report) return
    const text = [
      `AgentProof AI — Trust Report`,
      `Task: ${report.task}`,
      `Category: ${report.task_category}`,
      ``,
      `Recommendation:`,
      report.recommendation,
      ``,
      ...(report.models || []).map(m =>
        `${m.display_name}: Trust ${m.trust_score?.toFixed(1) ?? 'N/A'} | Efficiency ${m.efficiency_score?.toFixed(1) ?? 'N/A'}`
      ),
    ].join('\n')
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }, [report])

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: 16 }}>
      <div className="spinner spinner-lg" />
      <div style={{ color: 'var(--text-muted)' }}>Generating Trust Report…</div>
    </div>
  )

  if (error) return (
    <div className="container" style={{ paddingTop: 40 }}>
      <div className="error-box">{error}</div>
      <Link to={`/evaluate/${id}/dashboard`} className="btn btn-secondary" style={{ marginTop: 16 }}>← Back to Dashboard</Link>
    </div>
  )

  const models = report?.models || evaluation?.models || []
  const successModels = models.filter(m => m.trust_score !== null && m.trust_score !== undefined)
  const bestTrust = successModels.reduce((best, m) => (!best || (m.trust_score ?? 0) > (best.trust_score ?? 0)) ? m : best, null)
  const bestEfficiency = successModels.reduce((best, m) => (!best || (m.efficiency_score ?? 0) > (best.efficiency_score ?? 0)) ? m : best, null)

  return (
    <div style={{ minHeight: '100vh', paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)', padding: '24px' }}>
        <div className="container">
          {evaluation?.demo_mode && (
            <div className="demo-banner">
              <AlertTriangle size={16} />
              <strong>DEMO MODE</strong> — Sample data only. No real API calls were made.
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <div style={{ width: 42, height: 42, background: 'var(--gradient-primary)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Shield size={20} color="white" />
              </div>
              <div>
                <h1 className="page-title" style={{ marginBottom: 4 }}>Trust Report</h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
                  {report?.task?.slice(0, 100)}{report?.task?.length > 100 ? '…' : ''}
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Link to={`/evaluate/${id}/claims`} className="btn btn-secondary btn-sm">
                <FileText size={14} /> Claims
              </Link>
              <button className="btn btn-secondary btn-sm" onClick={copyReport} id="copy-report-btn">
                <Copy size={14} />
                {copied ? 'Copied!' : 'Copy Report'}
              </button>
              <button className="btn btn-secondary btn-sm" onClick={exportJSON} id="export-json-btn">
                <Download size={14} />
                Export JSON
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container" style={{ paddingTop: 32 }}>
        {/* Best performer highlight */}
        {bestTrust && (
          <div style={{
            padding: '20px 24px', marginBottom: 28,
            background: 'linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(139,92,246,0.08) 100%)',
            border: '1px solid rgba(59,130,246,0.25)', borderRadius: 'var(--radius-lg)',
            display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap',
          }}>
            <div style={{ background: 'var(--gradient-primary)', borderRadius: 12, width: 52, height: 52, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Trophy size={24} color="white" />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--blue-400)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
                Best Performer for This Task
              </div>
              <div style={{ fontSize: 20, fontWeight: 800, marginBottom: 2 }}>{bestTrust.display_name}</div>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                  Trust: <strong style={{ color: 'var(--emerald-400)' }}>{bestTrust.trust_score?.toFixed(1) ?? '—'}</strong>
                </span>
                <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                  Efficiency: <strong style={{ color: 'var(--blue-400)' }}>{bestTrust.efficiency_score?.toFixed(1) ?? '—'}</strong>
                </span>
                <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
                  Verified claims: <strong style={{ color: 'var(--emerald-400)' }}>{bestTrust.verified_claims ?? 0}</strong>
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Recommendation */}
        {report?.recommendation && (
          <div className="card" style={{ marginBottom: 28 }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 16 }}>
              <div style={{ width: 36, height: 36, background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Zap size={18} color="var(--blue-400)" />
              </div>
              <div>
                <h2 style={{ fontSize: 17, marginBottom: 4 }}>Recommendation</h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Based on actual evaluation results</div>
              </div>
            </div>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.75 }}>
              <MarkdownText text={report.recommendation} />
            </div>
          </div>
        )}

        {/* Per-model report cards */}
        <div style={{ marginBottom: 28 }}>
          <h2 style={{ fontSize: 18, marginBottom: 20 }}>Model Breakdown</h2>
          {successModels.map(model => (
            <ModelReportCard
              key={model.model_id}
              model={model}
              isBestTrust={bestTrust?.model_id === model.model_id}
              isBestEfficiency={bestEfficiency?.model_id === model.model_id}
            />
          ))}
        </div>

        {/* Scoring methodology */}
        <div className="card" style={{ marginBottom: 28 }}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
            <Info size={16} style={{ flexShrink: 0, color: 'var(--blue-400)', marginTop: 2 }} />
            <div>
              <h3 style={{ fontSize: 15, marginBottom: 10 }}>Scoring Methodology (Transparent)</h3>
              {[
                {
                  title: 'Trust Score (0–100)',
                  formula: '(verified_claims / total_factual_claims × 100) − (contradicted × 15) − (outdated × 8) − (unverifiable × 3) + (task_completion × 20)',
                  note: 'Opinions and predictions excluded. Score is NOT a guarantee of truth.',
                },
                {
                  title: 'Efficiency Score (0–100)',
                  formula: 'Weighted average: latency score (50%) + token efficiency (30%) + cost efficiency (20%). Missing metrics excluded from weighting.',
                  note: '"Estimated" costs are calculated from known pricing tables, not provider-reported.',
                },
              ].map(item => (
                <div key={item.title} style={{ marginBottom: 14 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{item.title}</div>
                  <div style={{ fontSize: 12, fontFamily: 'JetBrains Mono, monospace', color: 'var(--blue-400)', background: 'var(--bg-secondary)', padding: '8px 12px', borderRadius: 6, marginBottom: 4 }}>
                    {item.formula}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.note}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to={`/evaluate/${id}/dashboard`} className="btn btn-secondary">
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-secondary" onClick={copyReport}>
              <Copy size={16} />
              {copied ? 'Copied!' : 'Copy Report'}
            </button>
            <button className="btn btn-primary" onClick={exportJSON}>
              <Download size={16} />
              Export JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
