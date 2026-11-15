import { Link, useLocation } from 'react-router-dom'
import { Shield, Zap, FlaskConical, Menu } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()
  
  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/evaluate', label: 'Evaluate' },
    { href: '/demo', label: 'Demo' },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <div className="navbar-logo">
            <Shield size={18} color="white" />
          </div>
          <span className="navbar-brand-name">AgentProof <span style={{ color: 'var(--blue-400)' }}>AI</span></span>
        </Link>

        <div className="navbar-nav">
          {navLinks.map(link => (
            <Link
              key={link.href}
              to={link.href}
              className="btn btn-ghost btn-sm"
              style={{
                color: location.pathname === link.href ? 'var(--blue-400)' : 'var(--text-secondary)',
              }}
            >
              {link.label}
            </Link>
          ))}
          <Link to="/evaluate" className="btn btn-primary btn-sm" style={{ marginLeft: '8px' }}>
            <Zap size={14} />
            Start Evaluating
          </Link>
        </div>
      </div>
    </nav>
  )
}
