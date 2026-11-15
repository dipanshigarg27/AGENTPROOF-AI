import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEvaluation } from '../lib/api'
import { ClaimBadge, ClaimTypeTag } from '../components/ClaimBadge'
import SourceCard from '../components/SourceCard'
import {
  ChevronDown, ChevronRight, AlertTriangle, Shield,
  Search, Info, ArrowRight, ExternalLink,
} from 'lucide-react'

const STATUS_ICONS = {
  SUPPORTED: '✅',
  CONTRADICTED: '❌',
  POTENTIALLY_OUTDATED: '⚠️',
  UNVERIFIABLE: '❓',
  OPINION: '💬',
}

function ClaimRow({ claim, index }) {
  const [expanded, setExpanded] = useState(false)
  const v = claim.verification || {}
  const statusKey = (v.status || 'UNVERIFIABLE').toLowerCase().replace('_', '-')

  return (
    <div className={`claim-card ${statusKey}`} id={`claim-${claim.id || index}`}>
      <div
        style={{ display: 'flex', alignItems: 'flex-start', gap: 12, cursor: 'pointer' }}
        onClick={() => setExpanded(!expanded)}
      >
        <span style={{ fontSize: 18, flexShrink: 0 }}>{STATUS_ICONS[v.status] || '❓'}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10, marginBottom: 6 }}>
            <p style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary)', margin: 0, lineHeight: 1.5 }}>
              {claim.claim_text || claim.text}
            </p>
            <div style={{ display: 'flex', gap: 6, flexShrink: 0, flexWrap: 'wrap' }}>
              <ClaimBadge status={v.status || 'UNVERIFIABLE'} />
              <ClaimTypeTag type={claim.claim_type || claim.type} />
            </div>
          </div>

          {v.explanation && (
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
              {v.explanation}
            </p>
          )}
        </div>
        <div style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-subtle)' }}>
          {v.evidence_summary && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
                Evidence Summary
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                {v.evidence_summary}
              </p>
            </div>
          )}

          {v.sources && v.sources.length > 0 && (
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
                Sources ({v.sources.length})
              </div>
              {v.sources.map((src, i) => (
                <SourceCard key={i} source={src} index={i} />
              ))}
            </div>
          )}

          {(!v.sources || v.sources.length === 0) && v.status !== 'OPINION' && (
            <div style={{ fontSize: 13, color: 'var(--text-muted)', fontStyle: 'italic' }}>
              No web sources retrieved for this claim.
            </div>
          )}

          {v.retrieved_at && (
            <div style={{ marginTop: 10, fontSize: 11, color: 'var(--text-muted)' }}>
              Evidence retrieved: {new Date(v.retrieved_at).toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function ModelClaimsPanel({ model, colorIndex }) {
  const claims = model.claims || []
  const MODEL_COLORS = ['var(--blue-400)', 'var(--purple-400)', 'var(--teal-400)', 'var(--amber-400)', 'var(--rose-400)']
  const color = MODEL_COLORS[colorIndex % MODEL_COLORS.length]

  const statusCounts = claims.reduce((acc, c) => {
    const s = c.verification?.status || 'UNVERIFIABLE'
    acc[s] = (acc[s] || 0) + 1
    return acc
  }, {})

  return (
    <div className="card" style={{ marginBottom: 24 }}>
      {/* Model header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
          <div>
            <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 2 }}>{model.display_name || model.model_id}</h3>
            <span className="badge badge-gray" style={{ fontSize: 11 }}>{model.provider}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {statusCounts.SUPPORTED > 0 && <span className="badge badge-emerald">✅ {statusCounts.SUPPORTED} supported</span>}
          {statusCounts.CONTRADICTED > 0 && <span className="badge badge-rose">❌ {statusCounts.CONTRADICTED} contradicted</span>}
          {statusCounts.POTENTIALLY_OUTDATED > 0 && <span className="badge badge-amber">⚠️ {statusCounts.POTENTIALLY_OUTDATED} outdated</span>}
          {statusCounts.UNVERIFIABLE > 0 && <span className="badge badge-gray">❓ {statusCounts.UNVERIFIABLE} unverifiable</span>}
          {statusCounts.OPINION > 0 && <span className="badge badge-purple">💬 {statusCounts.OPINION} opinion</span>}
        </div>
      </div>

      {claims.length === 0 ? (
        <div className="empty-state" style={{ padding: '24px' }}>
          <Search size={24} />
          <div>No claims extracted for this model</div>
        </div>
      ) : (
        claims.map((claim, i) => (
          <ClaimRow key={claim.id || i} claim={claim} index={i} />
        ))
      )}
    </div>
  )
}

export default function ClaimVerificationReport() {
  const { id } = useParams()
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getEvaluation(id)
        setEvaluation(res.data)
      } catch (e) {
        setError(e.response?.data?.detail || 'Failed to load claims.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: 16 }}>
      <div className="spinner spinner-lg" />
      <div style={{ color: 'var(--text-muted)' }}>Loading claim verification report…</div>
    </div>
  )

  if (error) return <div className="container" style={{ paddingTop: 40 }}><div className="error-box">{error}</div></div>

  const models = (evaluation?.models || []).filter(m => m.response_text || (m.claims && m.claims.length > 0))

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
            <div>
              <h1 className="page-title">Claim Verification Report</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
                {evaluation?.task?.slice(0, 100)}{evaluation?.task?.length > 100 ? '…' : ''}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Link to={`/evaluate/${id}/dashboard`} className="btn btn-secondary btn-sm">← Dashboard</Link>
              <Link to={`/evaluate/${id}/report`} className="btn btn-primary btn-sm">
                <Shield size={14} />
                Trust Report
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container" style={{ paddingTop: 32 }}>
        {/* Verification legend */}
        <div style={{
          display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24,
          padding: '14px 18px', background: 'var(--bg-card)',
          border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
        }}>
          <span style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600, marginRight: 4 }}>Legend:</span>
          {[
            { status: 'SUPPORTED', label: 'Evidence supports claim', color: 'badge-emerald' },
            { status: 'CONTRADICTED', label: 'Evidence conflicts', color: 'badge-rose' },
            { status: 'POTENTIALLY_OUTDATED', label: 'May be outdated', color: 'badge-amber' },
            { status: 'UNVERIFIABLE', label: 'Insufficient evidence', color: 'badge-gray' },
            { status: 'OPINION', label: 'Subjective — not scored', color: 'badge-purple' },
          ].map(item => (
            <span key={item.status} className={`badge ${item.color}`} style={{ fontSize: 12 }}>
              {STATUS_ICONS[item.status]} {item.label}
            </span>
          ))}
        </div>

        {/* Important disclaimer */}
        <div style={{
          display: 'flex', gap: 10, padding: '12px 16px', marginBottom: 24,
          background: 'rgba(251,191,36,0.05)', border: '1px solid rgba(251,191,36,0.2)',
          borderRadius: 'var(--radius-md)', fontSize: 13, color: 'var(--text-secondary)',
        }}>
          <Info size={15} style={{ flexShrink: 0, color: 'var(--amber-400)', marginTop: 1 }} />
          <div>
            <strong style={{ color: 'var(--amber-400)' }}>Verification limitations:</strong>{' '}
            Claim verification uses live web evidence from Tavily Search. We distinguish evidence that{' '}
            <em>supports</em> a claim from evidence that merely <em>mentions</em> the same topic.
            Verdicts are based on available evidence at the time of evaluation and are not guarantees of truth.
            Not all hallucinations can be detected automatically.
          </div>
        </div>

        {models.length === 0 ? (
          <div className="empty-state">
            <Search size={40} />
            <div>No claim verification data available yet.</div>
          </div>
        ) : (
          models.map((model, i) => (
            <ModelClaimsPanel key={model.model_id} model={model} colorIndex={i} />
          ))
        )}
      </div>
    </div>
  )
}
