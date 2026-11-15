/**
 * ScoreRing — SVG circular progress ring for Trust/Efficiency scores
 */
export default function ScoreRing({ score, size = 80, strokeWidth = 8, label, color }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  const getColor = () => {
    if (color) return color
    if (score >= 70) return 'var(--emerald-400)'
    if (score >= 40) return 'var(--amber-400)'
    return 'var(--rose-400)'
  }

  const scoreColor = getColor()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--border)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={scoreColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
        }}>
          <span style={{ fontSize: size > 70 ? '18px' : '14px', fontWeight: 800, color: scoreColor, lineHeight: 1 }}>
            {score !== null && score !== undefined ? Math.round(score) : '—'}
          </span>
        </div>
      </div>
      {label && (
        <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', textAlign: 'center' }}>
          {label}
        </span>
      )}
    </div>
  )
}
