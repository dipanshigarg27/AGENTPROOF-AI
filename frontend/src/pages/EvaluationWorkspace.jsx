import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, ChevronDown, Info, AlertCircle, CheckSquare, Square, Loader2 } from 'lucide-react'
import { getModels, createEvaluation, healthCheck } from '../lib/api'

const TASK_CATEGORIES = [
  'General Knowledge',
  'Research',
  'Business',
  'Technology',
  'Science',
  'Current Events',
]

const PROVIDER_ICONS = {
  openai: '🤖',
  anthropic: '🧠',
  groq: '⚡',
}

const PROVIDER_COLORS = {
  openai: 'var(--teal-400)',
  anthropic: '#c08c5a',
  groq: 'var(--purple-400)',
}

export default function EvaluationWorkspace() {
  const navigate = useNavigate()
  const [task, setTask] = useState('')
  const [selectedModels, setSelectedModels] = useState([])
  const [category, setCategory] = useState('General Knowledge')
  const [maxTokens, setMaxTokens] = useState(1000)
  const [customInstructions, setCustomInstructions] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(false)
  const [fetchingModels, setFetchingModels] = useState(true)
  const [error, setError] = useState(null)
  const [apiStatus, setApiStatus] = useState(null)

  useEffect(() => {
    const init = async () => {
      try {
        const [healthRes, modelsRes] = await Promise.all([
          healthCheck().catch(() => null),
          getModels(),
        ])
        if (healthRes) setApiStatus(healthRes.data)
        setModels(modelsRes.data.models || [])
      } catch (e) {
        setError('Could not connect to AgentProof backend. Make sure the backend is running on port 8000.')
      } finally {
        setFetchingModels(false)
      }
    }
    init()
  }, [])

  const toggleModel = (modelId) => {
    setSelectedModels(prev =>
      prev.includes(modelId)
        ? prev.filter(id => id !== modelId)
        : prev.length < 5 ? [...prev, modelId] : prev
    )
  }

  const handleSubmit = async () => {
    if (!task.trim()) return setError('Please enter a task or question.')
    if (selectedModels.length < 2) return setError('Please select at least 2 models to compare.')
    setError(null)
    setLoading(true)

    try {
      const res = await createEvaluation({
        task: task.trim(),
        model_ids: selectedModels,
        task_category: category,
        max_tokens: maxTokens,
        custom_instructions: customInstructions.trim() || null,
      })
      navigate(`/evaluate/${res.data.evaluation_id}/progress`)
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || 'Failed to start evaluation.'
      setError(msg)
      setLoading(false)
    }
  }

  const availableModels = models.filter(m => m.available)
  const unavailableModels = models.filter(m => !m.available)

  return (
    <div style={{ minHeight: '100vh', padding: '0 0 60px' }}>
      {/* Page header */}
      <div style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)', padding: '32px 24px 24px' }}>
        <div className="container">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <div style={{ width: 36, height: 36, background: 'var(--gradient-primary)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Zap size={18} color="white" />
            </div>
            <h1 className="page-title" style={{ margin: 0 }}>Evaluation Workspace</h1>
          </div>
          <p className="page-subtitle">Enter your task, select AI models, and run a verified comparison.</p>
        </div>
      </div>

      <div className="container" style={{ paddingTop: 32 }}>
        {/* API key status */}
        {apiStatus && (
          <div style={{
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)', padding: '12px 16px',
            marginBottom: 20, display: 'flex', alignItems: 'center',
            gap: 12, flexWrap: 'wrap',
          }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600 }}>API Keys:</span>
            {Object.entries(apiStatus.api_keys || {}).map(([key, configured]) => (
              <span key={key} className={`badge ${configured ? 'badge-emerald' : 'badge-gray'}`}>
                {configured ? '✓' : '✗'} {key}
              </span>
            ))}
          </div>
        )}

        {error && (
          <div className="error-box" style={{ marginBottom: 20 }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            {error}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 24, alignItems: 'start' }}>
          {/* Left column */}
          <div>
            {/* Task input */}
            <div className="card" style={{ marginBottom: 20 }}>
              <div className="form-group">
                <label className="form-label">Your Task or Question</label>
                <textarea
                  id="task-input"
                  className="form-textarea"
                  style={{ minHeight: 160, fontSize: 15, lineHeight: 1.7 }}
                  placeholder="Enter a question or task you want AI agents to solve…&#10;&#10;Examples:&#10;• What is the current interest rate set by the US Federal Reserve?&#10;• Explain the latest developments in quantum computing.&#10;• What are the best practices for building a REST API in 2024?"
                  value={task}
                  onChange={e => setTask(e.target.value)}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{task.length} / 4000 characters</span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>All selected models receive identical text</span>
                </div>
              </div>
            </div>

            {/* Model selection */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div>
                  <h2 style={{ fontSize: 16, marginBottom: 4 }}>Select AI Models</h2>
                  <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    Select 2–5 models to compare. Only models with configured API keys are available.
                  </p>
                </div>
                <span className={`badge ${selectedModels.length >= 2 ? 'badge-emerald' : 'badge-gray'}`}>
                  {selectedModels.length} selected
                </span>
              </div>

              {fetchingModels ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: 20, color: 'var(--text-muted)' }}>
                  <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  Loading available models…
                </div>
              ) : (
                <>
                  {/* Available models */}
                  {availableModels.length > 0 && (
                    <div style={{ marginBottom: 20 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--emerald-400)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                        Available ({availableModels.length})
                      </div>
                      <div className="model-grid">
                        {availableModels.map(model => {
                          const isSelected = selectedModels.includes(model.id)
                          return (
                            <div
                              key={model.id}
                              id={`model-${model.id.replace('/', '-')}`}
                              className={`model-option ${isSelected ? 'selected' : ''}`}
                              onClick={() => toggleModel(model.id)}
                              role="checkbox"
                              aria-checked={isSelected}
                            >
                              <div style={{ marginTop: 2 }}>
                                {isSelected
                                  ? <CheckSquare size={18} color="var(--blue-400)" />
                                  : <Square size={18} color="var(--text-muted)" />
                                }
                              </div>
                              <div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                                  <span style={{ fontSize: 16 }}>{PROVIDER_ICONS[model.provider] || '🤖'}</span>
                                  <span style={{ fontWeight: 700, fontSize: 14 }}>{model.display_name}</span>
                                </div>
                                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 6 }}>
                                  {model.description}
                                </div>
                                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                                  <span className="badge badge-gray" style={{ fontSize: 10 }}>
                                    ${model.cost_per_million_input}/M in
                                  </span>
                                  <span style={{ fontSize: 11, color: PROVIDER_COLORS[model.provider], fontWeight: 600 }}>
                                    {model.provider}
                                  </span>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {/* Unavailable models */}
                  {unavailableModels.length > 0 && (
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                        Unavailable — Missing API Keys
                      </div>
                      <div className="model-grid">
                        {unavailableModels.map(model => (
                          <div key={model.id} className="model-option disabled">
                            <Square size={18} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                            <div>
                              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{model.display_name}</div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                {model.unavailable_reason}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {models.length === 0 && !fetchingModels && (
                    <div className="empty-state">
                      <AlertCircle size={32} />
                      <div>No models available. Add at least one API key to backend/.env</div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Right column — settings + run button */}
          <div>
            {/* Advanced settings */}
            <div className="card" style={{ marginBottom: 16 }}>
              <button
                className="btn btn-ghost"
                style={{ width: '100%', justifyContent: 'space-between', padding: '0 0 12px', borderBottom: showSettings ? '1px solid var(--border)' : 'none' }}
                onClick={() => setShowSettings(!showSettings)}
              >
                <span style={{ fontWeight: 700, fontSize: 15 }}>Evaluation Settings</span>
                <ChevronDown size={16} style={{ transform: showSettings ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }} />
              </button>

              <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Task Category</label>
                  <select
                    id="task-category"
                    className="form-select"
                    value={category}
                    onChange={e => setCategory(e.target.value)}
                  >
                    {TASK_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>

                {showSettings && (
                  <>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label">Max Response Length</label>
                      <select
                        id="max-tokens"
                        className="form-select"
                        value={maxTokens}
                        onChange={e => setMaxTokens(Number(e.target.value))}
                      >
                        <option value={500}>500 tokens (~375 words)</option>
                        <option value={1000}>1000 tokens (~750 words)</option>
                        <option value={2000}>2000 tokens (~1500 words)</option>
                        <option value={4000}>4000 tokens (~3000 words)</option>
                      </select>
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label">Custom Instructions (Optional)</label>
                      <textarea
                        id="custom-instructions"
                        className="form-textarea"
                        style={{ minHeight: 80 }}
                        placeholder="e.g. 'Respond concisely with citations' or 'Focus on data from 2024'"
                        value={customInstructions}
                        onChange={e => setCustomInstructions(e.target.value)}
                      />
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Validation */}
            <div className="card" style={{ marginBottom: 16 }}>
              {[
                { ok: task.trim().length >= 10, label: 'Task entered (min 10 chars)' },
                { ok: selectedModels.length >= 2, label: `2+ models selected (${selectedModels.length} selected)` },
              ].map(check => (
                <div key={check.label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, fontSize: 13 }}>
                  <div style={{
                    width: 20, height: 20, borderRadius: '50%',
                    background: check.ok ? 'rgba(16,185,129,0.15)' : 'rgba(74,90,122,0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    <span style={{ fontSize: 10, color: check.ok ? 'var(--emerald-400)' : 'var(--text-muted)' }}>
                      {check.ok ? '✓' : '○'}
                    </span>
                  </div>
                  <span style={{ color: check.ok ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                    {check.label}
                  </span>
                </div>
              ))}
            </div>

            {/* Run button */}
            <button
              id="run-evaluation-btn"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: 16, borderRadius: 'var(--radius-md)' }}
              onClick={handleSubmit}
              disabled={loading || task.trim().length < 10 || selectedModels.length < 2}
            >
              {loading ? (
                <>
                  <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                  Starting Evaluation…
                </>
              ) : (
                <>
                  <Zap size={18} />
                  Run Evaluation
                </>
              )}
            </button>

            {selectedModels.length < 2 && (
              <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', marginTop: 10 }}>
                Select at least 2 models to run the comparison.
              </p>
            )}

            {/* Info box */}
            <div style={{
              marginTop: 16, padding: '12px 14px',
              background: 'rgba(59,130,246,0.05)', border: '1px solid rgba(59,130,246,0.15)',
              borderRadius: 'var(--radius-md)', fontSize: 12, color: 'var(--text-secondary)',
              display: 'flex', gap: 8,
            }}>
              <Info size={14} style={{ flexShrink: 0, marginTop: 1, color: 'var(--blue-400)' }} />
              <span>All selected models receive the exact same task. Claims are verified against live web evidence via Tavily.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
