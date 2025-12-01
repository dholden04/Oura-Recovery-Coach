import './RecommendationCard.css'

const RecommendationCard = ({ recommendation }) => {
  const getRecommendationStyle = (type) => {
    const styles = {
      rest_day: { bg: '#fee2e2', border: '#dc2626', icon: '🛌' },
      light_recovery: { bg: '#fef3c7', border: '#f59e0b', icon: '🚶' },
      moderate_activity: { bg: '#dbeafe', border: '#3b82f6', icon: '🏃' },
      training_ready: { bg: '#d1fae5', border: '#10b981', icon: '💪' },
      peak_performance: { bg: '#e0e7ff', border: '#6366f1', icon: '🚀' }
    }
    return styles[type] || styles.moderate_activity
  }

  const style = getRecommendationStyle(recommendation.recommendation_type)

  return (
    <div className="recommendation-card" style={{ backgroundColor: style.bg, borderColor: style.border }}>
      <div className="recommendation-header">
        <div className="recommendation-icon" style={{fontSize: '3rem'}}>
          {style.icon}
        </div>
        <div className="recommendation-title">
          <h2>🤖 AI Recovery Recommendation</h2>
          <div className="recommendation-type">
            {recommendation.recommendation_type.replace(/_/g, ' ').toUpperCase()}
          </div>
          <div className="confidence-badge">
            Confidence: {Math.round(recommendation.confidence * 100)}%
          </div>
        </div>
      </div>

      <div className="recommendation-message">
        {recommendation.message.split('\n\n').map((paragraph, idx) => (
          <p key={idx}>{paragraph}</p>
        ))}
      </div>

      <div className="key-factors">
        <h3>🔑 Key Factors:</h3>
        <ul>
          {recommendation.key_factors.map((factor, idx) => (
            <li key={idx}>{factor}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default RecommendationCard
