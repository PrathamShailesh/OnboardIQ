import React, { useState } from 'react';
import Sidebar from './Sidebar';
import './DashboardShell.css';

function DashboardShell() {
  const [activeTab, setActiveTab] = useState('overview');

  // Let's create mockup statistics aligned with OnboardIQ overview requirements
  const stats = [
    {
      title: 'Active Onboardees',
      value: '142',
      change: '+12% this week',
      isPositive: true,
      color: 'var(--accent-primary)',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      )
    },
    {
      title: 'Avg. Onboarding Speed',
      value: '22.4 Days',
      change: '-3.2 days vs last month',
      isPositive: true,
      color: 'var(--accent-secondary)',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      )
    },
    {
      title: 'Tool Adoption Rate',
      value: '84.8%',
      change: '+4.5% vs average',
      isPositive: true,
      color: 'hsl(142, 70%, 50%)',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      )
    },
    {
      title: 'Open IT Support Tickets',
      value: '18',
      change: '+3 new today',
      isPositive: false,
      color: 'hsl(346, 80%, 60%)',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      )
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="tab-content animate-fade-in">
            <div className="welcome-banner glass-panel">
              <div className="welcome-text">
                <h1>Welcome to <span className="gradient-text">OnboardIQ</span></h1>
                <p>Track employee onboarding milestones, IT equipment ticketing, and software license adoption in one unified analytics pane.</p>
              </div>
              <div className="welcome-action">
                <button className="primary-btn">
                  <span>Generate Report</span>
                  <svg className="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="8 17 12 21 16 17" />
                    <line x1="12" y1="12" x2="12" y2="21" />
                    <path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="stats-grid">
              {stats.map((stat, idx) => (
                <div key={idx} className="stat-card glass-panel">
                  <div className="stat-header">
                    <span className="stat-title">{stat.title}</span>
                    <div className="stat-icon-wrapper" style={{ color: stat.color, backgroundColor: `${stat.color}15` }}>
                      {stat.icon}
                    </div>
                  </div>
                  <div className="stat-value">{stat.value}</div>
                  <div className="stat-footer">
                    <span className={`stat-change ${stat.isPositive ? 'positive' : 'negative'}`}>
                      {stat.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="content-layout">
              <div className="data-panel main-panel glass-panel">
                <div className="panel-header">
                  <h3>Onboarding Bottlenecks & Progress</h3>
                  <span className="badge">Realtime</span>
                </div>
                <div className="placeholder-viz">
                  <div className="pulse-circle" />
                  <p className="placeholder-text">Visualization engine is ready. Connect the FastAPI backend to visualize live onboarding data.</p>
                </div>
              </div>
              <div className="data-panel side-panel glass-panel">
                <div className="panel-header">
                  <h3>Recent Cohorts</h3>
                </div>
                <div className="cohorts-list">
                  <div className="cohort-item">
                    <div className="cohort-avatar font-eng">ENG</div>
                    <div className="cohort-details">
                      <h4>Engineering Cohort Q3</h4>
                      <p>12 members • 84% avg completion</p>
                    </div>
                  </div>
                  <div className="cohort-item">
                    <div className="cohort-avatar font-ops">OPS</div>
                    <div className="cohort-details">
                      <h4>Operations Cohort Q3</h4>
                      <p>8 members • 92% avg completion</p>
                    </div>
                  </div>
                  <div className="cohort-item">
                    <div className="cohort-avatar font-sales">SLS</div>
                    <div className="cohort-details">
                      <h4>Sales & Growth Cohort Q3</h4>
                      <p>15 members • 71% avg completion</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'onboarding':
        return (
          <div className="tab-content animate-fade-in">
            <h2>Onboarding Progress Detailed View</h2>
            <p className="tab-desc">Monitor employee tasks completion timelines, time-to-first-commit, and general milestone status.</p>
            <div className="data-panel glass-panel empty-state">
              <p>Onboarding metrics visualization will load once database schemas are populated.</p>
            </div>
          </div>
        );
      case 'tools':
        return (
          <div className="tab-content animate-fade-in">
            <h2>Tool Insights & License Utilization</h2>
            <p className="tab-desc">Analyze licensing costs and engagement for tools such as Slack, GitHub, Figma, and Jira.</p>
            <div className="data-panel glass-panel empty-state">
              <p>Tool activity charts are loading. FastAPI SQLite connection required.</p>
            </div>
          </div>
        );
      case 'support':
        return (
          <div className="tab-content animate-fade-in">
            <h2>Support Ticket Analytics</h2>
            <p className="tab-desc">Monitor time-to-resolution, ticket severity, and setup bottlenecks for new hire laptops and access cards.</p>
            <div className="data-panel glass-panel empty-state">
              <p>Support tickets dataset is currently disconnected.</p>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="dashboard-shell">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="main-content">
        <header className="content-header glass-panel">
          <div className="header-search">
            <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input type="text" placeholder="Search onboardees, tickets, tools..." />
          </div>

          <div className="header-actions">
            <button className="icon-btn" title="Notifications">
              <span className="dot-indicator" />
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
            </button>
            <button className="icon-btn" title="Help & Documentation">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01" />
              </svg>
            </button>
          </div>
        </header>

        <main className="content-body">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default DashboardShell;
