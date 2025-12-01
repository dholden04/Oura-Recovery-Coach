import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './MetricsChart.css'

const MetricsChart = ({ sleep, readiness, activity }) => {
  const data = [
    {
      name: 'Scores',
      Sleep: sleep.sleep_score,
      Readiness: readiness.readiness_score,
      Activity: activity.activity_score
    }
  ]

  const sleepBreakdown = [
    {
      stage: 'Deep',
      hours: (sleep.deep_sleep_duration / 3600).toFixed(1),
      percentage: Math.round((sleep.deep_sleep_duration / sleep.total_sleep_duration) * 100)
    },
    {
      stage: 'REM',
      hours: (sleep.rem_sleep_duration / 3600).toFixed(1),
      percentage: Math.round((sleep.rem_sleep_duration / sleep.total_sleep_duration) * 100)
    },
    {
      stage: 'Light',
      hours: (sleep.light_sleep_duration / 3600).toFixed(1),
      percentage: Math.round((sleep.light_sleep_duration / sleep.total_sleep_duration) * 100)
    }
  ]

  return (
    <div className="metrics-chart">
      <div className="chart-section">
        <h3>Overall Scores</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="Sleep" fill="#8b5cf6" />
            <Bar dataKey="Readiness" fill="#3b82f6" />
            <Bar dataKey="Activity" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-section">
        <h3>Sleep Stage Breakdown</h3>
        <div className="sleep-stages">
          {sleepBreakdown.map((stage) => (
            <div key={stage.stage} className="stage-bar">
              <div className="stage-info">
                <span className="stage-name">{stage.stage}</span>
                <span className="stage-value">{stage.hours}h ({stage.percentage}%)</span>
              </div>
              <div className="progress-bar">
                <div
                  className={`progress-fill ${stage.stage.toLowerCase()}`}
                  style={{ width: `${stage.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default MetricsChart
