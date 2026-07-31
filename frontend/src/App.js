import React, { useState, useEffect } from 'react';
import DashboardShell from './components/DashboardShell';
import Login from './components/Login';
import Signup from './components/Signup';
import { authService } from './auth';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState('login'); // 'login' or 'signup'

  useEffect(() => {
    // Check authentication status on mount
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setCurrentPage('dashboard');
  };

  const handleSignupSuccess = () => {
    setIsAuthenticated(true);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setCurrentPage('login');
  };

  if (!isAuthenticated) {
    if (currentPage === 'signup') {
      return <Signup onSignupSuccess={handleSignupSuccess} onSwitchToLogin={() => setCurrentPage('login')} />;
    }
    return <Login onLoginSuccess={handleLoginSuccess} onSwitchToSignup={() => setCurrentPage('signup')} />;
  }

  return (
    <div className="App">
      <DashboardShell onLogout={handleLogout} />
    </div>
  );
}

export default App;
