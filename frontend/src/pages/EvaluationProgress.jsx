import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CheckCircle, Circle, Loader2, AlertCircle, ArrowRight, XCircle } from 'lucide-react'
import { getEvaluation } from '../lib/api'

const STAGES = [
  { key: 'pending', label: 'Preparing evaluation' },
  { key: 'sending_to_models', label: 'Sending task to selected AI models', desc: 'Using Bifrost gateway to route requests concurrently' },
  { key: 'collecting_responses', label: 'Collecting model responses', desc: 'Capturing response text, latency, and token usage' },
  { key: 'extracting_claims', label: 'Extracting factual claims', desc: 'Identifying individual claims in each response' },
  { key: 'searching_evidence', label: 'Searching for current evidence', desc: 'Querying Tavily Search API for live web evidence' },
  { key: 'verifying_claims', label: 'Checking claims against evidence', desc: 'Comparing each claim to retrieved sources' },
  { key: 'calculating_scores', label: 'Calculating Trust & Efficiency scores', desc: 'Applying documented scoring formulas' },
  { key: 'generating_report', label: 'Preparing final report', desc: 'Assembling Trust Report with recommendations' },
  { key: 'completed', label: 'Evaluation complete!' },
  { key: 'failed', label: 'Evaluation failed' },
]

const STAGE_ORDER = [
  'pending', 'sending_to_models', 'collecting_responses',
  'extracting_claims', 'searching_evidence', 'verifying_claims',
  'calculating_scores', 'generating_report', 'completed',
]

function StageIcon({ status }) {
  if (status === 'completed') return <CheckCircle size={20} color="var(--emerald-400)" />
  if (status === 'active') return <Loader2 size={20} color="var(--blue-400)" style={{ animation: 'spin 1s linear infinite' }} />
  if (status === 'failed') return <XCircle size={20} color="var(--rose-400)" />
  return <Circle size={20} color="var(--text-muted)" />
}

export default function EvaluationProgress() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [evaluation, setEvaluation] = useState(null)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)

  const currentStatus = evaluation?.status || 'pending'
  const currentStageIndex = STAGE_ORDER.indexOf(currentStatus)

  useEffect(() => {
    const poll = async () => {
      try {
        const res = await getEvaluation(id)
        setEvaluation(res.data)

        if (res.data.status === 'completed' || res.data.status === 'failed') {
          clearInterval(intervalRef.current)
          if (res.data.status === 'completed') {
            setTimeout(() => navigate(`/evaluate/${id}/dashboard`), 1500)
          }
        }
      } catch (e) {
        setError(e.response?.data?.detail || 'Failed to fetch evaluation status.')
        clearInterval(intervalRef.current)
      }
    }

    poll()
    intervalRef.current = setInterval(poll, 2000) // Poll every 2s
    return () => clearInterval(intervalRef.current)
  }, [id, navigate])

  const getStageStatus = (stageKey, index) => {
    if (currentStatus === 'failed') {
      if (index < currentStageIndex) return 'completed'
      if (index === currentStageIndex) return 'failed'
      return 'pending'
    }
    if (index < currentStageIndex) return 'completed'
    if (index === currentStageIndex) return 'active'
    return 'pending'
  }

  const displayStages = STAGES.filter(s => s.key !== 'failed' || currentStatus === 'failed')
    .filter(s => s.key !== 'pending')

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 24px' }}>
      <div style={{ width: '100%', maxWidth: 640 }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>
            {currentStatus === 'completed' ? '🎉 Evaluation Complete!' :
             currentStatus === 'failed' ? '❌ Evaluation Failed' :
             'Running Evaluation…'}
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15 }}>
            {evaluation?.task
              ? `"${evaluation.task.slice(0, 80)}${evaluation.task.length > 80 ? '…' : ''}"`
              : 'Processing your task…'}
          </p>
        </div>

        {error && (
          <div className="error-box" style={{ marginBottom: 24 }}>
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Stage tracker */}
        <div className="card" style={{ marginBottom: 24 }}>
          {displayStages.map((stage, idx) => {
            const stageIndex = STAGE_ORDER.indexOf(stage.key)
            const status = getStageStatus(stage.key, stageIndex)
            return (
              <div
                key={stage.key}
                className={`progress-stage ${status}`}
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                <StageIcon status={status} />
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontWeight: 600, fontSize: 14,
                    color: status === 'active' ? 'var(--text-primary)' :
                           status === 'completed' ? 'var(--emerald-400)' :
                           status === 'failed' ? 'var(--rose-400)' : 'var(--text-muted)',
                  }}>
                    {stage.label}
                  </div>
                  {stage.desc && status === 'active' && (
                    <div style={{ fontSize: 12, color: 'var(--blue-400)', marginTop: 2 }}>
                      {stage.desc}
                    </div>
                  )}
                </div>
                {status === 'active' && (
                  <div className="badge badge-blue" style={{ fontSize: 11 }}>In Progress</div>
                )}
                {status === 'completed' && (
                  <div className="badge badge-emerald" style={{ fontSize: 11 }}>Done</div>
                )}
              </div>
            )
          })}
        </div>

        {/* Model status mini-cards */}
        {evaluation?.models && evaluation.models.length > 0 && (
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Model Status
            </div>
            {evaluation.models.map(model => (
              <div key={model.model_id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div className={`status-dot ${model.status === 'completed' ? 'completed' : model.status === 'error' ? 'failed' : 'running'}`} />
                  <span style={{ fontSize: 14, fontWeight: 500 }}>{model.display_name || model.model_id}</span>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  {model.latency_ms && (
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{model.latency_ms.toFixed(0)}ms</span>
                  )}
                  <span className={`badge ${model.status === 'completed' ? 'badge-emerald' : model.status === 'error' ? 'badge-rose' : 'badge-blue'}`} style={{ fontSize: 11 }}>
                    {model.status || 'pending'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        {currentStatus === 'completed' && (
          <button
            id="view-results-btn"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: 14, fontSize: 15 }}
            onClick={() => navigate(`/evaluate/${id}/dashboard`)}
          >
            View Comparison Dashboard
            <ArrowRight size={18} />
          </button>
        )}

        {currentStatus === 'failed' && (
          <div>
            {evaluation?.error_message && (
              <div className="error-box" style={{ marginBottom: 16 }}>
                Error: {evaluation.error_message}
              </div>
            )}
            <button
              className="btn btn-secondary"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={() => navigate('/evaluate')}
            >
              Try Again
            </button>
          </div>
        )}

        {!['completed', 'failed'].includes(currentStatus) && (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
            <Loader2 size={14} style={{ animation: 'spin 1s linear infinite', display: 'inline-block', marginRight: 6 }} />
            Polling for updates every 2 seconds…
          </div>
        )}
      </div>
    </div>
  )
}
