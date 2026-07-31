import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api';
import { authService } from '../auth';
import './BottleneckInsights.css';

function BottleneckInsights() {
  const [bottleneckData, setBottleneckData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBottleneckData();
  }, []);

  const loadBottleneckData = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/bottlenecks/analysis`, {
        headers: authService.getAuthHeader()
      });
      if (res.ok) {
        const data = await res.json();
        setBottleneckData(data);
      } else {
        setError('Failed to load bottleneck data');
      }
    } catch (err) {
      setError('Error loading bottleneck data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bottleneck-insights loading">
        <div className="spinner"></div>
        <p>Analyzing bottlenecks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bottleneck-insights error">
        <p>{error}</p>
        <button onClick={loadBottleneckData}>Retry</button>
      </div>
    );
  }

  if (!bottleneckData) {
    return null;
  }

  const { bottlenecks, department_delays, risk_employees, root_causes, summary } = bottleneckData;

  if (summary.total_employees === 0) {
    return (
      <div className="bottleneck-insights error">
        <p>Upload an employee dataset to generate bottleneck analysis.</p>
      </div>
    );
  }

  return (
    <div className=" bottleneck-insights">
      <div className="bottleneck-header">
        <h2>Bottleneck Analysis</h2>
        <button className="refresh-btn" onClick={loadBottleneckData}>
          Refresh Analysis
        </button>
      </div>

      {/* Top Bottlenecks Ranking */}
      <div className="bottleneck-section">
        <h3>⚠️ Current Bottlenecks</h3>
        <div className="bottleneck-ranking">
          {bottlenecks.map((bottleneck, idx) => (
            <div key={idx} className={`bottleneck-card rank-${bottleneck.rank}`}>
              <div className="bottleneck-rank">#{bottleneck.rank}</div>
              <div className="bottleneck-info">
                <h4>{bottleneck.stage_name}</h4>
                <div className="bottleneck-metrics">
                  <div className="metric">
                    <span className="metric-label">Average Delay:</span>
                    <span className="metric-value delay">{bottleneck.average_delay} days</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Expected:</span>
                    <span className="metric-value expected">{bottleneck.expected_time} days</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Affected:</span>
                    <span className="metric-value affected">{bottleneck.affected_employees} employees</span>
                  </div>
                </div>
                <div className="bottleneck-trend">
                  {bottleneck.trend === 'up' && (
                    <span className="trend up">↑ {bottleneck.trend_percentage}% worse than last month</span>
                  )}
                  {bottleneck.trend === 'down' && (
                    <span className="trend down">↓ {bottleneck.trend_percentage}% better than last month</span>
                  )}
                  {bottleneck.trend === 'stable' && (
                    <span className="trend stable">→ Stable compared to last month</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Department Delay Heatmap */}
      <div className="bottleneck-section">
        <h3>📊 Department Delay Analysis</h3>
        <div className="department-heatmap">
          {Object.entries(department_delays).map(([dept, data]) => (
            <div key={dept} className="department-bar">
              <div className="dept-label">{dept}</div>
              <div className="dept-bar-container">
                <div 
                  className="dept-bar-fill" 
                  style={{ 
                    width: `${Math.min((data.average_delay / 20) * 100, 100)}%`,
                    backgroundColor: getDelayColor(data.average_delay)
                  }}
                />
              </div>
              <div className="dept-metrics">
                <span className="avg-delay">{data.average_delay} days</span>
                <span className="completion-rate">{data.completion_rate}% complete</span>
                <span className="emp-count">({data.employee_count} employees)</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Root Cause Summary */}
      <div className="bottleneck-section">
        <h3>🔍 Root Cause Analysis</h3>
        <div className="root-causes">
          <div className="root-cause-summary">
            <div className="summary-stat">
              <span className="stat-value">{root_causes.total_delayed_employees}</span>
              <span className="stat-label">Employees Delayed</span>
            </div>
          </div>
          
          {Object.keys(root_causes.delay_reasons).length > 0 && (
            <div className="delay-reasons">
              <h4>Delay Reasons</h4>
              {Object.entries(root_causes.delay_reasons).map(([reason, percentage]) => (
                <div key={reason} className="reason-bar">
                  <span className="reason-label">{reason}</span>
                  <div className="reason-bar-container">
                    <div 
                      className="reason-bar-fill" 
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="reason-percentage">{percentage}%</span>
                </div>
              ))}
            </div>
          )}

          {Object.keys(root_causes.ticket_impact).length > 0 && (
            <div className="ticket-impact">
              <h4>Ticket Impact by Stage</h4>
              {Object.entries(root_causes.ticket_impact).map(([stage, count]) => (
                <div key={stage} className="impact-item">
                  <span className="impact-stage">{stage}</span>
                  <span className="impact-count">{count} tickets</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Risk Prediction */}
      <div className="bottleneck-section">
        <h3>⚡ Risk Prediction</h3>
        <div className="risk-prediction">
          <div className="risk-summary">
            <div className="risk-alert">
              <span className="risk-count">{risk_employees.length}</span>
              <span className="risk-label">Employees likely to exceed 30-day onboarding</span>
            </div>
          </div>
          
          {risk_employees.length > 0 && (
            <div className="risk-employees-list">
              <h4>At-Risk Employees</h4>
              <table className="risk-table">
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Department</th>
                    <th>Days Since Joining</th>
                    <th>Missing Stages</th>
                    <th>Risk Score</th>
                    <th>Est. Completion</th>
                  </tr>
                </thead>
                <tbody>
                  {risk_employees.slice(0, 10).map((emp, idx) => (
                    <tr key={idx}>
                      <td>{emp.employee_name}</td>
                      <td>{emp.department}</td>
                      <td>{emp.days_since_joining} days</td>
                      <td>
                        {emp.missing_stages.length > 0 ? (
                          emp.missing_stages.map((stage, i) => (
                            <span key={i} className="missing-stage">{stage}</span>
                          ))
                        ) : (
                          <span className="none">None</span>
                        )}
                      </td>
                      <td>
                        <span className={`risk-score ${getRiskLevel(emp.risk_score)}`}>
                          {emp.risk_score}
                        </span>
                      </td>
                      <td>{emp.estimated_completion_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getDelayColor(delay) {
  if (delay < 3) return '#4caf50';
  if (delay < 6) return '#ff9800';
  if (delay < 10) return '#f44336';
  return '#b71c1c';
}

function getRiskLevel(score) {
  if (score < 2) return 'low';
  if (score < 4) return 'medium';
  return 'high';
}

export default BottleneckInsights;
