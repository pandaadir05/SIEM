// Basic API client using fetch

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Function to get the auth token (replace with your actual token storage mechanism)
const getAuthToken = () => {
  // Example: return localStorage.getItem('authToken');
  return "fake-jwt-token-admin"; // Placeholder - REMOVE THIS
};

const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      // Try to parse error message from backend
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        // Ignore if response is not JSON
      }
      const error = new Error(errorData?.error || `HTTP error! status: ${response.status}`);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    // Handle cases where response might be empty (e.g., 204 No Content)
    if (response.status === 204) {
        return null;
    }

    // Assume JSON response otherwise
    return await response.json();

  } catch (error) {
    console.error(`API call failed: ${options.method || 'GET'} ${url}`, error);
    // Re-throw the error so components can handle it
    throw error;
  }
};

// Define specific API functions
export const login = (username, password) => {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify({ user: username, password: password }),
    // Don't send auth header for login itself
    headers: { 'Authorization': undefined }
  });
};

export const getLogs = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/logs?${query}`);
};

export const getAlerts = (params = {}) => {
   const query = new URLSearchParams(params).toString();
  return request(`/alerts?${query}`);
};

export const getAlertById = (alertId) => {
  return request(`/alerts/${alertId}`);
};

// Add other API functions as needed (e.g., getRules, updateRule, etc.)
