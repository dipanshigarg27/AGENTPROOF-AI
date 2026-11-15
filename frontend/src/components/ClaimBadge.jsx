/**
 * ClaimBadge — colored badge for claim verification status
 */
const STATUS_CONFIG = {
  SUPPORTED: { label: 'Supported', className: 'badge-emerald' },
  CONTRADICTED: { label: 'Contradicted', className: 'badge-rose' },
  POTENTIALLY_OUTDATED: { label: 'Potentially Outdated', className: 'badge-amber' },
  UNVERIFIABLE: { label: 'Unverifiable', className: 'badge-gray' },
  OPINION: { label: 'Opinion', className: 'badge-purple' },
}

export function ClaimBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.UNVERIFIABLE
  return (
    <span className={`badge ${config.className}`}>
      {config.label}
    </span>
  )
}

export function ClaimTypeTag({ type }) {
  const labels = {
    time_sensitive_factual: { label: '⏱ Time-Sensitive', className: 'badge-orange' },
    historical_factual: { label: '📚 Historical', className: 'badge-blue' },
    general_factual: { label: '📋 General Fact', className: 'badge-teal' },
    opinion: { label: '💬 Opinion', className: 'badge-purple' },
    prediction: { label: '🔮 Prediction', className: 'badge-gray' },
  }
  const config = labels[type] || { label: type, className: 'badge-gray' }
  return <span className={`badge ${config.className}`}>{config.label}</span>
}

export default ClaimBadge
