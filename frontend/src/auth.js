// Authentication utilities for frontend

const TOKEN_KEY = 'onboardiq_token';
const USER_KEY = 'onboardiq_user';

export const authService = {
  // Store authentication token
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  },

  // Get authentication token
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  // Remove authentication token
  removeToken() {
    localStorage.removeItem(TOKEN_KEY);
  },

  // Store user information
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  // Get user information
  getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  // Remove user information
  removeUser() {
    localStorage.removeItem(USER_KEY);
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  },

  // Logout
  logout() {
    this.removeToken();
    this.removeUser();
  },

  // Get authorization header
  getAuthHeader() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
};

// API wrapper with authentication
export const authenticatedFetch = async (url, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...authService.getAuthHeader(),
    ...options.headers
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  // Handle 401 Unauthorized - token expired or invalid
  if (response.status === 401) {
    authService.logout();
    window.location.href = '/login';
    throw new Error('Authentication required');
  }

  return response;
};
