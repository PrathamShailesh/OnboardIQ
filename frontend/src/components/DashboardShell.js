import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import EmployeeUpload from './EmployeeUpload';
import BottleneckInsights from './BottleneckInsights';
import BottleneckAlert from './BottleneckAlert';
import { API_BASE_URL } from '../api';
import { authService } from '../auth';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import './DashboardShell.css';

function DashboardShell({ onLogout }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardStats, setDashboardStats] = useState({
    activeOnboardees: '0',
    activeChange: 'No dataset loaded',
    onboardingSpeed: '—',
    speedChange: 'Upload data to calculate',
    toolAdoption: '—',
    toolChange: 'Upload data to calculate',
    openTickets: '0',
    ticketsChange: 'No dataset loaded',
    cohorts: [],
    milestones: {
      laptop: 0,
      training: 0,
      access: 0,
      email: 0,
      complete: 0,
      total: 0
    },
    toolEngagement: {
      slack_messages: 0,
      github_commits: 0,
      jira_resolved: 0
    },
    ticketCategories: {},
    stageDelays: {}
  });

  const [onboardingDetails, setOnboardingDetails] = useState([]);
  const [toolsDetails, setToolsDetails] = useState([]);
  const [supportDetails, setSupportDetails] = useState([]);

  const loadDashboardData = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/dashboard/summary`, {
        headers: authService.getAuthHeader()
      });
      if (res.ok) {
        const data = await res.json();
        setDashboardStats({
          activeOnboardees: String(data.active_onboardees),
          activeChange: data.total_employees ? `${data.total_employees} employees in the current dataset` : 'No dataset loaded',
          onboardingSpeed: data.avg_onboarding_speed,
          speedChange: 'Estimated from onboarding completion',
          toolAdoption: data.tool_adoption_rate,
          toolChange: 'Employees active in a tracked tool',
          openTickets: String(data.open_tickets),
          ticketsChange: 'Open or in-progress IT requests',
          cohorts: data.cohorts,
          milestones: data.onboarding_milestones,
          toolEngagement: data.tool_engagement,
          ticketCategories: data.ticket_categories,
          stageDelays: data.stage_delays || {}
        });
      } else {
        console.error('API error:', res.status, res.statusText);
        setDashboardStats(prev => ({
          ...prev,
          activeChange: 'Error loading data',
          onboardingSpeed: 'Error',
          toolAdoption: 'Error',
          openTickets: 'Error'
        }));
      }
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setDashboardStats(prev => ({
        ...prev,
        activeChange: 'Connection error',
        onboardingSpeed: 'Error',
        toolAdoption: 'Error',
        openTickets: 'Error'
      }));
    }
  };

  const loadDetailedData = async () => {
    try {
      const [onbRes, toolsRes, suppRes] = await Promise.all([
        fetch(`${API_BASE_URL}/onboarding/details`, {
          headers: authService.getAuthHeader()
        }),
        fetch(`${API_BASE_URL}/tools/details`, {
          headers: authService.getAuthHeader()
        }),
        fetch(`${API_BASE_URL}/support/details`, {
          headers: authService.getAuthHeader()
        })
      ]);

      if (onbRes.ok) {
        const onbData = await onbRes.json();
        setOnboardingDetails(onbData.data || []);
      } else {
        console.error('Onboarding details API error:', onbRes.status);
        setOnboardingDetails([]);
      }
      if (toolsRes.ok) {
        const toolsData = await toolsRes.json();
        setToolsDetails(toolsData.data || []);
      } else {
        console.error('Tools details API error:', toolsRes.status);
        setToolsDetails([]);
      }
      if (suppRes.ok) {
        const suppData = await suppRes.json();
        setSupportDetails(suppData.data || []);
      } else {
        console.error('Support details API error:', suppRes.status);
        setSupportDetails([]);
      }
    } catch (err) {
      console.error('Error loading detailed data:', err);
      setOnboardingDetails([]);
      setToolsDetails([]);
      setSupportDetails([]);
    }
  };

  useEffect(() => {
    loadDashboardData();
    loadDetailedData();
  }, [activeTab]);

  const stats = [
    {
      title: 'Active Onboardees',
      value: dashboardStats.activeOnboardees,
      change: dashboardStats.activeChange,
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
      value: dashboardStats.onboardingSpeed,
      change: dashboardStats.speedChange,
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
      value: dashboardStats.toolAdoption,
      change: dashboardStats.toolChange,
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
      value: dashboardStats.openTickets,
      change: dashboardStats.ticketsChange,
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
                <button className="primary-btn" onClick={loadDashboardData}>
                  <span>Refresh Metrics</span>
                  <svg className="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M23 4v6h-6M1 20v-6h6" />
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
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
                  <span className="badge">Current dataset</span>
                </div>
                
                <div className="progress-checklist-summary">
                  <div className="checklist-item-bar">
                    <div className="bar-labels">
                      <span>Laptops Issued</span>
                      <span>{dashboardStats.milestones.laptop} / {dashboardStats.milestones.total}</span>
                    </div>
                    <div className="bar-outer">
                      <div className="bar-inner accent-1" style={{ width: `${(dashboardStats.milestones.laptop / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                    </div>
                  </div>

                  <div className="checklist-item-bar">
                    <div className="bar-labels">
                      <span>Training Completed</span>
                      <span>{dashboardStats.milestones.training} / {dashboardStats.milestones.total}</span>
                    </div>
                    <div className="bar-outer">
                      <div className="bar-inner accent-2" style={{ width: `${(dashboardStats.milestones.training / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                    </div>
                  </div>

                  <div className="checklist-item-bar">
                    <div className="bar-labels">
                      <span>Security Access Granted</span>
                      <span>{dashboardStats.milestones.access} / {dashboardStats.milestones.total}</span>
                    </div>
                    <div className="bar-outer">
                      <div className="bar-inner accent-3" style={{ width: `${(dashboardStats.milestones.access / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                    </div>
                  </div>

                  <div className="checklist-item-bar">
                    <div className="bar-labels">
                      <span>Email Configured</span>
                      <span>{dashboardStats.milestones.email} / {dashboardStats.milestones.total}</span>
                    </div>
                    <div className="bar-outer">
                      <div className="bar-inner accent-4" style={{ width: `${(dashboardStats.milestones.email / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                    </div>
                  </div>
                </div>
              </div>

              <div className="data-panel side-panel glass-panel">
                <div className="panel-header">
                  <h3>Recent Cohorts</h3>
                </div>
                {dashboardStats.cohorts.length === 0 ? (
                  <div className="empty-state">
                    <p>No department/cohort data is available</p>
                    <p className="empty-state-sub">Upload a dataset with department information to view cohort analytics</p>
                  </div>
                ) : (
                  <div className="cohorts-list">
                    {dashboardStats.cohorts.map((cohort, idx) => (
                      <div key={idx} className="cohort-item">
                        <div className={`cohort-avatar font-${cohort.code.toLowerCase()}`}>{cohort.code}</div>
                        <div className="cohort-details">
                          <h4>{cohort.name}</h4>
                          <p>{cohort.members} members • {cohort.completion_rate}% completion</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <BottleneckAlert stageDelays={dashboardStats.stageDelays} />
            </div>
          </div>
        );
      case 'onboarding':
        return (
          <div className="tab-content animate-fade-in">
            <h2>Onboarding Progress Detailed View</h2>
            <p className="tab-desc">Monitor employee tasks completion timelines, equipment logs, and milestone status.</p>
            <div className="data-panel glass-panel detailed-milestones-grid">
              <div className="milestone-detail-card">
                <h3>Laptop Deployments</h3>
                <div className="value-label">{dashboardStats.milestones.laptop} / {dashboardStats.milestones.total} Assigned</div>
                <div className="progress-bar-detail">
                  <div className="progress-bar-fill fill-laptop" style={{ width: `${(dashboardStats.milestones.laptop / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                </div>
              </div>
              <div className="milestone-detail-card">
                <h3>Training Completions</h3>
                <div className="value-label">{dashboardStats.milestones.training} / {dashboardStats.milestones.total} Completed</div>
                <div className="progress-bar-detail">
                  <div className="progress-bar-fill fill-training" style={{ width: `${(dashboardStats.milestones.training / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                </div>
              </div>
              <div className="milestone-detail-card">
                <h3>Security Credentials</h3>
                <div className="value-label">{dashboardStats.milestones.access} / {dashboardStats.milestones.total} Granted</div>
                <div className="progress-bar-detail">
                  <div className="progress-bar-fill fill-access" style={{ width: `${(dashboardStats.milestones.access / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                </div>
              </div>
              <div className="milestone-detail-card">
                <h3>Corporate Email Setup</h3>
                <div className="value-label">{dashboardStats.milestones.email} / {dashboardStats.milestones.total} Synchronized</div>
                <div className="progress-bar-detail">
                  <div className="progress-bar-fill fill-email" style={{ width: `${(dashboardStats.milestones.email / Math.max(dashboardStats.milestones.total, 1)) * 100}%` }} />
                </div>
              </div>
            </div>

            <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
              <h3>Onboarding Progress by Department</h3>
              <div style={{ height: '300px', marginTop: '20px' }}>
                <BarChart width={800} height={300} data={dashboardStats.cohorts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="completion_rate" name="Completion Rate %" fill="#8884d8" />
                </BarChart>
              </div>
            </div>

            <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
              <h3>Employee Onboarding Status</h3>
              <div style={{ maxHeight: '400px', overflowY: 'auto', marginTop: '20px' }}>
                {onboardingDetails.length === 0 ? (
                  <div className="empty-state">
                    <p>No employee data available</p>
                    <p className="empty-state-sub">Upload a dataset to view onboarding progress</p>
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #ddd' }}>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Employee</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Department</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Laptop</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Training</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Access</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Email</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Complete</th>
                      </tr>
                    </thead>
                    <tbody>
                      {onboardingDetails.slice(0, 20).map((emp, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px' }}>{emp.employee_name}</td>
                          <td style={{ padding: '10px' }}>{emp.department}</td>
                          <td style={{ padding: '10px' }}>{emp.laptop_issued ? '✓' : '✗'}</td>
                          <td style={{ padding: '10px' }}>{emp.training_completed ? '✓' : '✗'}</td>
                          <td style={{ padding: '10px' }}>{emp.access_granted ? '✓' : '✗'}</td>
                          <td style={{ padding: '10px' }}>{emp.email_setup ? '✓' : '✗'}</td>
                          <td style={{ padding: '10px' }}>
                            <span style={{ 
                              padding: '4px 8px', 
                              borderRadius: '12px', 
                              backgroundColor: emp.onboarding_complete ? '#4caf50' : '#ff9800',
                              color: 'white',
                              fontSize: '12px'
                            }}>
                              {emp.onboarding_complete ? 'Complete' : 'In Progress'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              <BottleneckAlert stageDelays={dashboardStats.stageDelays} />
            </div>
          </div>
        );
      case 'tools':
        return (
          <div className="tab-content animate-fade-in">
            <h2>Tool Insights & License Utilization</h2>
            <p className="tab-desc">Analyze average engagement stats for development, collaboration, and project management tools.</p>
            <div className="data-panel glass-panel tool-utilization-metrics">
              <div className="tool-metric-card">
                <div className="tool-badge slack">Slack</div>
                <div className="metric-large">{dashboardStats.toolEngagement.slack_messages}</div>
                <div className="metric-label">Avg Messages / Month</div>
              </div>
              <div className="tool-metric-card">
                <div className="tool-badge github">GitHub</div>
                <div className="metric-large">{dashboardStats.toolEngagement.github_commits}</div>
                <div className="metric-label">Avg Commits / Month</div>
              </div>
              <div className="tool-metric-card">
                <div className="tool-badge jira">Jira</div>
                <div className="metric-large">{dashboardStats.toolEngagement.jira_resolved}</div>
                <div className="metric-label">Avg Tickets Resolved</div>
              </div>
            </div>

            <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
              <h3>Tool Engagement by Department</h3>
              <div style={{ height: '300px', marginTop: '20px' }}>
                <BarChart width={800} height={300} data={toolsDetails.slice(0, 10)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="employee_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="slack_messages" name="Slack Messages" fill="#4A154B" />
                  <Bar dataKey="github_commits" name="GitHub Commits" fill="#181717" />
                  <Bar dataKey="jira_tickets_resolved" name="Jira Tickets" fill="#0052CC" />
                </BarChart>
              </div>
            </div>

            <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
              <h3>Employee Tool Usage Details</h3>
              <div style={{ maxHeight: '400px', overflowY: 'auto', marginTop: '20px' }}>
                {toolsDetails.length === 0 ? (
                  <div className="empty-state">
                    <p>No tool usage data available</p>
                    <p className="empty-state-sub">Upload a dataset with tool engagement fields (slack_messages, github_commits, jira_tickets_resolved)</p>
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #ddd' }}>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Employee</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Department</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Slack Msgs</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>GitHub Commits</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Jira Tickets</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Slack Reactions</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>PR Reviews</th>
                      </tr>
                    </thead>
                    <tbody>
                      {toolsDetails.slice(0, 20).map((emp, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px' }}>{emp.employee_name}</td>
                          <td style={{ padding: '10px' }}>{emp.department}</td>
                          <td style={{ padding: '10px' }}>{emp.slack_messages}</td>
                          <td style={{ padding: '10px' }}>{emp.github_commits}</td>
                          <td style={{ padding: '10px' }}>{emp.jira_tickets_resolved}</td>
                          <td style={{ padding: '10px' }}>{emp.slack_reactions}</td>
                          <td style={{ padding: '10px' }}>{emp.github_prs_reviewed}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              <BottleneckAlert stageDelays={dashboardStats.stageDelays} />
            </div>
          </div>
        );
      case 'support':
        return (
          <div className="tab-content animate-fade-in">
            <h2>Support Ticket Analytics</h2>
            <p className="tab-desc">Monitor hardware, software, and credential ticket types submitted by active onboardees.</p>
            <div className="data-panel glass-panel support-analytics-grid">
              {Object.keys(dashboardStats.ticketCategories).length === 0 ? (
                <p>No active support tickets recorded.</p>
              ) : (
                <div className="categories-chart-bars">
                  {Object.entries(dashboardStats.ticketCategories).map(([cat, count], idx) => (
                    <div key={idx} className="category-item-bar">
                      <div className="bar-labels">
                        <span>{cat} Issues</span>
                        <span>{count} Open</span>
                      </div>
                      <div className="bar-outer">
                        <div className="bar-inner fill-support" style={{ width: `${Math.min((count / 15) * 100, 100)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
              <h3>Issue Type Distribution</h3>
              <div style={{ height: '300px', marginTop: '20px', display: 'flex', justifyContent: 'center' }}>
                <PieChart width={400} height={300}>
                  <Pie
                    data={Object.entries(dashboardStats.ticketCategories).map(([name, value]) => ({ name, value }))}
                    cx={200}
                    cy={150}
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {Object.entries(dashboardStats.ticketCategories).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'][index % 5]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </div>
            </div>

            <div className="data-panel glass-panel" style={{ marginTop: '20px' }}>
              <h3>Support Ticket Details</h3>
              <div style={{ maxHeight: '400px', overflowY: 'auto', marginTop: '20px' }}>
                {supportDetails.length === 0 ? (
                  <div className="empty-state">
                    <p>No support ticket data available</p>
                    <p className="empty-state-sub">Upload a dataset with support ticket fields (ticket_id, issue_type, status, priority)</p>
                  </div>
                ) : (
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #ddd' }}>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Ticket ID</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Employee</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Issue Type</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Priority</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
                        <th style={{ padding: '10px', textAlign: 'left' }}>Resolution Time (hrs)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {supportDetails.slice(0, 20).map((ticket, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px' }}>{ticket.ticket_id}</td>
                          <td style={{ padding: '10px' }}>{ticket.employee_name}</td>
                          <td style={{ padding: '10px' }}>{ticket.issue_type}</td>
                          <td style={{ padding: '10px' }}>
                            <span style={{ 
                              padding: '4px 8px', 
                              borderRadius: '12px', 
                              backgroundColor: ticket.priority === 'Critical' ? '#f44336' : 
                                               ticket.priority === 'High' ? '#ff9800' : 
                                               ticket.priority === 'Medium' ? '#2196f3' : '#4caf50',
                              color: 'white',
                              fontSize: '12px'
                            }}>
                              {ticket.priority}
                            </span>
                          </td>
                          <td style={{ padding: '10px' }}>
                            <span style={{ 
                              padding: '4px 8px', 
                              borderRadius: '12px', 
                              backgroundColor: ticket.status === 'Open' ? '#f44336' : 
                                               ticket.status === 'In Progress' ? '#ff9800' : 
                                               ticket.status === 'Resolved' ? '#4caf50' : '#9e9e9e',
                              color: 'white',
                              fontSize: '12px'
                            }}>
                              {ticket.status}
                            </span>
                          </td>
                          <td style={{ padding: '10px' }}>{ticket.resolution_time_hours || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              <BottleneckAlert stageDelays={dashboardStats.stageDelays} />
            </div>
          </div>
        );
      case 'bottlenecks':
        return <BottleneckInsights />;
      case 'upload':
        return <EmployeeUpload />;
      default:
        return null;
    }
  };

  return (
    <div className="dashboard-shell">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="main-content">
        <header className="content-header glass-panel">
          <div>
            <strong>Onboarding analytics</strong>
            <p className="header-subtitle">Monitor setup progress, tool adoption, and support trends.</p>
          </div>
          <button 
            onClick={onLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            Logout
          </button>
        </header>

        <main className="content-body">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default DashboardShell;





