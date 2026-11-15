import { ExternalLink, Calendar, Star } from 'lucide-react'

/**
 * SourceCard — displays a Tavily evidence source
 */
export default function SourceCard({ source, index }) {
  return (
    <div className="source-card animate-slide-in" style={{ animationDelay: `${index * 0.05}s` }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: 700,
              color: 'var(--blue-400)',
              background: 'rgba(59,130,246,0.1)',
              padding: '1px 6px',
              borderRadius: '4px',
            }}>
              [{index + 1}]
            </span>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--text-primary)',
                textDecoration: 'none',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '400px',
                display: 'block',
              }}
              onMouseOver={e => e.target.style.color = 'var(--blue-400)'}
              onMouseOut={e => e.target.style.color = 'var(--text-primary)'}
            >
              {source.title || 'Source'}
            </a>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Calendar size={10} />
              {source.published_date
                ? new Date(source.published_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                : 'Date unavailable'
              }
            </span>
            {source.relevance_score && (
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Star size={10} />
                {(source.relevance_score * 100).toFixed(0)}% relevant
              </span>
            )}
          </div>

          {source.snippet && (
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              {source.snippet.length > 200 ? source.snippet.slice(0, 200) + '…' : source.snippet}
            </p>
          )}
        </div>

        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'var(--text-muted)', flexShrink: 0 }}
        >
          <ExternalLink size={14} />
        </a>
      </div>
    </div>
  )
}
