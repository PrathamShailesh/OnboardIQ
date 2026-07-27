import React from 'react';

function BottleneckAlert({ stageDelays }) {
  if (!stageDelays || Object.keys(stageDelays).length === 0) {
    return null;
  }

  const topBottleneck = Object.values(stageDelays).sort((a, b) => b.average_delay - a.average_delay)[0];
  
  if (!topBottleneck) return null;

  return (
    <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
      <div className="panel-header">
        <h3>⚠️ Top Bottleneck Alert</h3>
        <span className="badge">Critical</span>
      </div>
      <div className="bottleneck-alert-card">
        <div className="alert-header">
          <h4>{topBottleneck.stage_name}</h4>
          <span className="delay-badge">{topBottleneck.average_delay} days delay</span>
        </div>
        <div className="alert-details">
          <p>Expected: {topBottleneck.expected_time} days</p>
          <p>Affected: {topBottleneck.affected_employees} employees</p>
          <p>Completion: {topBottleneck.completion_rate}%</p>
        </div>
      </div>
    </div>
  );
}

export default BottleneckAlert;
