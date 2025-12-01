import './MetricCard.css'

const MetricCard = ({ title, score, icon, details }) => {
  const getScoreColor = (score) => {
    if (score >= 85) return '#10b981' // green
    if (score >= 70) return '#3b82f6' // blue
    if (score >= 55) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const getScoreLabel = (score) => {
    if (score >= 85) return 'Excellent'
    if (score >= 70) return 'Good'
    if (score >= 55) return 'Fair'
    return 'Needs Attention'
  }

  return (
    <div className="metric-card">
      <div className="metric-header">
        <h3>{title}</h3>
      </div>

      <div className="metric-score">
        <div className="score-circle" style={{ borderColor: getScoreColor(score) }}>
          <span className="score-number" style={{ color: getScoreColor(score) }}>
            {score}
          </span>
          <span className="score-max">/100</span>
        </div>
        <div className="score-label" style={{ color: getScoreColor(score) }}>
          {getScoreLabel(score)}
        </div>
      </div>

      <div className="metric-details">
        {details.map((detail, idx) => (
          <div key={idx} className="detail-row">
            <span className="detail-label">{detail.label}:</span>
            <span className="detail-value">{detail.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default MetricCard
