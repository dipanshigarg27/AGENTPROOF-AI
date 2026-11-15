import { Link, useNavigate } from 'react-router-dom'
import { AlertTriangle, ArrowRight, Zap, Shield, FileText, Info } from 'lucide-react'

export default function DemoPage() {
  const DEMO_ID = 'demo'

  return (
    <div style={{ minHeight: '100vh', paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)', padding: '32px 24px 24px' }}>
        <div className="container">
          <div className="demo-banner" style={{ marginBottom: 20 }}>
            <AlertTriangle size={18} />
            <div>
              <strong>DEMO MODE</strong> — All data on these pages is pre-prepared sample data.
              No real Bifrost or Tavily API calls were made. Live evaluation mode remains available from the Evaluate page.
            </div>
          </div>
          <h1 className="page-title">Demo Evaluation</h1>
          <p className="page-subtitle">
            Explore a sample evaluation comparing GPT-4o Mini vs Claude 3.5 Haiku on a Fed interest rate question.
          </p>
        </div>
      </div>

      <div className="container" style={{ paddingTop: 32 }}>
        {/* Demo scenario description */}
        <div className="card" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
            <div style={{ width: 42, height: 42, background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.3)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Info size={20} color="#fbbf24" />
            </div>
            <div>
              <h2 style={{ fontSize: 17, marginBottom: 8 }}>Sample Scenario</h2>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, margin: 0 }}>
                <strong style={{ color: 'var(--text-primary)' }}>Task:</strong> "What is the current interest rate set by the US Federal Reserve, and how has it changed over the past year?"
              </p>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, margin: '10px 0 0' }}>
                This demo illustrates the key AgentProof insight: <strong style={{ color: 'var(--amber-400)' }}>GPT-4o Mini responded faster and cost less, but had 1 contradicted claim and 1 potentially outdated claim</strong> (Trust Score: 72.5).{' '}
                <strong style={{ color: 'var(--emerald-400)' }}>Claude 3.5 Haiku was slower and more expensive, but had stronger evidence support with only 1 unverifiable claim</strong> (Trust Score: 85.2).
              </p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 10 }}>
                ⚠️ This is pre-prepared sample data for demonstration purposes. Trust scores were computed manually from sample evidence to illustrate the product concept.
              </p>
            </div>
          </div>
        </div>

        {/* Navigation cards */}
        <div className="grid-3" style={{ marginBottom: 32 }}>
          {[
            {
              icon: Zap,
              title: 'Comparison Dashboard',
              desc: 'Side-by-side scores, charts, and performance metrics for both models.',
              href: `/evaluate/${DEMO_ID}/dashboard`,
              color: 'var(--blue-400)',
              id: 'demo-dashboard-link',
            },
            {
              icon: FileText,
              title: 'Claim Verification',
              desc: 'Detailed breakdown of every factual claim and its supporting/contradicting evidence.',
              href: `/evaluate/${DEMO_ID}/claims`,
              color: 'var(--teal-400)',
              id: 'demo-claims-link',
            },
            {
              icon: Shield,
              title: 'Trust Report',
              desc: 'Full explainable report with recommendation and per-model scoring breakdown.',
              href: `/evaluate/${DEMO_ID}/report`,
              color: 'var(--purple-400)',
              id: 'demo-report-link',
            },
          ].map(card => (
            <Link key={card.href} to={card.href} id={card.id} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ height: '100%', cursor: 'pointer' }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 10,
                  background: `${card.color}18`, border: `1px solid ${card.color}30`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  marginBottom: 14,
                }}>
                  <card.icon size={20} color={card.color} />
                </div>
                <h3 style={{ fontSize: 15, marginBottom: 8 }}>{card.title}</h3>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>{card.desc}</p>
                <div style={{ marginTop: 14, color: card.color, fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
                  View Demo <ArrowRight size={14} />
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* CTA to live mode */}
        <div style={{
          padding: '24px 28px', background: 'linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(139,92,246,0.06) 100%)',
          border: '1px solid rgba(59,130,246,0.2)', borderRadius: 'var(--radius-lg)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16,
        }}>
          <div>
            <h3 style={{ fontSize: 17, marginBottom: 4 }}>Ready to run a real evaluation?</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14, margin: 0 }}>
              Add your API keys to backend/.env and run a live comparison with real Bifrost + Tavily calls.
            </p>
          </div>
          <Link to="/evaluate" className="btn btn-primary" id="go-to-live-eval">
            <Zap size={16} />
            Start Live Evaluation
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  )
}
