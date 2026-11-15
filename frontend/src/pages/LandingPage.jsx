import { Link } from 'react-router-dom'
import {
  Shield, Zap, Search, BarChart2, CheckCircle, AlertTriangle,
  ArrowRight, Globe, Cpu, TrendingUp, Award, ChevronRight,
} from 'lucide-react'

const BenefitCard = ({ icon: Icon, title, desc, color }) => (
  <div className="card" style={{ animationDelay: '0.1s' }}>
    <div style={{
      width: 48, height: 48, borderRadius: 12,
      background: `${color}20`, border: `1px solid ${color}40`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      marginBottom: 16,
    }}>
      <Icon size={22} color={color} />
    </div>
    <h3 style={{ fontSize: 18, marginBottom: 8 }}>{title}</h3>
    <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7 }}>{desc}</p>
  </div>
)

const StepCard = ({ step, title, desc, icon: Icon }) => (
  <div style={{ display: 'flex', gap: 20, marginBottom: 32 }}>
    <div style={{ flexShrink: 0 }}>
      <div style={{
        width: 48, height: 48, borderRadius: 12,
        background: 'var(--gradient-primary)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 18, fontWeight: 800, color: 'white',
      }}>
        {step}
      </div>
    </div>
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <Icon size={16} color="var(--blue-400)" />
        <h3 style={{ fontSize: 18 }}>{title}</h3>
      </div>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7 }}>{desc}</p>
    </div>
  </div>
)

const IntegrationCard = ({ logo, name, tagline, details, color }) => (
  <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      <div style={{
        width: 52, height: 52, borderRadius: 14,
        background: `${color}18`, border: `1px solid ${color}30`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 24, fontWeight: 900,
      }}>
        {logo}
      </div>
      <div>
        <div style={{ fontSize: 18, fontWeight: 700 }}>{name}</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{tagline}</div>
      </div>
    </div>
    <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7, margin: 0 }}>{details}</p>
  </div>
)

export default function LandingPage() {
  return (
    <div>
      {/* Hero Section */}
      <section style={{
        background: 'var(--gradient-hero)',
        padding: '100px 24px 80px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background glow */}
        <div style={{
          position: 'absolute', top: '20%', left: '50%',
          transform: 'translateX(-50%)',
          width: '600px', height: '300px',
          background: 'radial-gradient(ellipse, rgba(59,130,246,0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          {/* Tag */}
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
            <div className="badge badge-blue" style={{ fontSize: 13, padding: '5px 14px', gap: 6 }}>
              <Shield size={13} />
              Bifrost PS02 · Tavily PS06
            </div>
          </div>

          <h1 style={{
            fontSize: 'clamp(36px, 6vw, 64px)',
            fontWeight: 900,
            letterSpacing: '-0.03em',
            marginBottom: 20,
            lineHeight: 1.1,
          }}>
            Know Which AI Agent{' '}
            <span className="gradient-text">Deserves Your Trust.</span>
          </h1>

          <p style={{
            fontSize: 'clamp(16px, 2vw, 20px)',
            color: 'var(--text-secondary)',
            maxWidth: 640,
            margin: '0 auto 40px',
            lineHeight: 1.7,
          }}>
            Compare AI agents on the same task. Verify their answers with live web evidence.
            Choose with confidence.
          </p>

          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/evaluate" className="btn btn-primary btn-lg" id="cta-start-evaluating">
              <Zap size={18} />
              Start Evaluating
            </Link>
            <Link to="/demo" className="btn btn-secondary btn-lg" id="cta-explore-demo">
              <Search size={18} />
              Explore Demo
            </Link>
          </div>

          {/* Stats strip */}
          <div style={{
            display: 'flex', justifyContent: 'center', gap: 48,
            marginTop: 64, flexWrap: 'wrap',
          }}>
            {[
              { value: '9+', label: 'AI Models' },
              { value: '7', label: 'Eval Stages' },
              { value: '5', label: 'Claim Types' },
              { value: 'Live', label: 'Web Evidence' },
            ].map(stat => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 28, fontWeight: 800, color: 'var(--blue-400)' }}>{stat.value}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section style={{ padding: '80px 24px' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 style={{ fontSize: 'clamp(24px, 4vw, 36px)', marginBottom: 12 }}>
              Everything You Need to <span className="gradient-text">Trust AI Answers</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 16, maxWidth: 560, margin: '0 auto' }}>
              Run the same task across multiple AI agents, verify claims with live evidence, and get an explainable score.
            </p>
          </div>

          <div className="grid-3">
            <BenefitCard
              icon={Cpu}
              color="var(--blue-400)"
              title="Compare AI Agents"
              desc="Send any question to multiple AI models simultaneously via Bifrost. Get real responses with real metrics — latency, tokens, and cost."
            />
            <BenefitCard
              icon={Globe}
              color="var(--teal-400)"
              title="Verify with Live Evidence"
              desc="Every factual claim is checked against current web sources via Tavily. See which claims are supported, contradicted, or outdated."
            />
            <BenefitCard
              icon={TrendingUp}
              color="var(--purple-400)"
              title="Understand Trust & Cost"
              desc="Transparent scoring formulas calculate Trust and Efficiency scores. Never just take speed or cost as the winning metric."
            />
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section style={{ padding: '80px 24px', background: 'var(--bg-secondary)' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
            <div>
              <div className="badge badge-blue" style={{ marginBottom: 20 }}>How It Works</div>
              <h2 style={{ fontSize: 'clamp(24px, 4vw, 36px)', marginBottom: 32, lineHeight: 1.2 }}>
                Three Steps from Question to <span className="gradient-text">Verified Answer</span>
              </h2>
              <StepCard step="1" icon={Zap} title="Run"
                desc="Enter your question and select two or more AI models. All models receive the exact same task via the Bifrost gateway."
              />
              <StepCard step="2" icon={Search} title="Verify"
                desc="AgentProof extracts factual claims from each response and searches for current web evidence using Tavily."
              />
              <StepCard step="3" icon={Award} title="Compare"
                desc="See Trust and Efficiency scores for each model. Get an explainable recommendation based on actual verification results."
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Mini preview cards */}
              {[
                { label: 'GPT-4o Mini', trust: 72, eff: 88, status: 'completed', color: 'var(--blue-400)' },
                { label: 'Claude 3.5 Haiku', trust: 85, eff: 61, status: 'completed', color: 'var(--purple-400)' },
              ].map(model => (
                <div key={model.label} className="card" style={{ padding: '20px 24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <div className="status-dot completed" />
                        <span style={{ fontWeight: 700, fontSize: 15 }}>{model.label}</span>
                      </div>
                      <div style={{ display: 'flex', gap: 24 }}>
                        <div>
                          <div style={{ fontSize: 24, fontWeight: 800, color: model.trust >= 70 ? 'var(--emerald-400)' : 'var(--amber-400)' }}>
                            {model.trust}
                          </div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Trust Score</div>
                        </div>
                        <div>
                          <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--blue-400)' }}>
                            {model.eff}
                          </div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Efficiency</div>
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', maxWidth: 160 }}>
                      <span className="badge badge-emerald">3 Supported</span>
                      <span className="badge badge-amber">1 Outdated</span>
                    </div>
                  </div>
                </div>
              ))}
              <div style={{
                textAlign: 'center', padding: '12px', background: 'rgba(59,130,246,0.05)',
                border: '1px solid rgba(59,130,246,0.15)', borderRadius: 'var(--radius-md)',
                fontSize: 13, color: 'var(--blue-400)',
              }}>
                Sample illustration — real scores come from your evaluation
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section style={{ padding: '80px 24px' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 style={{ fontSize: 'clamp(24px, 4vw, 36px)', marginBottom: 12 }}>
              Powered by <span className="gradient-text">Real Integrations</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 16, maxWidth: 560, margin: '0 auto' }}>
              Both integrations are live and verifiable. No mock data in live mode.
            </p>
          </div>

          <div className="grid-2">
            <IntegrationCard
              logo="⚡"
              name="Bifrost AI Gateway"
              tagline="PS02 · AI Agent Benchmarking"
              color="var(--blue-400)"
              details="Bifrost provides a single OpenAI-compatible endpoint routing requests to 20+ AI providers. We use it to send the same task to multiple models simultaneously and capture real performance metrics including latency, token usage, and finish reason."
            />
            <IntegrationCard
              logo="🔍"
              name="Tavily Search API"
              tagline="PS06 · Stale Answer Detector"
              color="var(--teal-400)"
              details="Tavily provides LLM-optimized web search specifically designed for AI fact-checking. We use it to retrieve current evidence for every factual claim, then use an LLM to compare the claim against evidence for SUPPORTED / CONTRADICTED / OUTDATED / UNVERIFIABLE verdicts."
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '80px 24px', textAlign: 'center', background: 'var(--bg-secondary)' }}>
        <div className="container">
          <h2 style={{ fontSize: 'clamp(24px, 4vw, 36px)', marginBottom: 16 }}>
            Ready to Find Out Which AI <span className="gradient-text">You Can Trust?</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 16, marginBottom: 36 }}>
            Run your first evaluation in under a minute.
          </p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center' }}>
            <Link to="/evaluate" className="btn btn-primary btn-lg" id="cta-bottom-start">
              <Zap size={18} />
              Start Evaluating
              <ArrowRight size={16} />
            </Link>
            <Link to="/demo" className="btn btn-secondary btn-lg">
              View Demo First
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '24px', textAlign: 'center', borderTop: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: 13 }}>
        AgentProof AI · Built with Bifrost + Tavily · Hackathon Prototype
      </footer>
    </div>
  )
}
