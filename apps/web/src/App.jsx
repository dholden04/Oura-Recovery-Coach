import { useState, useEffect } from 'react'
import { format, subDays } from 'date-fns'
import './App.css'
import MetricCard from './components/MetricCard'
import RecommendationCard from './components/RecommendationCard'
import MetricsChart from './components/MetricsChart'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [selectedDate, setSelectedDate] = useState(format(subDays(new Date(), 1), 'yyyy-MM-dd'))
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [selectedDate])

  const fetchData = async () => {
    setLoading(true)
    setError(null)

    try {
      // Fetch all data in parallel
      const [sleepRes, readinessRes, activityRes, recommendationRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/oura/sleep/${selectedDate}`),
        fetch(`${API_BASE_URL}/api/oura/readiness/${selectedDate}`),
        fetch(`${API_BASE_URL}/api/oura/activity/${selectedDate}`),
        fetch(`${API_BASE_URL}/api/recommendations/${selectedDate}`, { method: 'POST' })
      ])

      if (!sleepRes.ok || !readinessRes.ok || !activityRes.ok || !recommendationRes.ok) {
        throw new Error('Failed to fetch data')
      }

      const [sleep, readiness, activity, recommendation] = await Promise.all([
        sleepRes.json(),
        readinessRes.json(),
        activityRes.json(),
        recommendationRes.json()
      ])

      setData({ sleep, readiness, activity, recommendation })
    } catch (err) {
      setError(err.message)
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.round((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>🏃 Recovery Coach</h1>
          <p>AI-powered recovery insights from your Oura Ring</p>
        </div>
      </header>

      {/* Date Selector */}
      <div className="date-selector">
        <label htmlFor="date">Select Date:</label>
        <input
          type="date"
          id="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          max={format(new Date(), 'yyyy-MM-dd')}
        />
        <button onClick={fetchData} disabled={loading}>
          {loading ? '🔄 Loading...' : '🔍 Refresh'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ⚠️ Error: {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing your recovery data...</p>
        </div>
      )}

      {/* Dashboard Content */}
      {!loading && data && (
        <div className="dashboard">
          {/* AI Recommendation - Main Feature */}
          <RecommendationCard recommendation={data.recommendation} />

          {/* Metrics Grid */}
          <div className="metrics-grid">
            <MetricCard
              title="😴 Sleep Quality"
              score={data.sleep.sleep_score}
              icon="🛌"
              details={[
                { label: 'Total Sleep', value: formatDuration(data.sleep.total_sleep_duration) },
                { label: 'Deep Sleep', value: formatDuration(data.sleep.deep_sleep_duration) },
                { label: 'REM Sleep', value: formatDuration(data.sleep.rem_sleep_duration) },
                { label: 'Efficiency', value: `${data.sleep.sleep_efficiency}%` }
              ]}
            />

            <MetricCard
              title="💪 Readiness"
              score={data.readiness.readiness_score}
              icon="⚡"
              details={[
                { label: 'Resting HR', value: `${data.readiness.resting_heart_rate} bpm` },
                { label: 'HRV Balance', value: `${data.readiness.hrv_balance}/100` },
                { label: 'Recovery Index', value: `${data.readiness.recovery_index}/100` },
                { label: 'Temp Deviation', value: `${data.readiness.temperature_deviation}°C` }
              ]}
            />

            <MetricCard
              title="🏃 Activity"
              score={data.activity.activity_score}
              icon="🔥"
              details={[
                { label: 'Steps', value: data.activity.steps.toLocaleString() },
                { label: 'Total Calories', value: `${data.activity.total_calories} kcal` },
                { label: 'Active Calories', value: `${data.activity.active_calories} kcal` },
                { label: 'Training Volume', value: `${data.activity.training_volume} min` }
              ]}
            />
          </div>

          {/* Charts Section */}
          <div className="charts-section">
            <h2>📊 Daily Metrics Overview</h2>
            <MetricsChart
              sleep={data.sleep}
              readiness={data.readiness}
              activity={data.activity}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>Powered by Oura Ring API & Claude AI</p>
        <p className="footer-tech">Built with React + FastAPI</p>
      </footer>
    </div>
  )
}

export default App
