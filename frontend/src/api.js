// Docker/WSL is already using port 8000 on this machine.  The OnboardIQ API
// therefore runs on 8001 by default.  Set REACT_APP_API_URL to override it.
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';
